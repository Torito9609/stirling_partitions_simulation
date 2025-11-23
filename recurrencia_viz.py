from dataclasses import dataclass
from typing import Optional, Dict, Tuple

import matplotlib.pyplot as plt


# ---------------------------------------------------
# Cálculo de S(n,k) con memoización (números de Stirling 2ª especie)
# ---------------------------------------------------
_stirling_cache: Dict[Tuple[int, int], int] = {}


def stirling_s2(n: int, k: int) -> int:
    """Calcula S(n,k) usando la recurrencia S(n,k) = k S(n-1,k) + S(n-1,k-1)."""
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
    Determina si (n,k) corresponde a un caso base de la recurrencia de Stirling S(n,k).
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
    Cada llamada recursiva se modela como un nodo.
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
    Asigna posiciones x,y a cada nodo usando un recorrido en orden
    para repartir los nodos en el eje horizontal.
    """
    current_x = [0]  # usamos lista mutable para capturar el contador

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
    Asigna índices 0,1,2,... a los nodos en preorden.
    Devuelve la cantidad total de nodos.
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
    """Busca en el árbol el nodo con índice idx."""
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
    Reconstruye el árbol de llamadas de S(n,k), enumera los nodos,
    y devuelve información sobre el nodo con índice = step.
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
    if node is None:
        return

    for child in (node.left, node.right):
        if child is not None:
            # Solo dibujar la arista si ambos nodos están dentro del paso de animación
            if max_step is None or (node.idx <= max_step and child.idx <= max_step):
                # Flecha desde el padre (node) hacia el hijo (child)
                ax.annotate(
                    "",
                    xy=(child.x, child.y),
                    xytext=(node.x, node.y),
                    arrowprops=dict(
                        arrowstyle="->",
                        color="white",
                        lw=1.0,
                        alpha=0.7,
                        shrinkA=10,  # para que no toque el centro del nodo
                        shrinkB=10,
                    ),
                    zorder=1,
                )

            _draw_edges(ax, child, max_step)


def _draw_nodes(ax, node: Optional[RecNode], max_step: Optional[int]):
    if node is None:
        return

    # Respetar la animación: solo dibujar nodos hasta max_step
    if max_step is None or node.idx <= max_step:
        val = stirling_s2(node.n, node.k)
        label = f"S({node.n},{node.k}) = {val}"

        # ¿Es caso base?
        base = es_caso_base(node.n, node.k)

        # Colores según tipo de nodo
        if base:
            # Caso base: por ejemplo, naranja
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
            color="lime",       # verde terminal, como pediste
            fontsize=7,         # un poco más pequeño
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
    Dibuja el árbol de recurrencia para S(n,k):
      S(n,k) = k S(n-1,k) + S(n-1,k-1)

    Para evitar árboles gigantes, limitamos visualmente a n <= 8.
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

    # Construir árbol de llamadas
    root = _build_call_tree(n, k, depth=0)
    _assign_positions(root, y_step=-1.3)
    total_nodes = _enumerate_nodes(root)

    # Recortar step si está fuera de rango
    if step is not None:
        step = max(0, min(step, total_nodes - 1))

    _draw_edges(ax, root, max_step=step)
    _draw_nodes(ax, root, max_step=step)

    # Ajustar márgenes para que el árbol entre bien
    xs = []
    ys = []

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
    
    plt.tight_layout()

    return fig, total_nodes
