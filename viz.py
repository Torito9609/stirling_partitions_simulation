import math
from typing import Dict, List, Tuple

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Polygon, Circle

# -------------------------------------------------------------------
# Visualización de particiones de {1..n}.
#
# Este módulo:
#   - Coloca los elementos 1..n en posiciones fijas sobre un círculo
#     (polígono regular).
#   - Para cada bloque de la partición dibuja una "nube" poligonal que
#     envuelve sus puntos (usando envolvente convexa o formas simples).
#   - Dibuja los puntos y sus etiquetas numéricas sobre un fondo negro.
#
# Se usa desde app.py para mostrar la partición seleccionada.
# -------------------------------------------------------------------


# ---------------------------------------------------------
# Posiciones base: puntos en círculo (polígono regular)
# ---------------------------------------------------------
def generar_posiciones(n: int) -> Dict[int, Tuple[float, float]]:
    """
    Genera posiciones (x, y) para los elementos 1..n sobre un círculo unitario.

    Parámetros:
        n : número de elementos del conjunto {1..n}.

    Devuelve:
        Diccionario {elemento: (x, y)} con coordenadas en R^2.

    Idea:
        Los puntos se distribuyen uniformemente en el ángulo, formando
        un polígono regular inscrito en un círculo de radio 1.
    """
    posiciones: Dict[int, Tuple[float, float]] = {}
    if n <= 0:
        return posiciones
    if n == 1:
        # Un solo elemento en el centro
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
    Calcula la envolvente convexa de un conjunto de puntos 2D.

    Implementa el algoritmo "monotone chain" (Andrew):
      - Ordena los puntos por coordenada x (y por y como desempate).
      - Construye la parte inferior (lower hull) y la parte superior
        (upper hull) usando producto cruzado para decidir si se debe
        eliminar el último punto.

    Parámetros:
        points : array de forma (m, 2) con m puntos en R^2.

    Devuelve:
        Array con los vértices de la envolvente convexa en orden.
    """
    if len(points) <= 1:
        return points

    # Ordenar por x, luego por y
    pts = np.array(sorted(points.tolist()))

    # Construir parte baja (lower hull)
    lower = []
    for p in pts:
        while len(lower) >= 2:
            x1, y1 = lower[-2]
            x2, y2 = lower[-1]
            x3, y3 = p
            # Producto cruzado para verificar giro (<= 0 significa giro no convexo)
            cross = (x2 - x1) * (y3 - y1) - (y2 - y1) * (x3 - x1)
            if cross <= 0:
                lower.pop()
            else:
                break
        lower.append(tuple(p))

    # Construir parte alta (upper hull)
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

    # Quitar el último de cada lista (está repetido en la unión)
    hull = np.array(lower[:-1] + upper[:-1])
    return hull


# ---------------------------------------------------------
# Dibujo de la partición con nubes poligonales
# ---------------------------------------------------------
def dibujar_particion(
    particion: List[List[int]],
    posiciones: Dict[int, Tuple[float, float]],
    ax=None,
):
    """
    Dibuja una partición de {1..n} como:

      - Puntos en las posiciones dadas por `posiciones`.
      - Una "nube" (región coloreada) que envuelve los puntos
        de cada bloque.

    Parámetros:
        particion : lista de bloques, cada bloque es una lista de enteros
                    (por ejemplo [[1,4], [2,3,5], [6]]).
        posiciones: diccionario {elemento: (x,y)} generado por generar_posiciones.

    Devuelve:
        fig : objeto Figure de matplotlib listo para mostrarse en Streamlit.
    """
    own_axis = ax is None
    if own_axis:
        # Canvas compacto + fondo negro
        fig, ax = plt.subplots(figsize=(5, 5))
    else:
        fig = ax.figure

    # Fondo del área de dibujo y de la figura
    ax.set_facecolor("black")
    fig.patch.set_facecolor("black")

    # Aquí podríamos personalizar un borde verde (spines), si se desea:
    # for spine in ax.spines.values():
    #     spine.set_edgecolor("green")
    #     spine.set_linewidth(2.0)

    if not particion:
        # Partición vacía: mensaje simple
        ax.text(
            0.5, 0.5, "Partición vacía",
            ha="center", va="center",
            fontsize=14, color="white"
        )
        ax.axis("off")
        return fig

    num_bloques = len(particion)

    for idx_bloque, bloque in enumerate(particion):
        # Color único por bloque — usamos el mapa de colores HSV
        color = plt.cm.hsv(idx_bloque / num_bloques)

        xs: List[float] = []
        ys: List[float] = []
        for elem in bloque:
            if elem in posiciones:
                x, y = posiciones[elem]
                xs.append(x)
                ys.append(y)

        if not xs:
            # Bloque vacío o elementos sin posición (no debería pasar)
            continue

        # Puntos de este bloque como array (m,2)
        pts = np.column_stack((xs, ys))

        # ===== NUBES (regiones coloreadas alrededor del bloque) =====
        if len(pts) == 1:
            # Un solo punto: lo rodeamos con un círculo ("burbuja")
            cx, cy = pts[0]
            burbuja = Circle(
                (cx, cy), radius=0.20,
                facecolor=color, alpha=0.30,
                edgecolor=color, linewidth=1.2, zorder=1
            )
            ax.add_patch(burbuja)

        elif len(pts) == 2:
            # Dos puntos: construimos un "cinturón" rectangular alrededor del segmento
            p1, p2 = pts
            vx, vy = p2 - p1
            norm = math.hypot(vx, vy) or 1.0
            # Vector normal unitario para dar espesor
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
            # Tres o más puntos: usamos la envolvente convexa como "nube"
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

        # Numeritos del bloque sobre cada punto
        for elem, (x, y) in zip(bloque, pts):
            ax.text(
                x, y, str(elem),
                ha="center", va="center",
                color="white",
                fontsize=10, fontweight="bold",
                zorder=3
            )

    # Opcionalmente se podrían ajustar límites y ejes aquí,
    # pero la app se encarga de encajarlo con use_container_width.
    if own_axis:
        ax.set_xlim(-1.3, 1.3)
        ax.set_ylim(-1.3, 1.3)
        ax.axis("off")
    return fig


def dibujar_particiones_en_grid(
    particiones: List[List[List[int]]],
    n: int | None = None,
    max_cols: int = 3,
    figsize_unit: float = 3.3,
):
    """Dibuja una lista de particiones en una rejilla de subplots.

    Parámetros:
        particiones: lista con todas las particiones (cada una es lista de bloques).
        n          : tamaño del conjunto {1..n}. Si es None se infiere del máximo
                     elemento encontrado en las particiones.
        max_cols   : número máximo de columnas en la rejilla.
        figsize_unit: tamaño base (en pulgadas) usado para calcular figsize
                      dinámico.

    Devuelve:
        fig : objeto Figure con todos los subplots dibujados.
    """
    if not particiones:
        fig, ax = plt.subplots(figsize=(4, 3))
        ax.text(0.5, 0.5, "No hay particiones para mostrar", ha="center", va="center")
        ax.axis("off")
        return fig

    if n is None:
        n = max(max(bloque) for particion in particiones for bloque in particion)

    posiciones = generar_posiciones(n)
    total = len(particiones)
    cols = max(1, min(max_cols, total))
    rows = math.ceil(total / cols)

    fig, axes = plt.subplots(
        rows,
        cols,
        figsize=(cols * figsize_unit, rows * figsize_unit),
    )
    fig.patch.set_facecolor("black")
    axes_flat = np.atleast_1d(axes).flatten()

    for ax in axes_flat:
        ax.set_xlim(-1.3, 1.3)
        ax.set_ylim(-1.3, 1.3)
        ax.axis("off")

    for particion, ax in zip(particiones, axes_flat):
        dibujar_particion(particion, posiciones, ax=ax)

    # Desactivar ejes sobrantes si la rejilla tiene más espacios que particiones
    for ax in axes_flat[total:]:
        ax.axis("off")

    fig.tight_layout()
    return fig
