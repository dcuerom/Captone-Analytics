from __future__ import annotations

import json
import threading
import urllib.error
import urllib.request
from http.server import ThreadingHTTPServer
from pathlib import Path
from typing import Any, Dict, Tuple

import pytest

import backend.api_server as api


def _http_request(url: str, method: str = "GET", payload: Dict[str, Any] | None = None) -> Tuple[int, Dict[str, Any]]:
    data = None
    headers = {"Accept": "application/json"}
    if payload is not None:
        data = json.dumps(payload).encode("utf-8")
        headers["Content-Type"] = "application/json"

    req = urllib.request.Request(url=url, data=data, method=method, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=5) as resp:
            body = resp.read().decode("utf-8")
            return resp.status, json.loads(body) if body else {}
    except urllib.error.HTTPError as err:
        body = err.read().decode("utf-8")
        return err.code, json.loads(body) if body else {}


@pytest.fixture()
def live_server(tmp_path: Path, monkeypatch):
    eda_path = tmp_path / "EDA" / "df_despacho.csv"
    sim_path = tmp_path / "DatosSimulados" / "df_despacho.csv"
    eda_path.parent.mkdir(parents=True, exist_ok=True)
    sim_path.parent.mkdir(parents=True, exist_ok=True)

    monkeypatch.setattr(api, "EDA_PATH", eda_path)
    monkeypatch.setattr(api, "SIM_PATH", sim_path)
    monkeypatch.setattr(
        api,
        "_preflight_check",
        lambda: {"status": "ok", "failedCount": 0, "checks": []},
    )
    monkeypatch.setattr(
        api,
        "_build_payload",
        lambda run_id=None, date_str=None: {
            "schemaVersion": api.API_SCHEMA_VERSION,
            "generatedAt": "2026-01-01T00:00:00Z",
            "optimizationRun": {"id": run_id or "run-x", "name": "run", "date": date_str or "2026-04-08", "routes": []},
            "orders": [],
            "fleet": [],
            "historicalRuns": [],
        },
    )
    monkeypatch.setattr(
        api,
        "_start_optimization_async",
        lambda requested_date, config=None, run_id=None, depot_address=None: {
            "started": True,
            "reason": "started",
            "state": {
                "runId": run_id,
                "status": "running",
                "requestedDate": requested_date,
                "depotAddress": depot_address,
            },
        },
    )

    server = ThreadingHTTPServer(("127.0.0.1", 0), api.Handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    base_url = f"http://127.0.0.1:{server.server_address[1]}"
    try:
        yield base_url
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=2)


def test_health_endpoint(live_server: str) -> None:
    status, data = _http_request(f"{live_server}/api/v1/health")
    assert status == 200
    assert data["status"] == "ok"


def test_preflight_endpoint(live_server: str) -> None:
    status, data = _http_request(f"{live_server}/api/v1/preflight")
    assert status == 200
    assert data["status"] == "ok"


def test_data_endpoint_accepts_run_id(live_server: str) -> None:
    status, data = _http_request(f"{live_server}/api/v1/data?runId=run-123&date=2026-04-08")
    assert status == 200
    assert data["schemaVersion"] == api.API_SCHEMA_VERSION
    assert data["optimizationRun"]["id"] == "run-123"


def test_optimize_endpoint_accepts_run_and_depot(live_server: str) -> None:
    status, data = _http_request(
        f"{live_server}/api/v1/optimize",
        method="POST",
        payload={
            "date": "2026-04-08",
            "runId": "run-opt-001",
            "depotAddress": "Santa Elena - Sierra Bella, Santiago, RM, Chile",
            "config": {"ga_n_gen": 200},
        },
    )
    assert status == 202
    assert data["runId"] == "run-opt-001"
    assert data["status"] == "running"


def test_upload_orders_endpoint_rejects_invalid_rows(live_server: str) -> None:
    csv_text = (
        "id_pedido,id_cliente,direccion_ruteo,Comuna,latitud,longitud,fecha_entrega,a_ventana,b_ventana,peso_pedido,volumen_pedido\n"
        "ORD-1,C1,Dir 1,Santiago,,-70.66,2026-04-08,09:00,12:00,1000,10000\n"
    )
    status, data = _http_request(
        f"{live_server}/api/v1/upload-orders",
        method="POST",
        payload={"filename": "orders.csv", "csv": csv_text},
    )
    assert status == 400
    assert "invalidRows" in data
    assert data["invalidRows"] >= 1
