from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from ..database import get_session
from .. import models
from ..schemas import BatchHiresIn

router = APIRouter(prefix="/batch", tags=["batch"])

@router.post("/hired_employees")
async def batch_hires(payload: BatchHiresIn, db: Session = Depends(get_session)):
    try:
        rows = [row.model_dump() for row in payload.rows]
        db.bulk_insert_mappings(models.HiredEmployee, rows)
        db.commit()
        return {"inserted": len(rows)}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
