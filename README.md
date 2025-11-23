# 📘 Simulación Visual de Particiones de Conjuntos y Árboles de Recurrencia de Stirling S(n,k)

Este proyecto implementa una herramienta interactiva para:

- **Enumerar y visualizar las particiones del conjunto {1..n}** usando Representaciones RGS (Restricted Growth Strings).
- **Mostrar paso a paso el árbol de recurrencia de los números de Stirling de segunda especie**  
  \( S(n,k) = k\,S(n-1,k) + S(n-1,k-1) \)
- Presentar ambas visualizaciones como una **aplicación web ejecutada con Streamlit**, accesible desde cualquier navegador sin configuración adicional.

Es ideal para cursos de _Matemáticas Discretas_, combinatoria o para explorar el comportamiento de las particiones y su relación con los números de Stirling.

---

## 📂 Estructura del Proyecto

├── app.py # Aplicación principal Streamlit (SPA)
├── rgs.py # Algoritmos RGS para generar particiones
├── viz.py # Visualización geométrica de particiones
├── recurrencia_viz.py # Árbol de recurrencia de S(n,k)
├── requirements.txt # Dependencias del proyecto
└── README.md # Este archivo

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
