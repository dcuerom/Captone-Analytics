import pandas as pd
from grafo.main import process_daily_routing
from grafo.geocoder import geocode_orders
from grafo.network_builder import get_santiago_graph
from grafo.visualizer import plot_network_and_routes
from datos.validacion.normalizador import normalizar_pedidos

# Crear un DataFrame sucio con 3 direcciones en la RM
test_data = {
    'RUT': ['14.512.240-4', ' 17-313.403-1 ', '11.111.111-1'],
    'Número de orden': ['ORD 1   ', ' ORD\t2 ', 'ORD-3'],
    'fecha de despacho': ['2026-12-02', '2026-12-02', '2026-12-02'],
    'direccion_ruteo': [
        '  Avenida Matta 5370, Santiago, Chile  ', 
        'Avenida La Florida 7678, Santiago, Chile',
        'Plaza de Armas, Santiago, Chile'
    ],
    'volumen total_m3': [None, 4.2, 1.5],
    'peso_total_kg': [188, None, 50]
}

df_test = pd.DataFrame(test_data)
print("\n--- 1. NORMALIZACIÓN DE DATOS ---")
df_normalizado = normalizar_pedidos(df_test)
print(df_normalizado[['RUT', 'Número de orden', 'volumen total_m3', 'peso_total_kg']])

print("\n--- 2. GEOCODIFICACIÓN ---")
df_geocoded = geocode_orders(df_normalizado)
print(df_geocoded[['RUT', 'latitud', 'longitud']])

print("\n--- 3. RUTEO Y MATRIZ A* ---")
matriz, info = process_daily_routing(df_geocoded)
print("\nMATRIZ DE DISTANCIAS (KM):")
print(matriz)

print("\n--- 4. VISUALIZACIÓN ---")
# Obtener el grafo directamente para enviárselo al plot
G = get_santiago_graph(filepath='grafo/santiago_routing_graph.graphml')
plot_network_and_routes(G, info, filepath='test_rutas_santiago.html')
print("\nFlujo End-to-End Exitoso.")
