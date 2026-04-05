import os
import re
import pandas as pd
import numpy as np

def parse_cvrp_instance(filepath: str):
    """
    Lee un archivo .vrp en formato TSPLIB y extrae la información requerida.
    Retorna un diccionario con:
    - name: Nombre de la instancia
    - dimension: Cantidad total de nodos
    - capacity: Capacidad máxima del vehículo
    - k_trucks: Cantidad de vehículos recomendados (extraídos del nombre, ej: A-n32-k5 -> 5)
    - df_nodos: DataFrame con id_nodo, x, y, demanda
    - depot_id: ID del nodo definido como depósito
    """
    with open(filepath, 'r') as f:
        lines = f.readlines()

    name = ""
    dimension = 0
    capacity = 0
    k_trucks = None
    
    node_coord_section = False
    demand_section = False
    depot_section = False
    
    nodes_data = {}
    demands_data = {}
    depots = []

    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        if line.startswith("NAME"):
            name = line.split(":")[-1].strip()
            # Intentar extraer el número de camiones del sufijo -kX
            match = re.search(r'-k(\d+)', name)
            if match:
                k_trucks = int(match.group(1))
        elif line.startswith("DIMENSION"):
            dimension = int(line.split(":")[-1].strip())
        elif line.startswith("CAPACITY"):
            capacity = int(line.split(":")[-1].strip())
            
        elif line.startswith("NODE_COORD_SECTION"):
            node_coord_section = True
            demand_section = False
            depot_section = False
            continue
        elif line.startswith("DEMAND_SECTION"):
            node_coord_section = False
            demand_section = True
            depot_section = False
            continue
        elif line.startswith("DEPOT_SECTION"):
            node_coord_section = False
            demand_section = False
            depot_section = True
            continue
        elif line.startswith("EOF"):
            break
            
        else:
            parts = line.split()
            if node_coord_section:
                node_id = str(parts[0])
                nodes_data[node_id] = {
                    "id_nodo": node_id,
                    "x": float(parts[1]),
                    "y": float(parts[2])
                }
            elif demand_section:
                node_id = str(parts[0])
                demands_data[node_id] = float(parts[1])
            elif depot_section:
                dep_val = str(parts[0])
                if dep_val != "-1":
                    depots.append(dep_val)
                    
    # Integrar todo en una lista de diccionarios
    data_list = []
    for node_id, coords in nodes_data.items():
        dem = demands_data.get(node_id, 0.0)
        data_list.append({
            "id_nodo": node_id,
            "x": coords["x"],
            "y": coords["y"],
            "demanda": dem
        })
        
    df_nodos = pd.DataFrame(data_list)
    depot_id = depots[0] if depots else "1"
    
    if k_trucks is None:
        filename = os.path.basename(filepath)
        match = re.search(r'-k(\d+)', filename, re.IGNORECASE)
        if match:
            k_trucks = int(match.group(1))
            
    if k_trucks is None:
        raise ValueError(f"No se pudo encontrar el límite de vehículos (K) en la cabecera ni en el nombre de archivo: {filepath}")
    
    return {
        "name": name,
        "dimension": dimension,
        "capacity": capacity,
        "k_trucks": k_trucks,
        "df_nodos": df_nodos,
        "depot_id": depot_id
    }

if __name__ == "__main__":
    # Test
    res = parse_cvrp_instance("../Instancias de Prueba VRP/A/A-n32-k5.vrp")
    print(res["name"], res["k_trucks"], res["capacity"])
    print(res["df_nodos"].head())
    print("Depósito:", res["depot_id"])
