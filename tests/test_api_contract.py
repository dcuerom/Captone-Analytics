from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

import backend.api_server as api


def test_normalize_and_validate_rejects_invalid_coordinates() -> None:
    raw = pd.DataFrame(
        [
            {
                "id_pedido": "ORD-1",
                "id_cliente": "C1",
                "direccion_ruteo": "Dir 1",
                "Comuna": "Santiago",
                "latitud": "",
                "longitud": -70.65,
                "fecha_entrega": "2026-04-08",
                "a_ventana": "09:00",
                "b_ventana": "12:00",
                "peso_pedido": 1000,
                "volumen_pedido": 50000,
            }
        ]
    )
    normalized = api._normalize_uploaded_orders(raw)
    errors = api._validate_normalized_orders(normalized)

    assert len(errors) == 1
    assert "latitud/longitud faltantes" in errors[0]["errors"]


def test_validate_rejects_invalid_time_window() -> None:
    raw = pd.DataFrame(
        [
            {
                "id_pedido": "ORD-2",
                "id_cliente": "C2",
                "direccion_ruteo": "Dir 2",
                "Comuna": "Santiago",
                "latitud": -33.45,
                "longitud": -70.66,
                "fecha_entrega": "2026-04-08",
                "a_ventana": "14:00",
                "b_ventana": "10:00",
                "peso_pedido": 1000,
                "volumen_pedido": 50000,
            }
        ]
    )
    normalized = api._normalize_uploaded_orders(raw)
    errors = api._validate_normalized_orders(normalized)

    assert len(errors) == 1
    assert "b_ventana debe ser >= a_ventana" in errors[0]["errors"]


def test_normalize_accepts_titlecase_model_columns() -> None:
    raw = pd.DataFrame(
        [
            {
                "id_pedido": "ORD-3",
                "id_cliente": "C3",
                "Dirección": "Av. Matta 123",
                "Comuna": "Santiago",
                "Latitud": -33.45,
                "Longitud": -70.66,
                "fecha_entrega": "2026-12-02",
                "a_ventana": 900,
                "b_ventana": 1020,
                "peso_pedido": 1000,
                "volumen_pedido": 50000,
            }
        ]
    )
    normalized = api._normalize_uploaded_orders(raw)
    errors = api._validate_normalized_orders(normalized)

    assert errors == []
    assert normalized.loc[0, "direccion_ruteo"] == "Av. Matta 123"
    assert float(normalized.loc[0, "latitud"]) == -33.45
    assert float(normalized.loc[0, "longitud"]) == -70.66


def test_build_payload_with_run_id_uses_run_artifacts(tmp_path: Path, monkeypatch) -> None:
    date_str = "2026-04-08"
    run_id = "run-test-001"

    results_dir = tmp_path / "resultados" / "rutas"
    map_dir = tmp_path / "resultados" / "mapa_rutas"
    eda_path = tmp_path / "EDA" / "df_despacho.csv"
    sim_path = tmp_path / "DatosSimulados" / "df_despacho.csv"
    results_dir.mkdir(parents=True, exist_ok=True)
    map_dir.mkdir(parents=True, exist_ok=True)
    eda_path.parent.mkdir(parents=True, exist_ok=True)
    sim_path.parent.mkdir(parents=True, exist_ok=True)

    algo = "hibrido"
    (results_dir / f"kpis_{algo}_{date_str}_{run_id}.csv").write_text(
        "KPI,Valor\nDistancia Total Recorrida (km),10\nCosto de Ruta (F.O. componente transporte),1000\n% Entregas a Tiempo,100\nVehÃ­culos Utilizados,1\nCapacidad Flota Fija,2\n",
        encoding="utf-8",
    )
    (results_dir / f"resumen_camiones_{algo}_{date_str}_{run_id}.csv").write_text(
        "Vehiculo_Fisico,Cluster,Distancia_km,Espera_min,Viaje_Efectivo_min,Servicio_min\n1,1,10,0,20,10\n",
        encoding="utf-8",
    )
    (results_dir / f"detalle_paradas_{algo}_{date_str}_{run_id}.csv").write_text(
        "Vehiculo_Fisico,Secuencia,Nodo,Distancia_Recorrida_km,Tiempo_Viaje_min,Hora_Llegada,Tiempo_Servicio_min,Tiempo_Espera_min,Violacion_Ventana_min,Vol_L,Peso_kg,Cluster_Visitado\n"
        "1,1,ORD-1_C1,10,20,09:10,5,0,0,100,50,1\n",
        encoding="utf-8",
    )
    (results_dir / f"clientes_atendidos_{algo}_{date_str}_{run_id}.csv").write_text(
        "id_nodo,Cluster,Atendido\nORD-1_C1,1,Si\n",
        encoding="utf-8",
    )
    (results_dir / f"run_{run_id}.json").write_text(
        json.dumps({"runId": run_id, "date": date_str, "createdAt": "2026-04-08T00:00:00Z"}),
        encoding="utf-8",
    )
    eda_path.write_text(
        "id_pedido,id_cliente,direccion_ruteo,Comuna,latitud,longitud,fecha_entrega,a_ventana,b_ventana,peso_pedido,volumen_pedido,id_nodo\n"
        "ORD-1,C1,Dir 1,Santiago,-33.45,-70.66,2026-04-08,540,720,50000,100000,ORD-1_C1\n",
        encoding="utf-8",
    )

    monkeypatch.setattr(api, "RESULTS_DIR", results_dir)
    monkeypatch.setattr(api, "MAP_DIR", map_dir)
    monkeypatch.setattr(api, "EDA_PATH", eda_path)
    monkeypatch.setattr(api, "SIM_PATH", sim_path)

    payload = api._build_payload(run_id=run_id, date_str=date_str)

    assert payload["schemaVersion"] == api.API_SCHEMA_VERSION
    assert payload["optimizationRun"]["id"] == run_id
    assert payload["optimizationRun"]["totalOrders"] == 1
    assert len(payload["orders"]) == 1
    assert len(payload["fleet"]) == 2

