from io import BytesIO
import json

def seed(client):
    client.post("/upload/departments", files={"file": ("departments.csv", BytesIO(b"id,department\n1,Staff\n2,Supply Chain\n"))})
    client.post("/upload/jobs", files={"file": ("jobs.csv", BytesIO(b"id,job\n1,Recruiter\n2,Manager\n"))})
    hires = b"id,name,datetime,department_id,job_id\n1,A,2021-01-15T10:00:00Z,1,1\n2,B,2021-04-02T09:00:00Z,1,2\n3,C,2021-07-03T12:00:00Z,2,2\n4,D,2021-10-20T08:30:00Z,2,1\n"
    client.post("/upload/hired_employees", files={"file": ("hired.csv", BytesIO(hires))})

def test_reports(client):
    seed(client)
    r1 = client.get("/reports/hires_by_quarter")
    assert r1.status_code == 200
    rows = r1.json()
    assert any(row["q1"] == 1 for row in rows)
    r2 = client.get("/reports/above_mean")
    assert r2.status_code == 200
    assert isinstance(r2.json(), list)
