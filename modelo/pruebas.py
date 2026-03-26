"""
Compatibilidad hacia atrás.

Este archivo mantiene la entrada histórica `pruebas.py`
y delega toda la ejecución en `prueba.py`.
"""

try:
    from .prueba import ejecutar_prueba_tdvrptw
except ImportError:
    from prueba import ejecutar_prueba_tdvrptw


if __name__ == "__main__":
    ejecutar_prueba_tdvrptw()
