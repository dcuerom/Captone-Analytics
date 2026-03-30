import pandas as pd
import sys
import os

# Agregamos la ruta del geocoder al path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../Captone-Analytics/grafo')))
from geocoder import geocode_orders

def extract_comuna(address: str) -> str:
    if not isinstance(address, str): return "N/A"
    parts = [p.strip() for p in address.split(',')]
    if "RM (Metropolitana)" in parts:
        idx = parts.index("RM (Metropolitana)")
        if idx > 0:
            return parts[idx-1]
    return "N/A"

def main():
    print("Cargando bodegas_rm.csv...")
    df = pd.read_csv("bodegas_rm.csv")
    
    # Extraer columna Comuna
    df["Comuna"] = df["Dirección"].apply(extract_comuna)
    
    # Las columnas actuales Latitud / Longitud pueden traer datos centroidales base.
    # Para usar geocode_orders() primero borramos las viejas si existen.
    if "Latitud" in df.columns:
        df.drop(columns=["Latitud"], inplace=True)
    if "Longitud" in df.columns:
        df.drop(columns=["Longitud"], inplace=True)
        
    print(f"Llamando al geocoder con {len(df)} registros...")
    
    # Llamamos a la funcion del modulo
    df_result = geocode_orders(df, address_col="Dirección")
    
    # Restore titles cases
    df_result["Latitud"] = df_result["latitud"]
    df_result["Longitud"] = df_result["longitud"]
    df_result.drop(columns=["latitud", "longitud"], inplace=True, errors="ignore")
    
    # Reordenar columnas para visualización clara
    cols = ["id", "Dirección", "Comuna", "Latitud", "Longitud", "Precio de venta", "Dimensiones"]
    df_result = df_result[[c for c in cols if c in df_result.columns]]
    
    output_filename = "bodegas_rm_geocoded.csv"
    df_result.to_csv(output_filename, index=False)
    print(f"Proceso finalizado. Archivo guardado como: {output_filename}")

if __name__ == "__main__":
    main()
