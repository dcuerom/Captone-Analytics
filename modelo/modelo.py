"""
modelo/modelo.py

Modelo matemático base para el Time-Dependent Vehicle Routing Problem with Time Windows (TDVRPTW)
Utilizando la estructura de Pyomo para optimización exacta.
Unidades Estricta: Tiempo (min), Distancia (m), Volumen (cm3), Masa (g).
"""

from pyomo.environ import *

def crear_modelo_tdvrptw():
    """
    Instancia un ConcreteModel de Pyomo con los conjuntos, parámetros y variables
    base correspondientes al archivo modelo.md actualizado.
    
    Parámetros como K y S quedan vacíos a rellenar por la capa de Algoritmo.
    """
    model = ConcreteModel(name="TDVRPTW_Cluster_First")
    
    # =========================================================
    # 1. ZONA TODO: Definiciones de Flota y Costos
    # =========================================================
    # TODO: Rellenar por el usuario desde capa externa
    NOMBRES_CAMIONES = []  # ej. ['C1', 'C2']
    VALOR_S = None         # Cociente Costo combustible / rendimiento
    
    # =========================================================
    # 2. CONJUNTOS
    # =========================================================
    model.C = Set(doc="Conjunto de Nodos Clientes (ej. 1..N)")
    model.DEPOT = Set(initialize=[0], doc="Nodo Depósito Central")
    model.I = Set(initialize=lambda m: m.C | m.DEPOT, doc="Todos los Nodos (C U {0})")
    
    model.K = Set(initialize=NOMBRES_CAMIONES, doc="Conjunto de Camiones")
    model.T = Set(doc="Intervalos de partición temporales t")
    
    # =========================================================
    # 3. PARÁMETROS (VACÍOS MUTABLES)
    # =========================================================
    # Unidades: VOL(cm3), MASA(g), DIST(m), TIEMPO(min)
    
    # Parámetros de flota
    model.Cv = Param(model.K, default=0, mutable=True, doc="Capacidad en volumen del camión k [cm3]")
    model.Cm = Param(model.K, default=0, mutable=True, doc="Capacidad en peso del camión k [g]")
    model.S = Param(default=0 if VALOR_S is None else VALOR_S, mutable=True, doc="Factor de Costo Combustible S")
    
    # Parámetros de clientes
    model.VP = Param(model.I, default=0, mutable=True, doc="Volumen del pedido i [cm3]")
    model.PP = Param(model.I, default=0, mutable=True, doc="Masa del pedido i [g]")
    model.a = Param(model.I, default=0, mutable=True, doc="Límite inf. ventana cliente i [min]")
    model.b = Param(model.I, default=1440, mutable=True, doc="Límite sup. ventana cliente i [min]")
    model.s = Param(model.I, default=0, mutable=True, doc="Atención variable cliente i o prep en DEPOT [min]")
    
    # Parámetros Logísticos Globales
    model.aten = Param(default=0, mutable=True, doc="Tiempo atención fijo [min]")
    model.d_max = Param(default=1440, mutable=True, doc="Duración máxima ruta [min]")
    model.M = Param(default=100000, mutable=True, doc="Big-M")
    
    # Tensores espaciales y temporales
    model.Dist = Param(model.I, model.I, default=999999, mutable=True, doc="Distancia arco i->j [m]")
    # Tensor 3D Time-Dependent: Tiempo de viaje entre i,j saliendo en intervalo t
    model.T_viaje = Param(model.I, model.I, model.T, default=999999, mutable=True, doc="Tiempo de viaje TD [min]")
    
    # =========================================================
    # 4. VARIABLES DE DECISIÓN
    # =========================================================
    # Binaria: 1 si el camión k utiliza el arco i->j saliendo de i en el periodo t
    model.X = Var(model.I, model.T, model.I, model.K, domain=Binary, doc="Travesía de arcos dependiente del tiempo")
    
    # Continua: Tiempo de llegada del camión k al nodo j
    model.ts = Var(model.I, model.K, domain=NonNegativeReals, doc="Llegada al nodo i [min]")
    
    # =========================================================
    # 5. RESTRICCIONES RELEVANTES (Referencia de modelo.md)
    # =========================================================
    # Nota: Las restricciones reales formales irían conectadas aquí si se
    # usara Pyomo para solver lineal, pero como resolveremos mediante GA / Tabu,
    # la clase Pyomo operará más bien como definición canónica de los espacios.
    
    def obj_rule(m):
        # min sum(X * Dist * S)
        return sum(
            m.X[i, t, j, k] * m.Dist[i, j] * m.S
            for i in m.I for j in m.I for t in m.T for k in m.K
        )
    model.Obj = Objective(rule=obj_rule, sense=minimize)
    
    return model
