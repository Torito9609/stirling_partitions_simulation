from dataclasses import dataclass
from typing import Optional, Dict, Tuple
from matplotlib.lines import Line2D

import matplotlib.pyplot as plt

# -------------------------------------------------------------------
# Visualización del árbol de recurrencia para los números de Stirling
# de segunda especie S(n, k).
#
# Este módulo:
#   - Calcula S(n, k) con memoización.
#   - Construye el árbol de llamadas recursivas de la relación:
#         S(n,k) = k·S(n-1,k) + S(n-1,k-1)
#   - Asigna posiciones (x, y) a cada nodo para dibujarlo.
#   - Dibuja nodos, aristas y una leyenda con la convención:
#         flecha izquierda  → término k·S(n-1,k)
#         flecha derecha    → término S(n-1,k-1)
# -------------------------------------------------------------------


# ---------------------------------------------------
# Cálculo de S(n,k) con memoización (Stirling 2ª especie)
# ---------------------------------------------------
_stirling_cache: Dict[Tuple[int, int], int] = {}


def stirling_s2(n: int, k: int) -> int:
    """
    Calcula el número de Stirling de segunda especie S(n,k) usando la recurrencia:

        S(n,k) = k·S(n-1,k) + S(n-1,k-1)

    con los casos base estándar:

        S(0,0) = 1
        S(n,0) = 0 para n > 0
        S(n,n) = 1
        S(n,k) = 0 si k < 0 o k > n

    Se usa un diccionario global _stirling_cache para memoización.
    """
    if (n, k) in _stirling_cache:
        return _stirling_cache[(n, k)]

    # Casos base estándar
    if n == 0 and k == 0:
        val = 1
    elif n > 0 and k == 0:
        val = 0
    elif n == k:
        val = 1
    elif k < 0 or k > n:
        val = 0
    else:
        val = k * stirling_s2(n - 1, k) + stirling_s2(n - 1, k - 1)

    _stirling_cache[(n, k)] = val
    return val


def es_caso_base(n: int, k: int) -> bool:
    """
    Indica si (n, k) corresponde a uno de los casos base de S(n, k).
    """
    if n == 0 and k == 0:
        return True
    if n > 0 and k == 0:
        return True
    if n == k:
        return True
    if k < 0 or k > n:
        return True
    return False


# ---------------------------------------------------
# Estructura de nodo para el árbol de llamadas
# ---------------------------------------------------
@dataclass
class RecNode:
    """
    Nodo del árbol de llamadas de la recurrencia S(n,k).

    Atributos:
        n, k   : parámetros de la llamada S(n, k).
        depth  : profundidad en el árbol (raíz tiene depth = 0).
        left   : hijo izquierdo (S(n-1, k)).
        right  : hijo derecho (S(n-1, k-1)).
        x, y   : posición asignada para dibujar el nodo.
        idx    : índice asignado en preorden (para animación).
    """
    n: int
    k: int
    depth: int
    left: Optional["RecNode"] = None
    right: Optional["RecNode"] = None
    x: float = 0.0
    y: float = 0.0
    idx: int = -1


def _build_call_tree(n: int, k: int, depth: int = 0) -> RecNode:
    """
    Construye el árbol de llamadas recursivas para S(n,k).

    Cada llamada S(n,k) es un nodo:
      - Si (n,k) es caso base, se crea un nodo sin hijos.
      - Si no, se crean recursivamente los hijos:
            left  = S(n-1, k)
            right = S(n-1, k-1)
    """
    node = RecNode(n=n, k=k, depth=depth)

    # Casos base: detenemos la recursión
    if es_caso_base(n, k):
        return node

    # Paso recursivo: S(n,k) -> S(n-1,k) y S(n-1,k-1)
    node.left = _build_call_tree(n - 1, k, depth + 1)
    node.right = _build_call_tree(n - 1, k - 1, depth + 1)
    return node


# ---------------------------------------------------
# Asignación de posiciones (x,y) para dibujar el árbol
# ---------------------------------------------------
def _assign_positions(root: RecNode, y_step: float = -1.2) -> None:
    """
    Asigna posiciones (x, y) a cada nodo del árbol.

    Estrategia:
      - Se hace un recorrido en orden (inorder) para repartir
        los nodos en el eje horizontal (x).
      - La coordenada y depende de la profundidad (depth * y_step).
    """
    current_x = [0]  # usamos lista mutable para que el closure pueda modificarla

    def inorder(node: Optional[RecNode], depth: int = 0):
        if node is None:
            return

        inorder(node.left, depth + 1)
        node.x = current_x[0]
        node.y = depth * y_step
        current_x[0] += 1
        inorder(node.right, depth + 1)

    inorder(root, 0)


def _enumerate_nodes(root: RecNode) -> int:
    """
    Asigna índices 0, 1, 2, ... a los nodos en preorden.

    Estos índices se usan para:
      - Controlar hasta qué nodo se dibuja en la animación.
      - Asegurar un orden consistente de aparición.

    Devuelve:
        El número total de nodos del árbol.
    """
    counter = [0]

    def dfs(node: Optional[RecNode]):
        if node is None:
            return
        node.idx = counter[0]
        counter[0] += 1
        dfs(node.left)
        dfs(node.right)

    dfs(root)
    return counter[0]


def _find_node_by_idx(root: RecNode, idx: int) -> Optional[RecNode]:
    """
    Busca en el árbol el nodo cuyo índice (idx) coincide con el valor dado.
    """
    result = None

    def dfs(node: Optional[RecNode]):
        nonlocal result
        if node is None or result is not None:
            return
        if node.idx == idx:
            result = node
            return
        dfs(node.left)
        dfs(node.right)

    dfs(root)
    return result


def get_node_info(n: int, k: int, step: int) -> Dict:
    """
    Reconstruye el árbol de llamadas de S(n,k), lo enumera
    y devuelve información sobre el nodo con índice = step.

    Actualmente esta función no se está usando en la app,
    pero se deja para futuras extensiones (por ejemplo,
    paneles explicativos de la recurrencia).
    """
    info = {
        "n": None,
        "k": None,
        "val": None,
        "is_base": None,
        "left": None,   # dict con n,k,val o None
        "right": None,  # dict con n,k,val o None
        "total_nodes": 0,
    }

    # Validación básica similar a la de dibujar_arbol_recurrencia
    if n < 0 or k < 0 or k > n:
        return info

    root = _build_call_tree(n, k, depth=0)
    _assign_positions(root, y_step=-1.3)
    total_nodes = _enumerate_nodes(root)
    info["total_nodes"] = total_nodes

    if total_nodes == 0:
        return info

    # Asegurar que step esté en rango
    step = max(0, min(step, total_nodes - 1))
    node = _find_node_by_idx(root, step)
    if node is None:
        return info

    # Nodo activo
    n0, k0 = node.n, node.k
    v0 = stirling_s2(n0, k0)
    base = es_caso_base(n0, k0)
    info["n"] = n0
    info["k"] = k0
    info["val"] = v0
    info["is_base"] = base

    # Hijo izquierdo
    if node.left is not None:
        nl, kl = node.left.n, node.left.k
        vl = stirling_s2(nl, kl)
        info["left"] = {"n": nl, "k": kl, "val": vl}

    # Hijo derecho
    if node.right is not None:
        nr, kr = node.right.n, node.right.k
        vr = stirling_s2(nr, kr)
        info["right"] = {"n": nr, "k": kr, "val": vr}

    return info


# ---------------------------------------------------
# Dibujo del árbol
# ---------------------------------------------------
def _draw_edges(ax, node: Optional[RecNode], max_step: Optional[int]):
    """
    Dibuja las aristas (flechas) del árbol.

    Convención visual:
      - Flecha izquierda  (hijo = node.left)  en morado oscuro (#8a2be2)
      - Flecha derecha    (hijo = node.right) en amarillo (#ffd700)

    max_step controla la animación: solo se dibujan aristas
    cuyos nodos origen y destino tienen idx <= max_step.
    """
    if node is None:
        return

    children = [("left", node.left), ("right", node.right)]

    for side, child in children:
        if child is not None:

            # Solo dibujar si ambos nodos están dentro del paso de animación
            if max_step is None or (node.idx <= max_step and child.idx <= max_step):

                # Colores según convención
                if side == "left":
                    arrow_color = "#8a2be2"   # morado oscuro → k·S(n-1,k)
                else:
                    arrow_color = "#ffd700"   # amarillo → S(n-1,k-1)

                ax.annotate(
                    "",
                    xy=(child.x, child.y),
                    xytext=(node.x, node.y),
                    arrowprops=dict(
                        arrowstyle="->",
                        color=arrow_color,
                        lw=1.2,
                        alpha=0.9,
                        shrinkA=10,
                        shrinkB=10,
                    ),
                    zorder=1,
                )

            _draw_edges(ax, child, max_step)


def _draw_nodes(ax, node: Optional[RecNode], max_step: Optional[int]):
    """
    Dibuja los nodos del árbol (círculos y etiquetas).

    Convención:
      - Nodos caso base: color naranja, etiqueta S(n,k) = valor.
      - Nodos internos: color azul, etiqueta S(n,k) (sin mostrar el valor).
    """
    if node is None:
        return

    # Respetar la animación: solo dibujar nodos hasta max_step
    if max_step is None or node.idx <= max_step:
        val = stirling_s2(node.n, node.k)
        base = es_caso_base(node.n, node.k)

        # Etiqueta diferenciada:
        if base:
            # Los casos base sí muestran su valor
            label = f"S({node.n},{node.k}) = {val}"
        else:
            # Los nodos internos NO muestran el resultado
            label = f"S({node.n},{node.k})"

        # Colores según tipo de nodo
        if base:
            # Caso base: naranja
            color_nodo = "#ff7f0e"
        else:
            # Nodo recursivo normal: azul
            color_nodo = "#1f77b4"

        # ----- Nodo (círculo) -----
        ax.scatter(
            [node.x],
            [node.y],
            s=200,
            color=color_nodo,
            edgecolors="white",
            linewidths=1.2,
            zorder=2,
        )

        # ----- Etiqueta (debajo del nodo) -----
        ax.text(
            node.x,
            node.y - 0.25,      # un poco debajo para no tapar el nodo
            label,
            ha="center",
            va="top",
            color="lime",       # verde tipo "terminal"
            fontsize=7,
            fontweight="bold",
            zorder=3,
        )

    # Recorrer hijos
    _draw_nodes(ax, node.left, max_step)
    _draw_nodes(ax, node.right, max_step)


# ---------------------------------------------------
# Función pública llamada desde app.py
# ---------------------------------------------------
def dibujar_arbol_recurrencia(n: int, k: int, step: Optional[int] = None):
    """
    Dibuja el árbol de recurrencia para S(n,k) y devuelve:

        fig, total_nodes

    donde:
      - fig         : figura de matplotlib para mostrar en Streamlit.
      - total_nodes : número total de nodos del árbol.

    Parámetros:
        n, k : definen la llamada S(n,k) en la raíz.
        step : índice máximo de nodo a dibujar (para animación). Si es None,
               se dibuja el árbol completo.

    Nota:
        Para evitar árboles gigantes en pantalla, se limita a n <= 8.
    """
    fig, ax = plt.subplots(figsize=(6.5, 4.5))
    ax.set_facecolor("black")
    fig.patch.set_facecolor("black")

    # Validación básica
    if n < 0 or k < 0 or k > n:
        ax.text(
            0.5,
            0.5,
            f"Parámetros inválidos:\nS({n},{k})",
            ha="center",
            va="center",
            color="white",
            fontsize=14,
        )
        ax.axis("off")
        plt.tight_layout()
        return fig

    if n > 8:
        ax.text(
            0.5,
            0.5,
            f"n = {n} es demasiado grande\npara dibujar el árbol de recurrencia.\nUsa n ≤ 8.",
            ha="center",
            va="center",
            color="white",
            fontsize=12,
        )
        ax.axis("off")
        plt.tight_layout()
        return fig

    # Construir árbol de llamadas y preparar posiciones/índices
    root = _build_call_tree(n, k, depth=0)
    _assign_positions(root, y_step=-1.3)
    total_nodes = _enumerate_nodes(root)

    # Recortar step si está fuera de rango
    if step is not None:
        step = max(0, min(step, total_nodes - 1))

    _draw_edges(ax, root, max_step=step)
    _draw_nodes(ax, root, max_step=step)

    # Ajustar márgenes para que el árbol entre bien
    xs: list[float] = []
    ys: list[float] = []

    def collect(node: Optional[RecNode]):
        if node is None:
            return
        xs.append(node.x)
        ys.append(node.y)
        collect(node.left)
        collect(node.right)

    collect(root)

    if xs and ys:
        margen_x = 1.0
        margen_y = 0.8
        ax.set_xlim(min(xs) - margen_x, max(xs) + margen_x)
        ax.set_ylim(min(ys) - margen_y, max(ys) + margen_y)

    ax.set_title(f"Árbol de recurrencia para S({n},{k})", color="white", fontsize=12)

    # Leyenda con la convención de colores de las flechas
    legend_elements = [
        Line2D(
            [0], [0], color="#8a2be2", lw=2,
            label="Flecha izquierda → k·S(n−1,k)"
        ),
        Line2D(
            [0], [0], color="#ffd700", lw=2,
            label="Flecha derecha → S(n−1,k−1)"
        ),
    ]

    fig.legend(
        handles=legend_elements,
        loc="upper center",
        bbox_to_anchor=(0.5, 1.02),   # por encima del título, fuera del área del plot
        ncol=2,
        facecolor="black",
        edgecolor="white",
        labelcolor="white",
        fontsize=8,
    )

    plt.tight_layout()

    return fig, total_nodes
