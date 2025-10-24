# Globant – Data Engineering Coding Challenge (FastAPI + Postgres + Docker)

Backend REST para carga de CSVs, inserción por lotes (1–1000 filas) y endpoints SQL solicitados.

## 🧰 Stack
- FastAPI, SQLAlchemy 2.x, Pydantic v2
- PostgreSQL (Docker)
- Pytest
- Pandas
- Docker / Compose

## 🗂️ Endpoints
- `POST /upload/{table}`: carga CSV a `departments|jobs|hired_employees` (batch 1000 filas)
- `POST /batch/hired_employees`: inserción JSON por lotes (1–1000)
- `GET  /reports/hires_by_quarter`: hires 2021 por trimestre, ordenado por depto y job
- `GET  /reports/above_mean`: departamentos con hires > promedio 2021

## ▶️ Run (Docker recomendado)
```bash
docker compose up --build
# API en: http://localhost:8000
# Docs:   http://localhost:8000/docs
```

Copia tus CSVs en `./data/` o súbelos por `POST /upload/{table}`.

## ▶️ Run local (sin Docker)
```bash
python -m venv .venv && source .venv/bin/activate  # (Windows: .venv\Scripts\activate)
pip install -r requirements.txt
cp .env.example .env  # ajusta DATABASE_URL si es necesario
uvicorn app.main:app --reload
```

## 🧪 Tests
```bash
pytest -q
```

## 🧱 Modelo de datos (CSV)
- `departments.csv`: `id,department`
- `jobs.csv`: `id,job`
- `hired_employees.csv`: `id,name,datetime,department_id,job_id`  (datetime ISO, UTC)

## 📝 Notas
- Para producción, usar migraciones (Alembic) y manejo de credenciales vía secrets.
- El batch máximo por request es 1000 filas (requisito del challenge).
