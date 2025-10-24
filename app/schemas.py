from datetime import datetime
from pydantic import BaseModel, ConfigDict
from typing import List, Optional

# Base schema used by other models
class DepartmentBase(BaseModel):
    id: int
    department: str

class JobBase(BaseModel):
    id: int
    job: str

class HiredEmployeeBase(BaseModel):
    id: int
    name: str
    datetime: datetime
    department_id: int
    job_id: int

# Input schema for batch inserts
class BatchHiresIn(BaseModel):
    rows: List[HiredEmployeeBase]

# Response schemas
class DepartmentOut(DepartmentBase):
    model_config = ConfigDict(from_attributes=True)

class JobOut(JobBase):
    model_config = ConfigDict(from_attributes=True)

class HiredEmployeeOut(HiredEmployeeBase):
    model_config = ConfigDict(from_attributes=True)
    department: Optional[DepartmentOut] = None
    job: Optional[JobOut] = None

# -------- NUEVO: respuestas para los reportes --------
class ReportByQuarter(BaseModel):
    department: str
    job: str
    Q1: int
    Q2: int
    Q3: int
    Q4: int

class AboveMeanOut(BaseModel):
    id: int
    department: str
    hired: int
