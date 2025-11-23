# 📘 Simulación Visual de Particiones de Conjuntos y Árboles de Recurrencia de Stirling S(n,k)

Este proyecto implementa una herramienta interactiva para:

- **Enumerar y visualizar las particiones del conjunto ${1..n}$** usando Representaciones RGS (Restricted Growth Strings).
- **Mostrar paso a paso el árbol de recurrencia de los números de Stirling de segunda especie**  
  \( $S(n,k) = k\,S(n-1,k) + S(n-1,k-1)$ \)
- Presentar ambas visualizaciones como una **aplicación web ejecutada con Streamlit**, accesible desde cualquier navegador sin configuración adicional.

Es ideal para cursos de _Matemáticas Discretas_, combinatoria o para explorar el comportamiento de las particiones y su relación con los números de Stirling.

---

## 📂 Estructura del Proyecto

```bash
.
├── app.py # Aplicación principal Streamlit (SPA)
├── rgs.py # Algoritmos RGS para generar particiones
├── viz.py # Visualización geométrica de particiones
├── recurrencia_viz.py # Árbol de recurrencia de S(n,k)
├── requirements.txt # Dependencias del proyecto
└── README.md # Este archivo
```

---

## 🚀 Requisitos Previos

El proyecto funciona en **Windows, Linux y macOS**.

Requieres:

- Python 3.9+
- pip (gestor de paquetes)

> Se recomienda usar un entorno virtual (.venv), pero no es obligatorio.

---

## 🛠️ Instalación

Clona el repositorio:

```bash
git clone https://github.com/Torito9609/stirling_partitions_simulation.git
```

Ingresa al directorio:

```bash
cd stirling_partitions_simulation
```

(Opcional) Crear un entorno virtual

```bash
python -m venv .venv
```

### Activarlo:

#### Windows

```bash
.venv\Scripts\activate
```

#### Linux/macOS

```bash
source .venv/bin/activate
```

### Instalar dependencias

```bash
pip install -r requirements.txt
```

---

## ▶️ Ejecución de la aplicación

Desde la raíz del proyecto:

```bash
streamlit run app.py
```

Esto abrirá tu navegador en:

```bash
http://localhost:8501/
```

---

## 🎮 Uso de la aplicación

La aplicación ofrece dos vistas principales seleccionables desde la barra lateral.

### 1️⃣ Visualización de particiones

Permite:

- Elegir n, el tamaño del conjunto.

- Seleccionar modo de enumeración:

  - Todas las particiones de {1..n}

  - Exactamente k bloques

- Navegar entre particiones:

  - ⬅️ Anterior

  - ➡️ Siguiente

- Activar Auto-play, que avanza automáticamente entre particiones a un ritmo configurable.

Cada partición se muestra con:

- Información textual del bloque.

- Representación geométrica:

  - Puntos distribuidos sobre un círculo.

  - “Nubes” poligonales que encierran los elementos de un bloque.

  - Colores distintos para cada bloque.

### 2️⃣ Árbol de recurrencia de S(n,k)

Permite visualizar la expansión recursiva del cálculo de los números de Stirling de segunda especie:

$S(n,k)=kS(n−1,k)+S(n−1,k−1)$

Funciones disponibles:

- Seleccionar valores de n y k.

- Dibujar el árbol.

- Animar su construcción paso a paso.

- Frenar o reanudar la animación.

La visualización incluye:

- Nodos con $S(n,k)$ (los casos base muestran su valor).

- Colores diferenciados para casos base (naranja) y llamados recursivos (azul).

- Flechas moradas para el término $k·S(n−1,k)$

- Flechas amarillas para el término $S(n−1,k−1)$

- Una leyenda superior que explica esta convención.

---

## 🧠 Contenido matemático

### ✔️ Particiones y RGS

Se implementan versiones adaptadas de los siguientes algoritmos lexicográficos optimizados del paper:

_Stamatelatos, G. & Efraimidis, P. S. (2021).
Lexicographic Enumeration of Set Partitions.
arXiv: 2105.07472._

Algoritmos incluidos:

- V – todas las particiones

- X – particiones con exactamente k bloques

- Y, Z – disponibles para posibles extensiones

### ✔️ Recurrencia de Stirling II

La implementación usa:

- $S(0,0) = 1$
- $S(n,0) = 0$ para $n \geq 0$
- $S(n,n) = 1$
