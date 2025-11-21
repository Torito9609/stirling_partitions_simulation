import math
from typing import Dict, List, Tuple

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Polygon, Circle


# ---------------------------------------------------------
# Posiciones base: puntos en círculo (polígono regular)
# ---------------------------------------------------------
def generar_posiciones(n: int) -> Dict[int, Tuple[float, float]]:
    """
    Genera posiciones (x, y) para los elementos 1..n sobre un círculo unitario.
    Devuelve un diccionario {elemento: (x, y)}.
    """
    posiciones: Dict[int, Tuple[float, float]] = {}
    if n <= 0:
        return posiciones
    if n == 1:
        posiciones[1] = (0.0, 0.0)
        return posiciones

    radio = 1.0
    for i in range(1, n + 1):
        # Distribuimos los puntos uniformemente formando un polígono regular
        ang = 2 * math.pi * (i - 1) / n
        x = radio * math.cos(ang)
        y = radio * math.sin(ang)
        posiciones[i] = (x, y)
    return posiciones


# ---------------------------------------------------------
# Convex hull (envolvente convexa) para las nubes
# ---------------------------------------------------------
def _convex_hull(points: np.ndarray) -> np.ndarray:
    """
    Devuelve la envolvente convexa de un conjunto de puntos 2D
    usando el algoritmo de "monotone chain" (Andrew).
    points: array de forma (m, 2)
    """
    if len(points) <= 1:
        return points

    # Ordenar por x, luego por y
    pts = np.array(sorted(points.tolist()))

    # Construir parte baja
    lower = []
    for p in pts:
        while len(lower) >= 2:
            x1, y1 = lower[-2]
            x2, y2 = lower[-1]
            x3, y3 = p
            # Producto cruzado para verificar giro
            cross = (x2 - x1) * (y3 - y1) - (y2 - y1) * (x3 - x1)
            if cross <= 0:
                lower.pop()
            else:
                break
        lower.append(tuple(p))

    # Construir parte alta
    upper = []
    for p in reversed(pts):
        while len(upper) >= 2:
            x1, y1 = upper[-2]
            x2, y2 = upper[-1]
            x3, y3 = p
            cross = (x2 - x1) * (y3 - y1) - (y2 - y1) * (x3 - x1)
            if cross <= 0:
                upper.pop()
            else:
                break
        upper.append(tuple(p))

    # Quitar el último de cada lista (está repetido)
    hull = np.array(lower[:-1] + upper[:-1])
    return hull


# ---------------------------------------------------------
# Dibujo de la partición con nubes poligonales
# ---------------------------------------------------------
def dibujar_particion(particion: List[List[int]], posiciones: Dict[int, Tuple[float, float]]):
    # Canvas compacto + fondo negro
    fig, ax = plt.subplots(figsize=(5, 5))
    
    # Fondo del área de dibujo
    ax.set_facecolor("black")
    fig.patch.set_facecolor("black")

    # Borde verde alrededor del canvas
    # (usamos spine para que se vea siempre cuadrado)
    

    if not particion:
        ax.text(0.5, 0.5, "Partición vacía", ha="center", va="center", fontsize=14, color="white")
        ax.axis("off")
        return fig

    num_bloques = len(particion)

    for idx_bloque, bloque in enumerate(particion):

        # Color único por bloque — modo HSV
        color = plt.cm.hsv(idx_bloque / num_bloques)

        xs = []
        ys = []
        for elem in bloque:
            if elem in posiciones:
                x, y = posiciones[elem]
                xs.append(x)
                ys.append(y)

        if not xs:
            continue

        pts = np.column_stack((xs, ys))

        # ===== NUBES =====
        if len(pts) == 1:
            cx, cy = pts[0]
            burbuja = Circle(
                (cx, cy), radius=0.20,
                facecolor=color, alpha=0.30,
                edgecolor=color, linewidth=1.2, zorder=1
            )
            ax.add_patch(burbuja)

        elif len(pts) == 2:
            p1, p2 = pts
            vx, vy = p2 - p1
            norm = math.hypot(vx, vy) or 1.0
            nx, ny = -vy / norm, vx / norm
            ancho = 0.15
            poly_pts = np.array([
                p1 + ancho * np.array([nx, ny]),
                p2 + ancho * np.array([nx, ny]),
                p2 - ancho * np.array([nx, ny]),
                p1 - ancho * np.array([nx, ny]),
            ])
            burbuja = Polygon(
                poly_pts, closed=True,
                facecolor=color, alpha=0.30,
                edgecolor=color, linewidth=1.2, zorder=1
            )
            ax.add_patch(burbuja)

        else:
            hull = _convex_hull(pts)
            burbuja = Polygon(
                hull, closed=True,
                facecolor=color, alpha=0.30,
                edgecolor=color, linewidth=1.2, zorder=1
            )
            ax.add_patch(burbuja)

        # ===== PUNTOS =====
        ax.scatter(
            pts[:, 0], pts[:, 1],
            s=150,
            color=color,
            alpha=1.0,
            edgecolors="white",
            linewidth=1.2,
            zorder=2
        )

        # Numeritos del bloque — ahora blancos
        for elem, (x, y) in zip(bloque, pts):
            ax.text(
                x, y, str(elem),
                ha="center", va="center",
                color="white",
                fontsize=10, fontweight="bold",
                zorder=3
            )

    return fig


