import os
import tempfile
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.database import Base
from app.database import get_session

@pytest.fixture(scope="session")
def db_engine():
    # Use SQLite for tests (in-memory file for reliability)
    fd, path = tempfile.mkstemp()
    os.close(fd)
    url = f"sqlite+pysqlite:///{path}"
    engine = create_engine(url, future=True)
    Base.metadata.create_all(engine)
    yield engine
    engine.dispose()
    os.remove(path)

@pytest.fixture()
def db_session(db_engine):
    TestingSessionLocal = sessionmaker(bind=db_engine, autoflush=False, autocommit=False, expire_on_commit=False, future=True)
    db = TestingSessionLocal()
    yield db
    db.close()

@pytest.fixture()
def client(db_session, monkeypatch):
    def _get_session_override():
        try:
            yield db_session
        finally:
            pass
    monkeypatch.setattr("app.database.get_session", _get_session_override)
    return TestClient(app)
