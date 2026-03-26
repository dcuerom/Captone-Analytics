import pandas as pd
import time
import ssl
import geopy.geocoders
from geopy.geocoders import ArcGIS
from geopy.extra.rate_limiter import RateLimiter
from geopy.adapters import URLLibAdapter

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE
geopy.geocoders.options.default_ssl_context = ctx

def geocode_depot(address: str):
    """
    Recibe la dirección del depósito y la geocodifica usando ArcGIS.
    Retorna una tupla (latitud, longitud).
    """
    geolocator = ArcGIS(user_agent="capstone_analytics_vrp", adapter_factory=URLLibAdapter)
    print(f"Geocodificando depósito: {address}...")
    location = geolocator.geocode(address)
    if location:
        print(f"Depósito localizado en: ({location.latitude}, {location.longitude})")
        return location.latitude, location.longitude
    else:
        raise ValueError(f"No se pudo encontrar la dirección del depósito: {address}")

def geocode_orders(df: pd.DataFrame, address_col: str = None) -> pd.DataFrame:
    """
    Recibe un DataFrame, y para cada fila obtiene la latitud y longitud 
    usando la API de ArcGIS a través de geopy. Optimizado para direcciones únicas.
    Detecta automáticamente la columna de dirección entre 'direccion_ruteo', 'Dirección', 'direccion'.
    """
    df_result = df.copy()
    
    # Detección automática de la columna de dirección
    if address_col is None:
        for candidate in ['direccion_ruteo', 'Dirección', 'Direccion', 'direccion', 'Direc']:
            if candidate in df_result.columns:
                address_col = candidate
                break
        if address_col is None:
            raise ValueError(f"No se encontró columna de dirección. Columnas disponibles: {list(df_result.columns)}")
    
    if 'latitud' not in df_result.columns:
        df_result['latitud'] = None
    if 'longitud' not in df_result.columns:
        df_result['longitud'] = None

    # Si ya existen coordenadas para todas las filas, no geocodificar
    if df_result['latitud'].notna().all() and df_result['longitud'].notna().all():
        print("Coordenadas ya presentes en el dataset, omitiendo geocodificación.")
        return df_result

    geolocator = ArcGIS(user_agent="capstone_analytics_vrp", adapter_factory=URLLibAdapter)
    geocode = RateLimiter(geolocator.geocode, min_delay_seconds=0.2)
    
    # Obtener direcciones únicas
    direcciones_unicas = df_result[address_col].dropna().unique()
    print(f"Total de direcciones únicas a geocodificar: {len(direcciones_unicas)}")
    
    # Crear un diccionario caché para las coordenadas
    coords_cache = {}
    
    # Precargar el caché con filas que ya tengan coordenadas válidas
    for idx, row in df_result.iterrows():
        addr = row[address_col]
        if pd.notna(row['latitud']) and pd.notna(row['longitud']):
            coords_cache[addr] = (row['latitud'], row['longitud'])
    
    # Geocodificar las direcciones que faltan
    d_restantes = [d for d in direcciones_unicas if d not in coords_cache and isinstance(d, str) and d.strip()]
    print(f"Direcciones únicas restantes por geocodificar: {len(d_restantes)}")
    
    for i, address in enumerate(d_restantes):
        try:
            location = geocode(address)
            if location:
                coords_cache[address] = (location.latitude, location.longitude)
                print(f"[{i+1}/{len(d_restantes)}] Geocoded: {address} -> ({location.latitude}, {location.longitude})")
            else:
                coords_cache[address] = (None, None)
                print(f"[{i+1}/{len(d_restantes)}] Not found: {address}")
        except Exception as e:
            print(f"[{i+1}/{len(d_restantes)}] Exception on {address}: {e}")
            coords_cache[address] = (None, None)
            time.sleep(1) # Pausa si hay error de conexión
            
    # Mappear los resultados al dataframe
    def get_lat(addr):
        return coords_cache.get(addr, (None, None))[0]
    
    def get_lon(addr):
        return coords_cache.get(addr, (None, None))[1]
        
    df_result['latitud'] = df_result[address_col].apply(get_lat)
    df_result['longitud'] = df_result[address_col].apply(get_lon)
            
    return df_result

def process_and_save_geocoded_data(input_path: str, output_path: str):
    print(f"Leyendo archivo: {input_path}")
    df = pd.read_excel(input_path)
    print(f"Total de filas leídas: {len(df)}")
    
    # Procesar
    df_geocoded = geocode_orders(df)
    
    # Imprimir un resumen
    nulos = df_geocoded['Latitud'].isna().sum()
    print(f"Geocodificación finalizada. {nulos} direcciones no pudieron ser geocodificadas.")
    
    # Guardar a un nuevo archivo
    print(f"Guardando archivo geocodificado en: {output_path}")
    df_geocoded.to_excel(output_path, index=False)
    
    return df_geocoded

# if __name__ == "__main__":
#     input_file = '../EDA/vrp_orders.xlsx'
#     output_file = '../EDA/vrp_orders_geocoded.xlsx'
#     import os
#     if os.path.exists(input_file):
#         process_and_save_geocoded_data(input_file, output_file)
#     else:
#         print(f"Archivo no encontrado: {input_file}")
