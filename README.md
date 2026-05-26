# Breathe ESG Ingestion Prototype

Monorepo with a Django REST backend and a React (Vite) frontend.

## Local setup

### Backend

1. Create a virtual environment.
2. Install deps:
   - `pip install -r backend/requirements.txt`
3. Run migrations (SQLite is the default for local dev):
   - `python backend/manage.py migrate`
4. Start the server:
   - `python backend/manage.py runserver 8000`

Optional: set `DATABASE_URL` in backend/.env.example to use Postgres locally.

### Frontend

1. Install deps:
   - `cd frontend`
   - `npm install`
2. Start the dev server:
   - `npm run dev`

### Sample data

CSV samples are in the sample-data folder:
- sap_fuel_procurement.csv
- utility_electricity.csv
Travel JSON sample:
- travel_export.json

### Create a company

Use the UI button "Create default company" or POST to `/api/companies/`.

## API overview

- `GET /api/health/`
- `GET /api/companies/`
- `POST /api/companies/`
- `POST /api/ingest/` (multipart form with `company_id`, `source_type`, `file`)
- `GET /api/batches/`
- `GET /api/records/`
- `GET /api/records/{id}/detail/`
- `POST /api/records/{id}/approve/`
- `POST /api/records/{id}/reject/`
- `POST /api/records/{id}/lock/`
- `PATCH /api/records/{id}/`

## Render deployment

This repo includes a render.yaml blueprint. Create a new Render Blueprint service pointing at the repo.

1. Set backend env vars:
   - `DJANGO_SECRET_KEY`
   - `DJANGO_DEBUG=false`
   - `ALLOWED_HOSTS=<render-backend-host>`
   - `CORS_ALLOWED_ORIGINS=<render-frontend-url>`
2. For the frontend, set `VITE_API_URL` to the backend URL.

Note: Render deployment uses Postgres via `DATABASE_URL`. Local dev defaults to SQLite.
