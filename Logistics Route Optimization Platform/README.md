# Logistics Route Optimization Platform

This frontend is connected to the Python backend in this same repository.

## Quick start validated in this branch

From repo root:

```bash
make venv
make build
make dev
```

Full integration check:

```bash
make dev-verify
```

`make dev-verify` validates:

- backend health
- `/api/v1/data` and `/api/v1/map`
- Vite proxy on `http://127.0.0.1:5173`
- frontend + backend startup with the repo `.venv`

## Runtime notes

- The frontend now includes a SaaS demo layer with `login` and `users` screens.
- This auth layer is front-only and does not modify the backend API contract.
- Session is stored in `localStorage` for demo continuity while navigating.
- Optimization and maps still consume the real backend at `/api/v1/*`.

## Graph and optimization worker tuning

The backend now defaults to conservative execution to reduce crashes by memory pressure when loading the Santiago road graph.

Optional environment variables:

```bash
export ROUTING_MAX_WORKERS=1
export GA_CLUSTER_WORKERS=1
```

Increase them only on stronger machines after validating RAM usage.

## Windows (PowerShell): run frontend + backend

### 1) Prepare backend environment (repo root)

```powershell
cd "C:\Users\Bruno Caro\OneDrive - udd.cl\Universidad\2026\1° Trimestre\Capstone Analytics\GitHub\Captone-Analytics"
py -3 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements-saas.txt
python scripts\preflight_check.py
```

If `py` is not available, use `python` instead.

### 2) Start backend (terminal 1, repo root)

```powershell
.\.venv\Scripts\Activate.ps1
python backend\api_server.py
```

Quick check from another terminal:

```powershell
Invoke-RestMethod http://127.0.0.1:8000/api/v1/health
Invoke-RestMethod http://127.0.0.1:8000/api/v1/preflight
```

### 3) Install Node.js if `npm` is missing

```powershell
winget install OpenJS.NodeJS.LTS
```

Close and reopen PowerShell, then verify:

```powershell
node -v
npm -v
```

### 4) Start frontend (terminal 2)

```powershell
cd "C:\Users\Bruno Caro\OneDrive - udd.cl\Universidad\2026\1° Trimestre\Capstone Analytics\GitHub\Captone-Analytics\Logistics Route Optimization Platform"
npm install
npm run dev
```

By default, Vite proxies `/api/v1/*` to `http://127.0.0.1:8000`.

If needed, define:

```env
VITE_API_BASE_URL=http://127.0.0.1:8000/api/v1
```

### 5) Optional backend tests

From repo root:

```powershell
.\.venv\Scripts\Activate.ps1
python -m pytest tests\test_api_contract.py tests\test_backend_endpoints.py -q
```
