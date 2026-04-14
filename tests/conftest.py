from __future__ import annotations

import sys
from pathlib import Path


# Asegura imports absolutos del proyecto durante pytest:
# import backend.api_server, import algoritmo..., etc.
ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

