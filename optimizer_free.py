from __future__ import annotations

import numpy as np

from evaluator import evaluate_layout
from layouts import seed_free_layout
from models import DesignLimits, LoadCase, Solution


def optimise_free(
    load_cases: list[LoadCase],
    limits: DesignLimits,
    min_piles: int,
    max_piles: int,
    population_size: int = 60,
    generations: int = 80,
    mutation_scale: float = 0.35,
    regularity_preference: float = 0.25,
    random_seed: int = 42,
    progress_callback=None,
) -> list[Solution]:
    """Genetic search in which each pile has independent x and y coordinates."""
    rng = np.random.default_rng(random_seed)
    all_best: list[Solution] = []
    pile_counts = list(range(min_piles, max_piles + 1))

    for count_index, n_piles in enumerate(pile_counts):
        population = _initial_population(n_piles, limits, population_size, rng)
        if not population:
            continue

        for generation in range(generations):
            evaluated = [
                evaluate_layout(
                    coordinates,
                    load_cases,
                    limits,
                    mode="Free pile locations",
                    regularity_weight=regularity_preference,
                )
                for coordinates in population
            ]
            evaluated.sort(key=lambda solution: solution.score)

            elite_count = max(4, population_size // 5)
            elites = evaluated[:elite_count]
            population = [np.asarray(solution.coordinates, dtype=float) for solution in elites]

            while len(population) < population_size:
                parent = np.asarray(elites[rng.integers(len(elites))].coordinates, dtype=float)
                child = _mutate(parent, limits, mutation_scale, rng)
                child = _repair_spacing(child, limits, rng)
                population.append(child)

            if progress_callback:
                completed = (count_index * generations + generation + 1) / (len(pile_counts) * generations)
                progress_callback(completed)

        final = [
            evaluate_layout(
                coordinates,
                load_cases,
                limits,
                mode="Free pile locations",
                regularity_weight=regularity_preference,
            )
            for coordinates in population
        ]
        all_best.extend(sorted(final, key=lambda solution: solution.score)[:8])

    feasible = [solution for solution in all_best if solution.feasible]
    return _deduplicate(sorted(feasible, key=lambda solution: solution.score))


def _initial_population(n_piles, limits, population_size, rng):
    population = []
    attempts = 0
    while len(population) < population_size and attempts < population_size * 30:
        candidate = seed_free_layout(
            n_piles,
            limits.max_width,
            limits.max_depth,
            limits.min_spacing,
            rng,
        )
        attempts += 1
        if candidate is not None:
            population.append(candidate)
    return population


def _mutate(parent, limits, mutation_scale, rng):
    child = parent.copy()
    n_moves = max(1, int(np.ceil(len(child) * rng.uniform(0.10, 0.35))))
    indices = rng.choice(len(child), size=n_moves, replace=False)
    sigma = mutation_scale * limits.min_spacing
    child[indices] += rng.normal(0.0, sigma, size=(n_moves, 2))

    # Occasional relocation prevents the search becoming trapped around its seed.
    if rng.random() < 0.12:
        index = rng.integers(len(child))
        child[index] = [
            rng.uniform(-limits.max_width / 2.0, limits.max_width / 2.0),
            rng.uniform(-limits.max_depth / 2.0, limits.max_depth / 2.0),
        ]

    child[:, 0] = np.clip(child[:, 0], -limits.max_width / 2.0, limits.max_width / 2.0)
    child[:, 1] = np.clip(child[:, 1], -limits.max_depth / 2.0, limits.max_depth / 2.0)
    return child


def _repair_spacing(points, limits, rng, iterations=50):
    repaired = points.copy()
    for _ in range(iterations):
        moved = False
        for i in range(len(repaired)):
            for j in range(i + 1, len(repaired)):
                delta = repaired[j] - repaired[i]
                distance = np.linalg.norm(delta)
                if distance < limits.min_spacing:
                    if distance < 1.0e-9:
                        direction = rng.normal(size=2)
                        direction /= np.linalg.norm(direction)
                    else:
                        direction = delta / distance
                    shift = 0.5 * (limits.min_spacing - distance + 1.0e-4) * direction
                    repaired[i] -= shift
                    repaired[j] += shift
                    moved = True
        repaired[:, 0] = np.clip(repaired[:, 0], -limits.max_width / 2.0, limits.max_width / 2.0)
        repaired[:, 1] = np.clip(repaired[:, 1], -limits.max_depth / 2.0, limits.max_depth / 2.0)
        if not moved:
            break
    return repaired


def _deduplicate(solutions: list[Solution], keep: int = 60) -> list[Solution]:
    unique: list[Solution] = []
    signatures = set()
    for solution in solutions:
        signature = tuple(sorted((round(x, 2), round(y, 2)) for x, y in solution.coordinates))
        if signature not in signatures:
            signatures.add(signature)
            unique.append(solution)
        if len(unique) >= keep:
            break
    return unique
