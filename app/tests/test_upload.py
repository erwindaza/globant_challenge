from io import BytesIO

def test_upload_departments(client):
    csv = b"id,department\n1,Supply Chain\n2,Maintenance\n3,Staff\n"
    r = client.post("/upload/departments", files={"file": ("departments.csv", BytesIO(csv), "text/csv")})
    assert r.status_code == 200
    assert r.json()["inserted"] == 3
