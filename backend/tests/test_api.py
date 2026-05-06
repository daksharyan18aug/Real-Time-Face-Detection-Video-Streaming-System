import pytest
import os
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Use SQLite for tests — no Docker/PostgreSQL needed
os.environ["DATABASE_URL"] = "sqlite:///./test.db"

from app.database import Base, get_db
from app.main import app

# Create a test SQLite engine
TEST_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(
    autocommit=False, autoflush=False, bind=engine
)

# Create all tables in test DB
Base.metadata.create_all(bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


# Override the DB dependency
app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)


def test_health_check():
    """Health endpoint should return 200 with status ok."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_roi_endpoint_missing_session_id():
    """GET /roi without session_id should return 422."""
    response = client.get("/roi")
    assert response.status_code == 422


def test_roi_endpoint_invalid_session():
    """GET /roi with unknown session_id should return 404."""
    response = client.get("/roi?session_id=nonexistent-session-123")
    assert response.status_code == 404


def test_websocket_connects():
    """WebSocket should accept connection."""
    with client.websocket_connect("/ws/stream") as websocket:
        assert websocket is not None