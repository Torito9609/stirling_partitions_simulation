import io

import streamlit as st
from streamlit_autorefresh import st_autorefresh

import rgs
import viz
import recurrencia_viz


# -------------------------------------------------------------------
# App Streamlit para:
#  - Visualizar particiones de {1..n} generadas con RGS.
#  - Visualizar el árbol de recurrencia de S(n, k) (Stirling 2ª especie).
#
# Se usan dos "vistas" principales:
#   1) Visualización de particiones.
#   2) Árbol de recurrencia S(n, k).
#
# El estado de la app se maneja con st.session_state.
# -------------------------------------------------------------------


# ------------------------------------------
# Inicialización de estado
# ------------------------------------------
def init_session_state():
    """
    Inicializa claves en st.session_state con valores por defecto.

    Estas claves se usan para:
      - Guardar la lista de particiones generadas.
      - Recordar el índice actual de la partición mostrada.
      - Guardar parámetros n, k de la enumeración.
      - Controlar los parámetros y animación del árbol de recurrencia.
    """
    if "partitions" not in st.session_state:
        # Lista de particiones actuales (cada partición es lista de bloques).
        st.session_state["partitions"] = []
    if "current_index" not in st.session_state:
        # Índice de la partición actualmente mostrada.
        st.session_state["current_index"] = 0
    if "current_n" not in st.session_state:
        # Valor de n usado para generar las particiones.
        st.session_state["current_n"] = None
    if "current_k" not in st.session_state:
        # Valor de k (si aplica) usado para generar las particiones.
        st.session_state["current_k"] = None
    # Parámetros por defecto para el árbol de recurrencia S(n, k)
    if "tree_n" not in st.session_state:
        st.session_state["tree_n"] = 4
    if "tree_k" not in st.session_state:
        st.session_state["tree_k"] = 2
    if "tree_step" not in st.session_state:
        # Paso actual de la animación del árbol (nodo máximo visible).
        st.session_state["tree_step"] = 0
    if "tree_anim_play" not in st.session_state:
        # Bandera para activar/desactivar auto-play del árbol.
        st.session_state["tree_anim_play"] = False


# ------------------------------------------
# Lógica para generar particiones
# ------------------------------------------
def generar_particiones(n: int, modo: str, k: int | None = None):
    """
    Genera y guarda en session_state las particiones de {1..n}.

    Parámetros:
        n   : tamaño del conjunto {1..n}.
        modo: cadena que describe el tipo de enumeración:
              - "Todas las particiones de {1..n}"
              - "Exactamente k bloques"
        k   : número de bloques (solo se usa si el modo requiere k).

    Efectos:
        - Actualiza st.session_state["partitions"] con la lista de particiones.
        - Reinicia el índice actual a 0.
        - Guarda n y k usados.
    """
    if modo == "Todas las particiones de {1..n}":
        partes = list(rgs.rgs_all(n, yield_blocks=True))
        partes.sort(key=len)
    elif modo == "Exactamente k bloques":
        if k is None:
            partes = []
        else:
            partes = list(rgs.rgs_exactly(n, k, yield_blocks=True))
            partes.sort(key=len)
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
    """Avanza al siguiente índice de partición (si existe)."""
    if st.session_state["partitions"]:
        if st.session_state["current_index"] < len(st.session_state["partitions"]) - 1:
            st.session_state["current_index"] += 1


def retroceder():
    """Retrocede al índice anterior de partición (si existe)."""
    if st.session_state["partitions"]:
        if st.session_state["current_index"] > 0:
            st.session_state["current_index"] -= 1


# ------------------------------------------
# App principal
# ------------------------------------------
def main():
    """
    Función principal de la app Streamlit.

    Configura la página, construye la barra lateral (controles)
    y muestra una de las dos vistas:
      - Visualización de particiones.
      - Árbol de recurrencia S(n, k).
    """
    st.set_page_config(page_title="Simulación de Particiones", layout="wide")
    init_session_state()

    # ---------------- Sidebar ----------------
    with st.sidebar:
        st.title("Controles")

        # Selector de vista principal
        vista = st.radio(
            "Selecciona la vista",
            ["Visualización de particiones", "Árbol de recurrencia S(n, k)"],
            index=0,
        )

        if vista == "Visualización de particiones":

            # Parámetro n para el conjunto {1..n}
            n = st.number_input(
                "Tamaño del conjunto n",
                min_value=0,
                max_value=12,
                value=5,
                step=1,
            )

            # Modo de enumeración (todas / exactamente k bloques)
            modo = st.selectbox(
                "Modo de enumeración",
                ["Todas las particiones de {1..n}", "Exactamente k bloques"],
            )

            k = None
            if modo == "Exactamente k bloques":
                # Solo tiene sentido k entre 0 y n
                k = st.number_input(
                    "Número de bloques k",
                    min_value=0,
                    max_value=int(n),
                    value=min(2, int(n)),
                    step=1,
                )

            st.markdown("---")

            # Botón para generar (o regenerar) particiones
            if st.button("Generar particiones"):
                generar_particiones(int(n), modo, int(k) if k is not None else None)

            st.markdown("### Visualización completa")
            st.session_state.setdefault("ver_todas", False)
            ver_todas = st.toggle(
                "Mostrar todas las particiones en rejilla", value=False, help="Dibuja todas las particiones en subplots (recomendado solo para n pequeños)."
            )

            st.markdown("### Navegación")
            col_a, col_b = st.columns(2)
            with col_a:
                if st.button("⬅️ Anterior"):
                    retroceder()
            with col_b:
                if st.button("Siguiente ➡️"):
                    avanzar()

        else:
            # Controles de la vista del árbol de recurrencia
            st.markdown("### Parámetros de S(n, k)")
            tree_n = st.number_input(
                "n (tamaño del conjunto)",
                min_value=1,
                max_value=12,
                value=4,
                step=1,
            )
            tree_k = st.number_input(
                "k (número de bloques)",
                min_value=0,
                max_value=int(tree_n),
                value=2,
                step=1,
            )

            if st.button("Mostrar árbol"):
                # Guardamos n y k elegidos para redibujar el árbol
                st.session_state["tree_n"] = int(tree_n)
                st.session_state["tree_k"] = int(tree_k)

            st.markdown("### Animación del árbol")

            # Botones para activar/pausar el auto-play del árbol
            col_t1, col_t2 = st.columns(2)
            with col_t1:
                if st.button("▶️ Play árbol"):
                    st.session_state["tree_anim_play"] = True
            with col_t2:
                if st.button("⏸️ Pause árbol"):
                    st.session_state["tree_anim_play"] = False

    # ---------------- Contenido principal ----------------
    if vista == "Visualización de particiones":
        st.title("Simulación de particiones de un conjunto")

        if not st.session_state["partitions"]:
            st.info("Genera las particiones desde la barra lateral para comenzar.")
            return

        partitions = st.session_state["partitions"]
        idx = st.session_state["current_index"]
        n_actual = st.session_state["current_n"]
        k_actual = st.session_state["current_k"]

        # Partición actual como lista de bloques, por ejemplo: [[1,4], [2,3,5], [6]]
        particion_actual = partitions[idx]

        # Información textual (izquierda) y figura (derecha)
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
            tamanos = [len(b) for b in particion_actual]
            st.write(f"Tamaños de los bloques: `{tamanos}`")

            st.markdown("#### Partición (como bloques)")
            # Ejemplo visual: { {1,4}, {2,3,5}, {6} }
            bloques_str = (
                "{ "
                + ", ".join(
                    "{" + ", ".join(map(str, b)) + "}" for b in particion_actual
                )
                + " }"
            )
            st.code(bloques_str, language="text")

        with col_fig:
            st.subheader("Visualización")
            # Generar posiciones para los puntos y dibujar la partición
            posiciones = viz.generar_posiciones(n_actual)
            fig = viz.dibujar_particion(particion_actual, posiciones)
            st.pyplot(fig, use_container_width=True)

        st.markdown("---")
        st.subheader("Todas las particiones")
        limite_n = 7
        if not ver_todas:
            st.info("Activa el toggle en la barra lateral para mostrar todas las particiones en subplots.")
        elif n_actual is not None and n_actual > limite_n:
            st.warning(
                f"n = {n_actual} genera {len(partitions)} particiones. Reduce n (≤ {limite_n}) para evitar la explosión combinatoria al dibujarlas."
            )
        else:
            grid_fig = viz.dibujar_particiones_en_grid(partitions, n=n_actual)
            st.pyplot(grid_fig, use_container_width=True)

            buffer = io.BytesIO()
            grid_fig.savefig(buffer, format="png", bbox_inches="tight", facecolor=grid_fig.get_facecolor())
            st.download_button(
                "Descargar figura de subplots",
                data=buffer.getvalue(),
                file_name=f"particiones_n{n_actual}.png",
                mime="image/png",
            )

    else:
        st.title("Árbol de recurrencia de S(n, k)")

        n_tree = st.session_state["tree_n"]
        k_tree = st.session_state["tree_k"]
        step = st.session_state["tree_step"]

        # Dibujar el árbol hasta el nodo con índice = step
        fig, total_nodes = recurrencia_viz.dibujar_arbol_recurrencia(
            n_tree, k_tree, step=step
        )
        st.pyplot(fig, use_container_width=False)

        st.write(f"Número total de nodos en el árbol: {total_nodes}")

        # Slider para moverse manualmente por la animación del árbol
        new_step = st.slider(
            "Paso de animación (nodo máximo visible)",
            min_value=0,
            max_value=max(total_nodes - 1, 0),
            value=step,
        )

        if new_step != step:
            st.session_state["tree_step"] = new_step

        # Auto-play del árbol usando st_autorefresh
        if st.session_state["tree_anim_play"]:
            count = st_autorefresh(
                interval=800,  # milisegundos entre pasos (0.8 s)
                limit=None,
                key="tree_autoplay_counter",
            )
            # Avanzamos un paso cada vez que cambia el contador
            if st.session_state["tree_step"] < total_nodes - 1:
                st.session_state["tree_step"] += 1
            else:
                # Si llegamos al último nodo, detenemos el auto-play
                st.session_state["tree_anim_play"] = False
        else:
            # Si está pausado, no hacemos nada extra
            pass


if __name__ == "__main__":
    main()
