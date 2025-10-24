from fastapi import FastAPI, UploadFile, File, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func, case, extract
import pandas as pd
from io import StringIO

from app.database import get_session, Base, engine
from app import models, schemas

# -------------------------------------------------------------
# Inicialización de la app
# -------------------------------------------------------------
app = FastAPI(
    title="Globant Challenge API",
    version="1.0.0",
    description="FastAPI application for data ingestion and reporting."
)

# Crear las tablas automáticamente
Base.metadata.create_all(bind=engine)

# -------------------------------------------------------------
# Dependency para sesión DB
# -------------------------------------------------------------
def get_db():
    db = next(get_session())
    try:
        yield db
    finally:
        db.close()

# -------------------------------------------------------------
# Función utilitaria para cargar CSV
# -------------------------------------------------------------
def load_csv_to_db(db: Session, file: UploadFile, model):
    try:
        content = file.file.read().decode("utf-8")

        # 👇 Detecta separador automáticamente, ignora BOM
        df = pd.read_csv(StringIO(content), sep=None, engine="python", encoding="utf-8-sig")

        if model == models.HiredEmployee:
            required_cols = {"id", "name", "datetime", "department_id", "job_id"}
            if not required_cols.issubset(df.columns):
                raise HTTPException(status_code=400, detail="Invalid CSV columns for hired_employees")

            # Convertir fechas
            df["datetime"] = pd.to_datetime(df["datetime"], errors="coerce")

            # 🧹 Eliminar filas con datos críticos vacíos
            df = df.dropna(subset=["id", "department_id", "job_id", "datetime"])

            # Convertir tipos con cuidado (sin fallar si hay NaN)
            df["id"] = df["id"].astype(int)
            df["department_id"] = df["department_id"].astype(int)
            df["job_id"] = df["job_id"].astype(int)
            df["name"] = df["name"].astype(str)

        elif model == models.Department:
            required_cols = {"id", "department"}
            if not required_cols.issubset(df.columns):
                raise HTTPException(status_code=400, detail="Invalid CSV columns for departments")
            df["id"] = df["id"].astype(int)
            df["department"] = df["department"].astype(str)

        elif model == models.Job:
            required_cols = {"id", "job"}
            if not required_cols.issubset(df.columns):
                raise HTTPException(status_code=400, detail="Invalid CSV columns for jobs")
            df["id"] = df["id"].astype(int)
            df["job"] = df["job"].astype(str)

        # 🚀 Insertar por lotes de 1000 filas
        batch_size = 1000
        total_rows = len(df)
        for start in range(0, total_rows, batch_size):
            end = start + batch_size
            batch = df.iloc[start:end].to_dict(orient="records")
            db.bulk_insert_mappings(model, batch)
            db.commit()

        return {"rows_inserted": total_rows, "batches": (total_rows // batch_size) + 1}

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=f"Failed to process CSV: {str(e)}")


# -------------------------------------------------------------
# Endpoint general: subir CSV a tabla específica
# -------------------------------------------------------------
@app.post("/upload/{table_name}")
def upload_csv(table_name: str, file: UploadFile = File(...), db: Session = Depends(get_db)):
    """
    Upload a CSV file and insert its rows into the corresponding table.
    Example: /upload/departments, /upload/jobs, /upload/hired_employees
    """
    table_map = {
        "departments": models.Department,
        "jobs": models.Job,
        "hired_employees": models.HiredEmployee
    }

    model = table_map.get(table_name.lower())
    if not model:
        raise HTTPException(status_code=400, detail="Invalid table name")

    result = load_csv_to_db(db, file, model)
    return {"message": f"Data inserted into {table_name}", **result}

# -------------------------------------------------------------
# Reporte 1: Hires por trimestre en 2021
# -------------------------------------------------------------
@app.get("/reports/hires_by_quarter", response_model=list[schemas.ReportByQuarter])
def hires_by_quarter(db: Session = Depends(get_db)):
    """
    Returns number of employees hired for each job and department in 2021, divided by quarter.
    """
    try:
        results = (
            db.query(
                models.Department.department.label("department"),
                models.Job.job.label("job"),
                func.sum(
                    case((extract("quarter", models.HiredEmployee.datetime) == 1, 1), else_=0)
                ).label("Q1"),
                func.sum(
                    case((extract("quarter", models.HiredEmployee.datetime) == 2, 1), else_=0)
                ).label("Q2"),
                func.sum(
                    case((extract("quarter", models.HiredEmployee.datetime) == 3, 1), else_=0)
                ).label("Q3"),
                func.sum(
                    case((extract("quarter", models.HiredEmployee.datetime) == 4, 1), else_=0)
                ).label("Q4"),
            )
            .join(models.HiredEmployee, models.HiredEmployee.department_id == models.Department.id)
            .join(models.Job, models.HiredEmployee.job_id == models.Job.id)
            .filter(extract("year", models.HiredEmployee.datetime) == 2021)
            .group_by(models.Department.department, models.Job.job)
            .order_by(models.Department.department.asc(), models.Job.job.asc())
            .all()
        )

        return [
            {
                "department": r.department,
                "job": r.job,
                "Q1": int(r.Q1),
                "Q2": int(r.Q2),
                "Q3": int(r.Q3),
                "Q4": int(r.Q4)
            }
            for r in results
        ]

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating report: {str(e)}")

# -------------------------------------------------------------
# Reporte 2: Departamentos sobre la media de contrataciones 2021
# -------------------------------------------------------------
@app.get("/reports/above_mean", response_model=list[schemas.AboveMeanOut])
def departments_above_mean(db: Session = Depends(get_db)):
    """
    Returns departments that hired more employees than the mean in 2021.
    """
    try:
        subquery = (
            db.query(
                models.HiredEmployee.department_id,
                func.count(models.HiredEmployee.id).label("total")
            )
            .filter(extract("year", models.HiredEmployee.datetime) == 2021)
            .group_by(models.HiredEmployee.department_id)
            .subquery()
        )

        mean_val = db.query(func.avg(subquery.c.total)).scalar() or 0

        results = (
            db.query(
                models.Department.id,
                models.Department.department,
                subquery.c.total.label("hired")
            )
            .join(subquery, subquery.c.department_id == models.Department.id)
            .filter(subquery.c.total > mean_val)
            .order_by(subquery.c.total.desc())
            .all()
        )

        return [
            {"id": r.id, "department": r.department, "hired": int(r.hired)}
            for r in results
        ]

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating report: {str(e)}")
