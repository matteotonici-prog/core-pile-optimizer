def rectangular_layout(nx, ny, spacing):

    piles = []

    for i in range(nx):
        for j in range(ny):

            piles.append(
                (i * spacing, j * spacing)
            )

    return piles


def perimeter_layout(nx, ny, spacing):

    piles = []

    for i in range(nx):
        for j in range(ny):

            if (
                i == 0
                or i == nx - 1
                or j == 0
                or j == ny - 1
            ):
                piles.append(
                    (i * spacing, j * spacing)
                )

    return piles
