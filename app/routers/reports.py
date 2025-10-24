from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session
from ..database import get_session

router = APIRouter(prefix="/reports", tags=["reports"])

@router.get("/hires_by_quarter")
def hires_by_quarter(db: Session = Depends(get_session)):
    sql = text("""            SELECT d.department, j.job,
               SUM(CASE WHEN EXTRACT(QUARTER FROM h.datetime) = 1 THEN 1 ELSE 0 END) AS q1,
               SUM(CASE WHEN EXTRACT(QUARTER FROM h.datetime) = 2 THEN 1 ELSE 0 END) AS q2,
               SUM(CASE WHEN EXTRACT(QUARTER FROM h.datetime) = 3 THEN 1 ELSE 0 END) AS q3,
               SUM(CASE WHEN EXTRACT(QUARTER FROM h.datetime) = 4 THEN 1 ELSE 0 END) AS q4
        FROM hired_employees h
        JOIN departments d ON d.id = h.department_id
        JOIN jobs j ON j.id = h.job_id
        WHERE EXTRACT(YEAR FROM h.datetime) = 2021
        GROUP BY d.department, j.job
        ORDER BY d.department ASC, j.job ASC;
    """)
    res = db.execute(sql).mappings().all()
    return [dict(r) for r in res]

@router.get("/above_mean")
def above_mean(db: Session = Depends(get_session)):
    sql = text("""            WITH hires_2021 AS (
            SELECT department_id, COUNT(*) AS hired
            FROM hired_employees
            WHERE EXTRACT(YEAR FROM datetime) = 2021
            GROUP BY department_id
        ),
        avg_h AS (SELECT AVG(hired) AS mean_hired FROM hires_2021)
        SELECT d.id, d.department, h.hired
        FROM hires_2021 h
        JOIN departments d ON d.id = h.department_id
        WHERE h.hired > (SELECT mean_hired FROM avg_h)
        ORDER BY h.hired DESC;
    """)
    res = db.execute(sql).mappings().all()
    return [dict(r) for r in res]
