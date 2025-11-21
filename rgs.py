# -------------------------------------------------------------
# RGS-based enumeration algorithms for set partitions
# 
# Adaptado desde:
# Giorgos Stamatelatos & Pavlos S. Efraimidis,
# "Lexicographic Enumeration of Set Partitions",
# arXiv:2105.07472 (2021)
# Repositorio: https://github.com/gstamatelat/partitions-enumeration
# 
# Algoritmos originales: V, W, X, Y, Z (originalmente implementados en C++)
# Licencia y información de cita: ver CITATION.cff en la raíz del proyecto.
# -------------------------------------------------------------


from __future__ import annotations
from typing import Dict, Iterator, List


# -------------------------------------------------------------
# Utilidades
# -------------------------------------------------------------

def rgs_to_blocks(a: List[int]) -> List[List[int]]:
    """
    Convierte una RGS (valores 0..m) en una partición de {1..n}.
    Devuelve una lista de bloques (cada bloque es lista de ints 1-based).
    El orden de bloques será por el primer índice donde aparece cada etiqueta.
    """
    groups: Dict[int, List[int]] = {}
    for i, label in enumerate(a, start=1):  # i es el elemento 1..n
        groups.setdefault(label, []).append(i)
    # Orden natural por etiqueta RGS (0,1,2,...) ya respeta orden de creación
    return [groups[k] for k in sorted(groups.keys())]


# -------------------------------------------------------------
# Algoritmo V — Todas las particiones (sin restricción de k)
# -------------------------------------------------------------

def _next_V(a: List[int], b: List[int], n: int) -> bool:
    """
    Avanza a la siguiente RGS en orden lexicográfico para 'todas las particiones'.
    Devuelve False si ya no hay siguiente.
    Traducción directa del 'next' del Algoritmo V (C++).
    """
    c = n - 1
    # Evita IndexError cuando c baja a 0
    while True:
        if c == 0:
            return False
        if not (a[c] == n - 1 or a[c] > b[c]):
            break
        c -= 1

    a[c] += 1
    for i in range(c + 1, n):
        a[i] = 0
        b[i] = max(a[i - 1], b[i - 1])
    return True

def rgs_all(n: int, *, yield_blocks: bool = False) -> Iterator[List[int] | List[List[int]]]:
    """
    Genera todas las RGS de longitud n (particiones de {1..n}) usando Algoritmo V.
    Si yield_blocks=True, devuelve la partición como lista de bloques (1-based).
    """
    if n < 0:
        raise ValueError("n debe ser >= 0")
    if n == 0:
        # Por convenio, una partición vacía: [[]] o RGS vacía.
        yield [] if not yield_blocks else []
        return

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
    Inicializa el estado (a, b) para enumerar particiones con exactamente k bloques (Algoritmo X).
    Traducción directa de la rutina 'first' del C++.
    """
    # for (int i = n - 1; i > n - k; i--)
    #   a[i] = k - n + i;
    #   b[i] = k - n + i - 1;
    for i in range(n - 1, n - k, -1):
        a[i] = k - n + i
        b[i] = k - n + i - 1


def _next_X(a: List[int], b: List[int], n: int, k: int) -> bool:
    """
    Avanza a la siguiente RGS con exactamente k bloques (Algoritmo X).
    Devuelve False si ya no hay siguiente.
    """
    while True:
        c = n - 1
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


def rgs_exactly(n: int, k: int, *, yield_blocks: bool = False) -> Iterator[List[int] | List[List[int]]]:
    """
    Genera las RGS (particiones de {1..n}) con exactamente k bloques (Algoritmo X).
    Si yield_blocks=True, devuelve la partición como lista de bloques (1-based).
    """
    if not (0 <= k <= n):
        return
    if n == 0:
        if k == 0:
            yield [] if not yield_blocks else []
        return

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
    Inicializa (a, b) para Algoritmo Y.
    C++:
      for (int i = n - k; i < n; i++) {
          a[i] = i - n + k;
          b[i] = std::max(a[i - 1], b[i - 1]);
      }
    """
    # Asumimos que a[:], b[:] empiezan en 0
    start = n - k
    for i in range(start, n):
        a[i] = i - n + k
        b[i] = max(a[i - 1], b[i - 1]) if i - 1 >= 0 else 0


def _next_Y(a: List[int], b: List[int], n: int, k: int) -> bool:
    """
    Avanza a la siguiente RGS con exactamente k bloques (Algoritmo Y).
    Devuelve False si ya no hay siguiente.
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

    if max(a[n - 1], b[n - 1]) != k - 1:
        i = n - 1
        k0 = k - 1
        while k0 > b[i]:
            a[i] = k0
            b[i] = k0 - 1
            i -= 1
            k0 -= 1
    return True


def rgs_exactly_y(n: int, k: int, *, yield_blocks: bool = False) -> Iterator[List[int] | List[List[int]]]:
    """
    Genera las RGS (particiones) con exactamente k bloques usando la variante Y.
    Si yield_blocks=True, devuelve la partición como lista de bloques (1-based).
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
# Nota: aquí b es de longitud n+1 en el C++ original.
# -------------------------------------------------------------

def _first_Z(a: List[int], b: List[int], n: int, kmin: int) -> None:
    """
    Inicializa (a, b) para Algoritmo Z (rango de k).
    C++:
      for (int i = n - 1; i > n - kmin; i--) {
          a[i] = kmin - n + i;
          b[i] = kmin - n + i - 1;
      }
    """
    for i in range(n - 1, n - kmin, -1):
        a[i] = kmin - n + i
        b[i] = kmin - n + i - 1


def _next_Z(a: List[int], b: List[int], n: int, kmin: int, kmax: int) -> bool:
    """
    Avanza a la siguiente RGS con k en [kmin, kmax] (Algoritmo Z).
    Devuelve False si ya no hay siguiente.
    Traducción directa del C++:
      - b es de tamaño n+1
      - lógica de zeroes y posterior relleno mínimo
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


def rgs_range(n: int, kmin: int, kmax: int, *, yield_blocks: bool = False) -> Iterator[List[int] | List[List[int]]]:
    """
    Genera RGS (particiones de {1..n}) cuyo número de bloques está en [kmin, kmax].
    Si yield_blocks=True, devuelve la partición como lista de bloques (1-based).
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

    # Emitir estado inicial: asegurar que el máximo esté en rango
    # (la inicialización Z coloca exactamente kmin bloques)
    yield rgs_to_blocks(a) if yield_blocks else list(a)

    while _next_Z(a, b, n, kmin, kmax):
        yield rgs_to_blocks(a) if yield_blocks else list(a)
