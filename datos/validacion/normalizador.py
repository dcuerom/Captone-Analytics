import pandas as pd
import re

def clean_rut(rut_series: pd.Series) -> pd.Series:
    """
    Elimina puntos, guiones y espacios de un RUT, y lo convierte a mayúsculas.
    """
    # Regex para mantener solo dígitos y la letra K
    return rut_series.astype(str).str.replace(r'[^0-9kK]', '', regex=True).str.upper()

def clean_text_column(series: pd.Series) -> pd.Series:
    """
    Normaliza el texto: elimina espacios múltiples, tabulaciones y retornos de carro.
    """
    return series.astype(str).str.replace(r'\s+', ' ', regex=True).str.strip()

def normalizar_pedidos(df: pd.DataFrame) -> pd.DataFrame:
    """
    Recibe un DataFrame de pedidos en crudo y aplica procesos de limpieza y normalización
    para asegurar la integridad de los datos antes de pasar a "process_daily_routing".
    
    1. Estandariza RUTs.
    2. Recorta espacios en las órdenes.
    3. Asegura tipos de datos correctos en coordenadas.
    4. Limpia las direcciones.
    5. Normaliza y rellena métricas nulas (volumen, peso) con 0 si faltan.
    """
    print(f"Normalizando {len(df)} registros...")
    df_norm = df.copy()
    
    # 1. Normalizar RUT
    col_rut = 'Rut' if 'Rut' in df_norm.columns else 'RUT'
    if col_rut in df_norm.columns:
        df_norm[col_rut] = clean_rut(df_norm[col_rut])
    else:
        print("Atención: No se encontró columna 'RUT' para normalizar.")
        
    # 2. Normalizar Número de orden
    col_ord = 'Número de orden' if 'Número de orden' in df_norm.columns else 'Número de Orden'
    if col_ord in df_norm.columns:
        df_norm[col_ord] = clean_text_column(df_norm[col_ord])
        
    # 3. Limpiar dirección (usualmente 'direccion_ruteo')
    if 'direccion_ruteo' in df_norm.columns:
        df_norm['direccion_ruteo'] = clean_text_column(df_norm['direccion_ruteo'])
        
    # 4. Asegurar formato numérico para lat/lon si existen
    for col in ['latitud', 'longitud']:
        if col in df_norm.columns:
            df_norm[col] = pd.to_numeric(df_norm[col], errors='coerce')
            
    # 5. Normalizar pesos y volúmenes (rellenar nulos con 0 y forzar numérico)
    if 'volumen_total_m3' in df_norm.columns:
        df_norm['volumen_total_m3'] = pd.to_numeric(df_norm['volumen_total_m3'], errors='coerce').fillna(0.0)
    elif 'volumen total_m3' in df_norm.columns:
        df_norm['volumen total_m3'] = pd.to_numeric(df_norm['volumen total_m3'], errors='coerce').fillna(0.0)
        
    if 'peso_total_kg' in df_norm.columns:
        df_norm['peso_total_kg'] = pd.to_numeric(df_norm['peso_total_kg'], errors='coerce').fillna(0.0)
        
    print("Normalización completada.")
    return df_norm

if __name__ == "__main__":
    # Prueba rápida
    data = {'RUT': ['12.345.678-9', ' 19-876,543-K', 'nada'], 
            'Número de orden': [' ORD - 123 ', 'ORD\t456', ' ']}
    df_test = pd.DataFrame(data)
    print("Pre-normalización:\n", df_test)
    print("Post-normalización:\n", normalizar_pedidos(df_test))
