
  # Logistics Route Optimization Platform

  This is a code bundle for Logistics Route Optimization Platform. The original project is available at https://www.figma.com/design/9QUqhBbg6Is42zO2eZSvmH/Logistics-Route-Optimization-Platform.

  ## Running the code

  Run `npm i` to install the dependencies.

  In another terminal, start the backend adapter from the repo root:

  `python backend/api_server.py`

  Run `npm run dev` to start the development server.

  The frontend consumes `GET /api/v1/data` (proxied to `http://127.0.0.1:8000` in Vite).
  
