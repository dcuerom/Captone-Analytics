import os
import time
import pandas as pd

# Directorios a monitorear
RUTA_RESULTADOS = 'resultados/rutas'
RUTA_MAPAS = 'resultados/mapa_rutas'
RUTA_SUMMARY = 'pruebas_sensibilidad/resultados_combinaciones.csv'

# Configuración de base (referencia a partir de qué fila empezamos a contar)
# Sabemos que la fila 24 (índice 23 en 0-indexed) es el inicio de la primera combinación de esta serie.
ROW_OFFSET = 23 
DAYS_PER_COMB = 4

def obtener_sufijo_actual():
    try:
        if not os.path.exists(RUTA_SUMMARY):
            return "_1.0"
        
        # Leemos el CSV para ver cuántas filas tenemos
        df = pd.read_csv(RUTA_SUMMARY)
        current_rows = len(df)
        
        # Si estamos en la fila 31, significa que han terminado 31 - 23 = 8 filas (2 combinaciones completas).
        # La siguiente fila (32) pertenecerá a la combinación 3.
        # Pero queremos el sufijo para los archivos que se están generando AHORA.
        # Los archivos se generan ANTES de que la fila se escriba en el CSV.
        # Así que si hay 31 filas, el proceso actual está trabajando en la fila 32.
        
        # Combinación = (filas_actuales - offset) // dias_por_comb + 1
        # Ejemplo: 
        # Si current_rows = 23 (solo cabecera y runs viejos), comb = (23-23)//4 + 1 = 1.
        # Si current_rows = 27 (terminó comb 1), comb = (27-23)//4 + 1 = 2.
        # Si current_rows = 31 (terminó comb 2), comb = (31-23)//4 + 1 = 3.
        
        comb_idx = (current_rows - ROW_OFFSET) // DAYS_PER_COMB + 1
        return f"_{float(comb_idx)}"
    except Exception as e:
        print(f"Error calculando sufijo: {e}")
        return "_unknown"

def obtener_archivos_sin_sufijo(directorio):
    archivos = []
    if not os.path.exists(directorio):
        return archivos
    for f in os.listdir(directorio):
        if f.endswith('.csv') or f.endswith('.html'):
            # Ignorar si ya tiene un formato de sufijo _X.Y
            base, ext = os.path.splitext(f)
            # Lógica: si el nombre termina en _[dígito].[dígito], asumimos que ya tiene sufijo
            import re
            if re.search(r'_\d+\.\d+$', base):
                continue
            archivos.append(f)
    return archivos

def renombrar_archivo(directorio, nombre_base, sufijo):
    base, ext = os.path.splitext(nombre_base)
    nombre_nuevo = f"{base}{sufijo}{ext}"
    old_path = os.path.join(directorio, nombre_base)
    new_path = os.path.join(directorio, nombre_nuevo)
    print(f"[{time.strftime('%H:%M:%S')}] Renombrando {old_path} -> {new_path}")
    os.rename(old_path, new_path)

def loop_monitoreo():
    print("Iniciando monitoreo de archivos inteligente...")
    while True:
        sufijo = obtener_sufijo_actual()
        
        files_rutas = obtener_archivos_sin_sufijo(RUTA_RESULTADOS)
        files_mapas = obtener_archivos_sin_sufijo(RUTA_MAPAS)
        
        for f in files_rutas:
            path = os.path.join(RUTA_RESULTADOS, f)
            mtime = os.path.getmtime(path)
            # Esperamos 30 segundos de inactividad para asegurar que el resumen_combinaciones 
            # ya haya sido leído/escrito si fuera el caso, aunque aquí lo usamos para detectar el cambio.
            if time.time() - mtime > 30:
                renombrar_archivo(RUTA_RESULTADOS, f, sufijo)
                
        for f in files_mapas:
            path = os.path.join(RUTA_MAPAS, f)
            mtime = os.path.getmtime(path)
            if time.time() - mtime > 30:
                renombrar_archivo(RUTA_MAPAS, f, sufijo)
        
        time.sleep(15)

if __name__ == "__main__":
    loop_monitoreo()
