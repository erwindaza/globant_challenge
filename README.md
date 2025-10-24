# Globant – Data Engineering Coding Challenge  
**FastAPI · PostgreSQL · Docker**

This repository contains the backend solution I developed for the **Globant Data Engineering Challenge**.  
It’s a fully functional **FastAPI REST service** running with **PostgreSQL** inside Docker containers.  
The project demonstrates resilient CSV ingestion (batch processing), data validation, and the required analytical reports implemented through SQL queries.

---

## 🚀 Overview

The system exposes a REST API to:
- Upload and process CSV files for three normalized tables:  
  `departments`, `jobs`, and `hired_employees`.
- Insert large datasets in **batches of up to 1,000 rows** per request.
- Generate **two analytical reports** based on the hiring dataset:
  1. Hires by department and job per quarter (2021)
  2. Departments with total hires above the company mean (2021)

The backend includes input validation, batch insertion control, and automated commits through SQLAlchemy.  
All components run in Docker containers, making the solution fully portable and reproducible.

---

## 🧱 Tech Stack

| Component | Purpose |
|------------|----------|
| **Python 3.11** | Primary language |
| **FastAPI** | REST framework (async, high-performance) |
| **SQLAlchemy 2.x** | ORM layer for PostgreSQL |
| **Pydantic v2** | Schema and input validation |
| **PostgreSQL 15** | Relational database container |
| **Pandas** | CSV parsing and transformation |
| **Docker / Docker Compose** | Container orchestration |
| **Uvicorn** | ASGI web server |

---

## ⚙️ Project Structure

```
globant_challenge/
│
├── app/
│ ├── main.py # FastAPI entrypoint
│ ├── models.py # SQLAlchemy ORM models
│ ├── schemas.py # Pydantic schemas
│ ├── database.py # PostgreSQL connection config
│ ├── crud/ # Database operations
│ ├── routes/ # API endpoints
│ ├── utils/ # CSV loader, batch insertion logic
│ └── init.py
│
├── data/ # Sample CSV files
├── docker-compose.yml # API + PostgreSQL services
├── Dockerfile # API container definition
├── requirements.txt # Python dependencies
├── .env.example # Environment template (no credentials)
├── .gitignore # Ignored files and folders
└── README.md
```

---

## 🔧 Environment Configuration

All environment variables are defined in a `.env` file (excluded from version control).  
Example configuration for local development (`.env.dev`):

```ini
POSTGRES_USER=user
POSTGRES_PASSWORD=pass
POSTGRES_DB=globant_db
POSTGRES_HOST=db
POSTGRES_PORT=5432
BATCH_SIZE=1000
```

⚠️ Never store or commit real credentials to the repository.

---

## 🐳 Running the Project with Docker

### Clone the repository
```bash
git clone https://github.com/erwindaza/globant_challenge.git
cd globant_challenge
```

### Build and start the containers
```bash
docker compose up -d --build
```

### Verify running containers
```bash
docker compose ps
```

### Open the API documentation (Swagger UI)
👉 http://localhost:8000/docs

---

## 🧩 API Endpoints

| Method | Endpoint | Description |
|--------|-----------|--------------|
| **POST** | `/upload/{table}` | Upload CSV to departments, jobs, or hired_employees (batch = 1000 rows) |
| **POST** | `/batch/hired_employees` | Insert JSON records by batch |
| **GET** | `/reports/hires_by_quarter` | Returns hires by department/job per quarter (2021) |
| **GET** | `/reports/above_mean` | Returns departments with hires above company average (2021) |

---

## 📊 Batch Processing

The API handles bulk insertions efficiently:
- CSVs are read via Pandas and validated by column names.
- Data is inserted in batches of 1,000 rows using bulk_insert_mappings.
- Each batch is committed separately for fault tolerance.
- Example: a CSV with 1,948 rows is inserted in two batches automatically.

---

## 🧮 SQL Validation

To verify the `/reports/hires_by_quarter` endpoint, I executed the following SQL query directly in PostgreSQL:

```sql
SELECT
    d.department,
    j.job,
    SUM(CASE WHEN EXTRACT(QUARTER FROM h.datetime)=1 THEN 1 ELSE 0 END) AS Q1,
    SUM(CASE WHEN EXTRACT(QUARTER FROM h.datetime)=2 THEN 1 ELSE 0 END) AS Q2,
    SUM(CASE WHEN EXTRACT(QUARTER FROM h.datetime)=3 THEN 1 ELSE 0 END) AS Q3,
    SUM(CASE WHEN EXTRACT(QUARTER FROM h.datetime)=4 THEN 1 ELSE 0 END) AS Q4
FROM hired_employees h
JOIN departments d ON h.department_id = d.id
JOIN jobs j ON h.job_id = j.id
WHERE EXTRACT(YEAR FROM h.datetime)=2021
GROUP BY d.department, j.job
ORDER BY d.department, j.job;
```

The results were exported as:  
📄 `hires_by_quarter_2021.csv` (containing 938 aggregated rows).

---

## ✅ Validation Artifacts

| File | Description |
|------|--------------|
| `response_1761265873673.json` | API output for `/reports/hires_by_quarter` |
| `response_1761266001435.json` | API output for `/reports/above_mean` |
| `hires_by_quarter_2021.csv` | SQL validation dataset exported from PostgreSQL |

These outputs were cross-checked to ensure consistency between the API response and the SQL aggregation logic.

---

## 📈 Execution Flow Summary

1. The API receives the CSV file via `/upload/{table}`.
2. The file is read with Pandas and validated against the expected schema.
3. Data is inserted into PostgreSQL using batch transactions (1,000 rows each).
4. Two analytical endpoints produce JSON summaries:
   - **`/reports/hires_by_quarter`** → Hires grouped by quarter, department, and job.
   - **`/reports/above_mean`** → Departments exceeding the global mean of hires.

---

## 🧠 Future Improvements

- Add Pytest for automated endpoint and data validation tests.
- Extend with CI/CD (GitHub Actions) for containerized deployments.
- Deploy to AWS ECS or Azure Container Apps.
- Implement data visualization dashboards (e.g., Grafana, Streamlit).
- Integrate S3 or GCS for historical data storage.

---

## 👨‍💻 Author

**Erwin Daza Castillo**  
Senior Data Engineer – Cloud, Big Data & AI  
📧 erwin.daza@gmail.com  
🌐 [https://github.com/erwindaza](https://github.com/erwindaza)

---

## 🧾 Notes

This project was fully implemented, tested, and validated locally using Docker.  
The results are reproducible, and the repository contains all necessary assets to run the solution end-to-end.

> Challenge completed and verified successfully – including Swagger UI, data ingestion, SQL validation, and Dockerized deployment.
