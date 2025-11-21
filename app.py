import streamlit as st

import rgs
import viz
import recurrencia_viz



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
    if "auto_play" not in st.session_state:
        st.session_state["auto_play"] = False
    if "last_auto_count" not in st.session_state:
        st.session_state["last_auto_count"] = 0 
    if "tree_n" not in st.session_state:
        st.session_state["tree_n"] = 4   # por defecto
    if "tree_k" not in st.session_state:
        st.session_state["tree_k"] = 2   # por defecto




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
        
        vista = st.radio(
        "Selecciona la vista",
        ["Visualización de particiones", "Árbol de recurrencia S(n, k)"],
        index=0,
        )
        
        intervalo = None
        
        if vista == "Visualización de particiones":

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
                    
            from streamlit_autorefresh import st_autorefresh  # pon este import al inicio del archivo también

            st.markdown("### Auto-play")

            intervalo = st.slider("Intervalo (segundos)", 0.5, 5.0, 1.5, 0.1)

            col_auto1, col_auto2 = st.columns(2)
            with col_auto1:
                if st.button("▶️ Iniciar auto-play"):
                    st.session_state["auto_play"] = True
            with col_auto2:
                if st.button("⏸️ Pausar auto-play"):
                    st.session_state["auto_play"] = False

            # -----------------------------------
            # AUTO-PLAY con st_autorefresh
            # -----------------------------------
            if st.session_state["auto_play"]:
                # Disparar un rerun cada `intervalo` segundos
                count = st_autorefresh(
                    interval=int(intervalo * 1000),  # ms
                    limit=None,
                    key="autoplay_counter",
                )

                # Si el contador cambió, avanzamos una partición
                if count != st.session_state["last_auto_count"]:
                    st.session_state["last_auto_count"] = count

                    if st.session_state["current_index"] < len(st.session_state["partitions"]) - 1:
                        st.session_state["current_index"] += 1
                    else:
                        # Si llegamos al final, detenemos el auto-play
                        st.session_state["auto_play"] = False
            else:
                # Si el autoplay está apagado, reseteamos el contador
                st.session_state["last_auto_count"] = 0
        else:
            st.markdown("### Parámetros de S(n, k)")
            tree_n = st.number_input("n (tamaño del conjunto)", min_value=1, max_value=12, value=4, step=1)
            tree_k = st.number_input("k (número de bloques)", min_value=0, max_value=int(tree_n), value=2, step=1)

            if st.button("Mostrar árbol"):
                st.session_state["tree_n"] = int(tree_n)
                st.session_state["tree_k"] = int(tree_k)

            # En esta vista no usamos autoplay
            st.session_state["auto_play"] = False


    
    


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
    else:
        st.title("Árbol de recurrencia de S(n, k)")

        n_tree = st.session_state["tree_n"]
        k_tree = st.session_state["tree_k"]

        st.write(f"Mostrando el árbol de recurrencia para S({n_tree}, {k_tree}).")

        fig = recurrencia_viz.dibujar_arbol_recurrencia(n_tree, k_tree)
        st.pyplot(fig, use_container_width=False)

        st.markdown(
            """
            Aquí luego vamos a:
            - Dibujar el árbol de llamadas recursivas de S(n,k) = k·S(n−1,k) + S(n−1,k−1)
            - Resaltar las ramas, casos base, etc.
            """
        )


if __name__ == "__main__":
    main()
