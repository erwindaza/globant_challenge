import io
import pandas as pd
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from sqlalchemy.orm import Session
from ..database import get_session
from .. import models

router = APIRouter(prefix="/upload", tags=["upload"])

MODEL_MAP = {
    "departments": models.Department,
    "jobs": models.Job,
    "hired_employees": models.HiredEmployee,
}

@router.post("/{table_name}")
async def upload_csv(table_name: str, file: UploadFile = File(...), db: Session = Depends(get_session)):
    if table_name not in MODEL_MAP:
        raise HTTPException(status_code=400, detail="Invalid table name")
    try:
        content = await file.read()
        df = pd.read_csv(io.BytesIO(content))
        # Normalize columns
        df.columns = [c.strip() for c in df.columns]
        if "datetime" in df.columns:
            df["datetime"] = pd.to_datetime(df["datetime"], utc=True, errors="coerce")
        records = df.to_dict(orient="records")
        batch_size = 1000
        inserted = 0
        Model = MODEL_MAP[table_name]
        for i in range(0, len(records), batch_size):
            batch = records[i:i+batch_size]
            db.bulk_insert_mappings(Model, batch)
            db.commit()
            inserted += len(batch)
        return {"table": table_name, "inserted": inserted}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
