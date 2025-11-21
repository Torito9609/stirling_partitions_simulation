import math
from typing import Dict, List, Tuple

import matplotlib.pyplot as plt
#import numpy as np


def generar_posiciones(n: int) -> Dict[int, Tuple[float, float]]:
    """
    Genera posiciones (x, y) para los elementos 1..n sobre un círculo unitario.
    Devuelve un diccionario {elemento: (x, y)}.
    """
    posiciones: Dict[int, Tuple[float, float]] = {}
    if n == 0:
        return posiciones
    if n == 1:
        posiciones[1] = (0.0, 0.0)
        return posiciones

    # Distribuimos los puntos uniformemente en el círculo
    radio = 1.0
    for i in range(1, n + 1):
        ang = 2 * math.pi * (i - 1) / n
        x = radio * math.cos(ang)
        y = radio * math.sin(ang)
        posiciones[i] = (x, y)
    return posiciones


def dibujar_particion(particion: List[List[int]], posiciones: Dict[int, Tuple[float, float]]):
    """
    Dibuja una partición de {1..n} donde:
      - particion es una lista de bloques, cada bloque es una lista de elementos (1-based)
      - posiciones es un dict {elemento: (x, y)} devuelto por generar_posiciones(n)
    Devuelve la figura de matplotlib.
    """
    # Creamos figura
    fig, ax = plt.subplots(figsize=(6, 6))

    if not particion:
        ax.text(0.5, 0.5, "Partición vacía", ha="center", va="center", fontsize=14)
        ax.axis("off")
        return fig

    # Colormap para los bloques
    cmap = plt.get_cmap("tab20")
    num_bloques = len(particion)

    # Dibujamos los puntos por bloque
    for idx_bloque, bloque in enumerate(particion):
        color = cmap(idx_bloque % cmap.N)

        xs = []
        ys = []
        for elem in bloque:
            if elem in posiciones:
                x, y = posiciones[elem]
                xs.append(x)
                ys.append(y)

        # Puntos del bloque
        ax.scatter(xs, ys, s=200, color=color, alpha=0.8, edgecolors="black")

        # Etiquetas de cada punto
        for elem in bloque:
            if elem in posiciones:
                x, y = posiciones[elem]
                ax.text(x, y, str(elem), ha="center", va="center", color="white", fontsize=10, fontweight="bold")

    # Opcional: dibujar el círculo base
    circle = plt.Circle((0, 0), 1.0, color="lightgray", fill=False, linestyle="--", alpha=0.5)
    ax.add_artist(circle)

    ax.set_aspect("equal", "box")
    ax.axis("off")
    ax.set_title("Bloques de la partición", fontsize=14)

    return fig
