import matplotlib.pyplot as plt


def dibujar_arbol_recurrencia(n: int, k: int):
    """
    Esqueleto: por ahora solo muestra un placeholder.
    Luego aquí dibujaremos el árbol de recurrencia S(n, k).
    """
    fig, ax = plt.subplots(figsize=(4, 4))
    ax.set_facecolor("black")
    fig.patch.set_facecolor("black")

    mensaje = f"Árbol de recurrencia\nS({n}, {k})"
    ax.text(
        0.5, 0.5, mensaje,
        ha="center", va="center",
        color="white", fontsize=14, fontweight="bold"
    )

    ax.axis("off")
    plt.tight_layout()
    return fig
