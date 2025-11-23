# -------------------------------------------------------------
# RGS-based enumeration algorithms for set partitions
#
# Adaptado desde:
# Giorgos Stamatelatos & Pavlos S. Efraimidis,
# "Lexicographic Enumeration of Set Partitions",
# arXiv:2105.07472 (2021)
# Repositorio: https://github.com/gstamatelat/partitions-enumeration
#
# Algoritmos originales: V, W, X, Y, Z (en C++).
# Aquí se implementan V, X, Y, Z para Python.
#
# En ESTE proyecto usamos:
#   - Algoritmo V  → rgs_all      (todas las particiones de {1..n})
#   - Algoritmo X  → rgs_exactly  (particiones con exactamente k bloques)
#
# Las variantes Y (rgs_exactly_y) y Z (rgs_range) se dejan implementadas
# para posibles extensiones futuras (otras estrategias de enumeración).
#
# -------------------------------------------------------------
# ¿Qué es una RGS (Restricted Growth String)?
# -------------------------------------------------------------
# Dado un conjunto {1..n}, una RGS es una lista a[0..n-1] de enteros
# que codifica una partición en bloques:
#
#   - El elemento i (1 ≤ i ≤ n) cae en el bloque número a[i-1].
#   - La primera aparición de una etiqueta nueva define un nuevo bloque.
#   - Las etiquetas empiezan en 0 y crecen de a 1 (0,1,2,...).
#
# Ejemplo:
#   a = [0, 0, 1, 0, 2]
#   → bloque 0: {1,2,4}
#     bloque 1: {3}
#     bloque 2: {5}
#   → partición: {{1,2,4}, {3}, {5}}
#
# Las funciones públicas rgs_all, rgs_exactly, rgs_exactly_y y rgs_range
# generan RGS en orden lexicográfico (a nivel de RGS) y opcionalmente
# las convierten a bloques explícitos de {1..n}.
# -------------------------------------------------------------

from __future__ import annotations
from typing import Dict, Iterator, List


# -------------------------------------------------------------
# Utilidades
# -------------------------------------------------------------
def rgs_to_blocks(a: List[int]) -> List[List[int]]:
    """
    Convierte una RGS en una partición explícita de {1..n}.

    Parámetros:
        a : lista de enteros (RGS), con valores 0..m.

    Devuelve:
        Lista de bloques, donde cada bloque es una lista de enteros 1-based.
        El orden de los bloques sigue el orden de aparición de las etiquetas
        (0, luego 1, luego 2, ...).
    """
    groups: Dict[int, List[int]] = {}
    for i, label in enumerate(a, start=1):  # i es el elemento 1..n
        groups.setdefault(label, []).append(i)

    # Orden natural por etiqueta RGS (0,1,2,...) respeta el orden de creación
    return [groups[k] for k in sorted(groups.keys())]


# -------------------------------------------------------------
# Algoritmo V — Todas las particiones (sin restricción de k)
# -------------------------------------------------------------
def _next_V(a: List[int], b: List[int], n: int) -> bool:
    """
    Algoritmo V (rutina interna): avanza a la siguiente RGS en orden
    lexicográfico para 'todas las particiones' de {1..n}.

    Parámetros:
        a : RGS actual (se modifica in-place al siguiente estado).
        b : arreglo auxiliar (también modificado).
        n : longitud de la RGS (tamaño del conjunto).

    Devuelve:
        True  si existe una siguiente RGS.
        False si ya no hay más (a estaba en el último estado).
    """
    c = n - 1
    # Evita IndexError cuando c baja a 0
    while True:
        if c == 0:
            return False
        # Condición de "tope" según el paper:
        #   - a[c] == n-1  : ya usamos la etiqueta máxima posible
        #   - a[c] >  b[c] : violaría la restricción de crecimiento
        if not (a[c] == n - 1 or a[c] > b[c]):
            break
        c -= 1

    # Incrementamos la posición c
    a[c] += 1
    # Rellenamos las posiciones siguientes con el mínimo válido
    for i in range(c + 1, n):
        a[i] = 0
        b[i] = max(a[i - 1], b[i - 1])
    return True


def rgs_all(
    n: int, *, yield_blocks: bool = False
) -> Iterator[List[int] | List[List[int]]]:
    """
    Genera TODAS las RGS de longitud n (particiones de {1..n})
    usando el Algoritmo V del artículo.

    Parámetros:
        n           : tamaño del conjunto {1..n}.
        yield_blocks: si es True, se devuelven particiones como lista
                      de bloques (1-based). Si es False, se devuelve
                      la RGS cruda (lista de enteros).

    Ejemplo de uso:
        for p in rgs_all(3, yield_blocks=True):
            print(p)     # [[1,2,3]], [[1,2],[3]], ...
    """
    if n < 0:
        raise ValueError("n debe ser >= 0")
    if n == 0:
        # Por convenio, una partición vacía: [[]] o RGS vacía.
        yield [] if not yield_blocks else []
        return

    # Estado inicial según el algoritmo V: todo ceros.
    a = [0] * n
    b = [0] * n

    # Emitir estado inicial
    yield rgs_to_blocks(a) if yield_blocks else list(a)

    # Iterar hasta agotar
    while _next_V(a, b, n):
        yield rgs_to_blocks(a) if yield_blocks else list(a)


# -------------------------------------------------------------
# Algoritmo X — Exactamente k bloques
# -------------------------------------------------------------
def _first_X(a: List[int], b: List[int], n: int, k: int) -> None:
    """
    Inicializa el estado (a, b) para enumerar particiones con
    exactamente k bloques usando el Algoritmo X.

    Traducción de la rutina 'first' del C++ del paper:

        for (int i = n - 1; i > n - k; i--) {
            a[i] = k - n + i;
            b[i] = k - n + i - 1;
        }
    """
    for i in range(n - 1, n - k, -1):
        a[i] = k - n + i
        b[i] = k - n + i - 1


def _next_X(a: List[int], b: List[int], n: int, k: int) -> bool:
    """
    Algoritmo X (rutina interna): avanza a la siguiente RGS
    con exactamente k bloques.

    Parámetros:
        a, b : arreglos de estado (modificados in-place).
        n    : longitud de la RGS.
        k    : número de bloques.

    Devuelve:
        True  si existe una siguiente RGS con k bloques.
        False si ya no hay más.
    """
    while True:
        c = n - 1
        # Buscar primera posición desde la derecha que se pueda incrementar
        while a[c] == k - 1 or a[c] > b[c]:
            c -= 1
            if c == 0:
                return False
        a[c] += 1
        for i in range(c + 1, n):
            a[i] = 0
            b[i] = max(a[i - 1], b[i - 1])
        m = max(a[n - 1], b[n - 1])
        if m == k - 1:
            return True


def rgs_exactly(
    n: int, k: int, *, yield_blocks: bool = False
) -> Iterator[List[int] | List[List[int]]]:
    """
    Genera las RGS (particiones de {1..n}) con exactamente k bloques.

    Para los casos triviales se devuelve directamente la RGS apropiada
    sin invocar al Algoritmo X; para el resto (2 <= k <= n-1) se usa
    la traducción fiel del Algoritmo X.

    Parámetros:
        n, k        : tamaño del conjunto y número de bloques.
        yield_blocks: si es True, se devuelven listas de bloques (1-based);
                      si es False, se devuelven las RGS crudas.

    Esta es la función que usa la app para el modo
    "Exactamente k bloques".
    """
    # Casos inválidos
    if not (0 <= k <= n):
        return

    # Caso n = 0
    if n == 0:
        if k == 0:
            # Por convenio, partición vacía
            yield [] if not yield_blocks else []
        return

    # Caso trivial: k = 0 y n > 0 -> no hay particiones
    if k == 0:
        return

    # Caso trivial: k = 1 -> todo en un solo bloque
    if k == 1:
        a = [0] * n  # RGS: todos con etiqueta 0
        yield rgs_to_blocks(a) if yield_blocks else list(a)
        return

    # Caso trivial: k = n -> cada elemento en su propio bloque
    if k == n:
        a = list(range(n))  # RGS: [0,1,2,...,n-1]
        yield rgs_to_blocks(a) if yield_blocks else list(a)
        return

    # Resto de casos (2 <= k <= n-1) -> usamos Algoritmo X
    a = [0] * n
    b = [0] * n
    _first_X(a, b, n, k)

    # Emitir estado inicial
    yield rgs_to_blocks(a) if yield_blocks else list(a)

    # Iterar
    while _next_X(a, b, n, k):
        yield rgs_to_blocks(a) if yield_blocks else list(a)


# -------------------------------------------------------------
# Algoritmo Y — Exactamente k bloques (otra variante)
# -------------------------------------------------------------
def _first_Y(a: List[int], b: List[int], n: int, k: int) -> None:
    """
    Inicializa (a, b) para Algoritmo Y (otra forma de generar
    particiones con exactamente k bloques).

    C++ original:

        for (int i = n - k; i < n; i++) {
            a[i] = i - n + k;
            b[i] = std::max(a[i - 1], b[i - 1]);
        }
    """
    # Asumimos que a[:] y b[:] empiezan en 0
    start = n - k
    for i in range(start, n):
        a[i] = i - n + k
        b[i] = max(a[i - 1], b[i - 1]) if i - 1 >= 0 else 0


def _next_Y(a: List[int], b: List[int], n: int, k: int) -> bool:
    """
    Algoritmo Y (rutina interna): avanza a la siguiente RGS
    con exactamente k bloques.

    Es una variante del algoritmo X con un patrón diferente en
    la inicialización y en el control del borde superior.
    """
    c = n - 1
    while True:
        if c == 0:
            return False
        if not (a[c] == k - 1 or a[c] > b[c]):
            break
        c -= 1

    a[c] += 1
    for i in range(c + 1, n):
        a[i] = 0
        b[i] = max(a[i - 1], b[i - 1])

    # Ajuste para asegurar que el máximo de la RGS sea exactamente k-1
    if max(a[n - 1], b[n - 1]) != k - 1:
        i = n - 1
        k0 = k - 1
        while k0 > b[i]:
            a[i] = k0
            b[i] = k0 - 1
            i -= 1
            k0 -= 1
    return True


def rgs_exactly_y(
    n: int, k: int, *, yield_blocks: bool = False
) -> Iterator[List[int] | List[List[int]]]:
    """
    Genera las RGS (particiones de {1..n}) con exactamente k bloques
    usando la variante Y del artículo.

    En este proyecto NO se está usando rgs_exactly_y en la app principal;
    se deja como alternativa de enumeración para posibles extensiones.

    Parámetros:
        n, k        : tamaño del conjunto y número de bloques.
        yield_blocks: si es True, devuelve bloques 1-based; si es False,
                      devuelve la RGS.
    """
    if not (0 <= k <= n):
        return
    if n == 0:
        if k == 0:
            yield [] if not yield_blocks else []
        return

    a = [0] * n
    b = [0] * n
    _first_Y(a, b, n, k)

    yield rgs_to_blocks(a) if yield_blocks else list(a)
    while _next_Y(a, b, n, k):
        yield rgs_to_blocks(a) if yield_blocks else list(a)


# -------------------------------------------------------------
# Algoritmo Z — k en [kmin, kmax]
# -------------------------------------------------------------
def _first_Z(a: List[int], b: List[int], n: int, kmin: int) -> None:
    """
    Inicializa (a, b) para el Algoritmo Z, que genera RGS cuyo
    número de bloques está en el rango [kmin, kmax].

    C++ original:

        for (int i = n - 1; i > n - kmin; i--) {
            a[i] = kmin - n + i;
            b[i] = kmin - n + i - 1;
        }

    Nota: aquí b es de longitud n+1 (igual que en el paper).
    """
    for i in range(n - 1, n - kmin, -1):
        a[i] = kmin - n + i
        b[i] = kmin - n + i - 1


def _next_Z(a: List[int], b: List[int], n: int, kmin: int, kmax: int) -> bool:
    """
    Algoritmo Z (rutina interna): avanza a la siguiente RGS
    cuyo número de bloques está en [kmin, kmax].

    Traducción directa del C++:

      - b es de tamaño n+1.
      - Se maneja un número de ceros ("zeroes") para distribuir
        las etiquetas de forma que el número de bloques se mantenga
        dentro del rango permitido.
    """
    i = n - 1
    while True:
        if i == 0:
            return False
        if not (a[i] == kmax - 1 or a[i] > b[i]):
            break
        i -= 1

    a[i] += 1
    b[i + 1] = max(a[i], b[i])

    zeroes = b[i + 1] + n - i - kmin
    i += 1
    while zeroes > 0 and i < n:
        a[i] = 0
        b[i + 1] = b[i]
        i += 1
        zeroes -= 1

    while i < n:
        a[i] = b[i] + 1
        b[i + 1] = a[i]
        i += 1

    return True


def rgs_range(
    n: int, kmin: int, kmax: int, *, yield_blocks: bool = False
) -> Iterator[List[int] | List[List[int]]]:
    """
    Genera RGS (particiones de {1..n}) cuyo número de bloques
    está en el rango [kmin, kmax], usando el Algoritmo Z.

    En este proyecto tampoco se usa directamente en la app,
    pero queda disponible para experimentos donde interese
    filtrar por un rango de k.

    Parámetros:
        n           : tamaño del conjunto.
        kmin, kmax  : cota inferior y superior del número de bloques.
        yield_blocks: si es True, devuelve bloques 1-based; si es False,
                      devuelve la RGS.
    """
    if n < 0:
        raise ValueError("n debe ser >= 0")
    if not (0 <= kmin <= kmax <= n):
        return
    if n == 0:
        if kmin == 0 <= kmax:
            yield [] if not yield_blocks else []
        return

    a = [0] * n
    # b es de longitud n+1 según el original
    b = [0] * (n + 1)
    _first_Z(a, b, n, kmin)

    # Emitir estado inicial (corresponde exactamente a kmin bloques)
    yield rgs_to_blocks(a) if yield_blocks else list(a)

    # Iterar siguientes RGS dentro del rango [kmin, kmax]
    while _next_Z(a, b, n, kmin, kmax):
        yield rgs_to_blocks(a) if yield_blocks else list(a)
