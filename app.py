import streamlit as st
#import matplotlib.pyplot as plt

import rgs
import viz


# ------------------------------------------
# Inicialización de estado
# ------------------------------------------
def init_session_state():
    if "partitions" not in st.session_state:
        st.session_state["partitions"] = []
    if "current_index" not in st.session_state:
        st.session_state["current_index"] = 0
    if "current_n" not in st.session_state:
        st.session_state["current_n"] = None
    if "current_k" not in st.session_state:
        st.session_state["current_k"] = None


# ------------------------------------------
# Lógica para generar particiones
# ------------------------------------------
def generar_particiones(n: int, modo: str, k: int | None = None):
    if modo == "Todas las particiones de {1..n}":
        partes = list(rgs.rgs_all(n, yield_blocks=True))
    elif modo == "Exactamente k bloques":
        if k is None:
            partes = []
        else:
            partes = list(rgs.rgs_exactly(n, k, yield_blocks=True))
    else:
        partes = []

    st.session_state["partitions"] = partes
    st.session_state["current_index"] = 0
    st.session_state["current_n"] = n
    st.session_state["current_k"] = k


# ------------------------------------------
# Navegación entre particiones
# ------------------------------------------
def avanzar():
    if st.session_state["partitions"]:
        if st.session_state["current_index"] < len(st.session_state["partitions"]) - 1:
            st.session_state["current_index"] += 1


def retroceder():
    if st.session_state["partitions"]:
        if st.session_state["current_index"] > 0:
            st.session_state["current_index"] -= 1


# ------------------------------------------
# App principal
# ------------------------------------------
def main():
    st.set_page_config(page_title="Simulación de Particiones", layout="wide")
    init_session_state()

    # ---------------- Sidebar ----------------
    with st.sidebar:
        st.title("Controles")

        n = st.number_input("Tamaño del conjunto n", min_value=0, max_value=12, value=5, step=1)

        modo = st.selectbox(
            "Modo de enumeración",
            ["Todas las particiones de {1..n}", "Exactamente k bloques"],
        )

        k = None
        if modo == "Exactamente k bloques":
            # Solo tiene sentido k entre 0 y n
            k = st.number_input("Número de bloques k", min_value=0, max_value=int(n), value=min(2, int(n)), step=1)

        st.markdown("---")

        if st.button("Generar particiones"):
            generar_particiones(int(n), modo, int(k) if k is not None else None)

        st.markdown("### Navegación")
        col_a, col_b = st.columns(2)
        with col_a:
            if st.button("⬅️ Anterior"):
                retroceder()
        with col_b:
            if st.button("Siguiente ➡️"):
                avanzar()

    # ---------------- Contenido principal ----------------
    st.title("Simulación de particiones de un conjunto")

    if not st.session_state["partitions"]:
        st.info("Genera las particiones desde la barra lateral para comenzar.")
        return

    partitions = st.session_state["partitions"]
    idx = st.session_state["current_index"]
    n_actual = st.session_state["current_n"]
    k_actual = st.session_state["current_k"]

    particion_actual = partitions[idx]  # lista de bloques, p.ej. [[1,4], [2,3,5], [6]]

    # Información textual
    col_info, col_fig = st.columns([1, 2])

    with col_info:
        st.subheader("Información de la partición")
        st.write(f"n actual: `{n_actual}`")
        if k_actual is not None:
            st.write(f"Modo: particiones con exactamente `{k_actual}` bloques")
        else:
            st.write("Modo: todas las particiones de {1..n}")

        st.write(f"Índice actual: `{idx + 1}` de `{len(partitions)}`")
        st.write(f"Número de bloques: `{len(particion_actual)}`")
        tamaños = [len(b) for b in particion_actual]
        st.write(f"Tamaños de los bloques: `{tamaños}`")

        st.markdown("#### Partición (como bloques)")
        # Ejemplo: {{1,4}, {2,3,5}, {6}}
        bloques_str = "{ " + ", ".join("{" + ", ".join(map(str, b)) + "}" for b in particion_actual) + " }"
        st.code(bloques_str, language="text")

    with col_fig:
        st.subheader("Visualización")
        # Generar posiciones y figura
        posiciones = viz.generar_posiciones(n_actual)
        fig = viz.dibujar_particion(particion_actual, posiciones)
        st.pyplot(fig, use_container_width=True)


if __name__ == "__main__":
    main()
