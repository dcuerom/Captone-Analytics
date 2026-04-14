import gzip
import hashlib
import os
from typing import Any

from dotenv import load_dotenv

try:
    from supabase import create_client  # type: ignore
except Exception:
    create_client = None

load_dotenv()

URL = os.getenv("SUPABASE_URL")
KEY = os.getenv("SUPABASE_KEY")

supabase: Any = None
if URL and KEY and create_client is not None:
    try:
        supabase = create_client(URL, KEY)
    except Exception:
        supabase = None


def _ensure_supabase() -> None:
    if supabase is None:
        raise RuntimeError("Cliente Supabase no inicializado. Define SUPABASE_URL y SUPABASE_KEY en .env")


def _sha256_file(path: str) -> str:
    digest = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _write_checksum(path: str) -> str:
    checksum = _sha256_file(path)
    checksum_path = f"{path}.sha256"
    with open(checksum_path, "w", encoding="utf-8") as f:
        f.write(f"{checksum}  {os.path.basename(path)}\n")
    return checksum_path


def upload_graph_to_storage(local_filepath: str = "grafo/santiago_routing_graph.graphml"):
    """Sube el archivo graphml de ruteo a Supabase Storage (comprimido en GZIP)."""
    _ensure_supabase()

    if not os.path.exists(local_filepath):
        raise FileNotFoundError(f"No se encontro el archivo local: {local_filepath}")

    bucket_name = "maps"
    filename = os.path.basename(local_filepath)
    gz_filename = f"{filename}.gz"

    print(f"Comprimiendo {filename} para reducir su tamano de subida...")
    with open(local_filepath, "rb") as f_in:
        with gzip.open(gz_filename, "wb") as f_out:
            f_out.writelines(f_in)

    print(f"Subiendo {gz_filename} a Supabase (Bucket: {bucket_name}). Esto puede tomar unos minutos...")
    with open(gz_filename, "rb") as f:
        res = supabase.storage.from_(bucket_name).upload(
            file=f,
            path=gz_filename,
            file_options={"cacheControl": "3600", "upsert": "true"},
        )

    try:
        checksum_path = _write_checksum(local_filepath)
        with open(checksum_path, "rb") as f_checksum:
            supabase.storage.from_(bucket_name).upload(
                file=f_checksum,
                path=f"{filename}.sha256",
                file_options={"cacheControl": "3600", "upsert": "true"},
            )
    except Exception as exc:
        print(f"Aviso: no se pudo subir checksum del grafo ({exc}).")

    print("Subida completada exitosamente.")

    if os.path.exists(gz_filename):
        os.remove(gz_filename)

    return res


def download_graph_from_storage(local_filepath: str = "grafo/santiago_routing_graph.graphml") -> str:
    """
    Descarga el archivo del grafo comprimido desde Supabase Storage y lo descomprime.
    Si el archivo ya existe localmente y pesa mas de 0 bytes, lo reutiliza.
    """
    _ensure_supabase()

    if os.path.exists(local_filepath) and os.path.getsize(local_filepath) > 0:
        print(f"El archivo ya existe localmente en {local_filepath}. Usando cache.")
        return local_filepath

    bucket_name = "maps"
    filename = os.path.basename(local_filepath)
    gz_filename = f"{filename}.gz"

    print(f"Descargando {gz_filename} desde Supabase Storage...")
    res = supabase.storage.from_(bucket_name).download(gz_filename)

    with open(gz_filename, "wb") as f:
        f.write(res)

    print(f"Descomprimiendo el archivo {gz_filename}...")
    with gzip.open(gz_filename, "rb") as f_in:
        with open(local_filepath, "wb") as f_out:
            f_out.writelines(f_in)

    if os.path.exists(gz_filename):
        os.remove(gz_filename)

    try:
        remote_checksum_bytes = supabase.storage.from_(bucket_name).download(f"{filename}.sha256")
        remote_checksum = remote_checksum_bytes.decode("utf-8").strip().split()[0].lower()
        local_checksum = _sha256_file(local_filepath)
        if remote_checksum and remote_checksum != local_checksum:
            raise RuntimeError("Checksum del grafo descargado no coincide con storage.")
        with open(f"{local_filepath}.sha256", "w", encoding="utf-8") as f:
            f.write(f"{local_checksum}  {filename}\n")
    except Exception as exc:
        print(f"Aviso: no se pudo validar checksum remoto ({exc}). Se escribira checksum local.")
        _write_checksum(local_filepath)

    print(f"Grafo guardado exitosamente en {local_filepath}.")
    return local_filepath
