import os
from typing import Any
from dotenv import load_dotenv

try:
    from supabase import create_client  # type: ignore
except Exception:
    create_client = None

load_dotenv()

# Initialize Supabase client
URL = os.getenv("SUPABASE_URL")
KEY = os.getenv("SUPABASE_KEY")

supabase: Any = None
if URL and KEY and create_client is not None:
    try:
        supabase = create_client(URL, KEY)
    except Exception:
        supabase = None

import gzip

def upload_graph_to_storage(local_filepath: str = 'grafo/santiago_routing_graph.graphml'):
    """Sube el archivo graphml de ruteo a Supabase Storage (comprimido en GZIP)."""
    if supabase is None:
        raise RuntimeError("Cliente Supabase no inicializado. Define SUPABASE_URL y SUPABASE_KEY en .env")

    if not os.path.exists(local_filepath):
        raise FileNotFoundError(f"No se encontró el archivo local: {local_filepath}")
        
    bucket_name = "maps"
    filename = os.path.basename(local_filepath)
    gz_filename = f"{filename}.gz"
    
    # 1. Compress the file locally first
    print(f"Comprimiendo {filename} para reducir su tamaño de subida...")
    with open(local_filepath, 'rb') as f_in:
        with gzip.open(gz_filename, 'wb') as f_out:
            f_out.writelines(f_in)
            
    print(f"Subiendo {gz_filename} a Supabase (Bucket: {bucket_name}). Esto puede tomar unos minutos...")
    with open(gz_filename, 'rb') as f:
        # Se usa upsert para sobreescribir si ya existe
        res = supabase.storage.from_(bucket_name).upload(
            file=f,
            path=gz_filename,
            file_options={"cacheControl": "3600", "upsert": "true"}
        )
    print("Subida completada exitosamente.")
    
    # Clean up the temporary gz file
    if os.path.exists(gz_filename):
        os.remove(gz_filename)
        
    return res

def download_graph_from_storage(local_filepath: str = 'grafo/santiago_routing_graph.graphml') -> str:
    """
    Descarga el archivo del grafo comprimido desde Supabase Storage y lo descomprime.
    Si el archivo ya existe localmente y pesa más de 0 bytes, lo reutiliza.
    """
    if os.path.exists(local_filepath) and os.path.getsize(local_filepath) > 0:
        print(f"El archivo ya existe localmente en {local_filepath}. Usando caché.")
        return local_filepath

    bucket_name = "maps"
    filename = os.path.basename(local_filepath)
    gz_filename = f"{filename}.gz"
    
    print(f"Descargando {gz_filename} desde Supabase Storage...")
    
    # Download the byte stream of the gzipped file
    res = supabase.storage.from_(bucket_name).download(gz_filename)
    
    # Save the gz file locally
    with open(gz_filename, 'wb') as f:
        f.write(res)
        
    print(f"Descomprimiendo el archivo {gz_filename}...")
    with gzip.open(gz_filename, 'rb') as f_in:
        with open(local_filepath, 'wb') as f_out:
            f_out.writelines(f_in)
            
    # Clean up
    if os.path.exists(gz_filename):
        os.remove(gz_filename)
        
    print(f"Grafo guardado exitosamente en {local_filepath}.")
    return local_filepath
    if supabase is None:
        raise RuntimeError("Cliente Supabase no inicializado. Define SUPABASE_URL y SUPABASE_KEY en .env")
