from typing import Optional, List
from sqlalchemy import String, Integer, DateTime, ForeignKey, text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base

class Department(Base):
    __tablename__ = "departments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=False)
    department: Mapped[str] = mapped_column(String, nullable=False, index=True)

    # Relationship with HiredEmployee
    employees: Mapped[List["HiredEmployee"]] = relationship(back_populates="department")


class Job(Base):
    __tablename__ = "jobs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=False)
    job: Mapped[str] = mapped_column(String, nullable=False, index=True)

    # Relationship with HiredEmployee
    employees: Mapped[List["HiredEmployee"]] = relationship(back_populates="job")


class HiredEmployee(Base):
    __tablename__ = "hired_employees"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=False)
    name: Mapped[str] = mapped_column(String, nullable=False)
    datetime: Mapped["datetime"] = mapped_column(DateTime(timezone=True), server_default=text("NOW()"))
    department_id: Mapped[int] = mapped_column(ForeignKey("departments.id"), index=True)
    job_id: Mapped[int] = mapped_column(ForeignKey("jobs.id"), index=True)

    # Relationships
    department: Mapped[Optional["Department"]] = relationship(back_populates="employees")
    job: Mapped[Optional["Job"]] = relationship(back_populates="employees")

