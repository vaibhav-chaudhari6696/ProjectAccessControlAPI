from fastapi.testclient import TestClient
import pytest
from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool
from ..main import app
from ..db.session import get_session
from ..models.user import UserRole

SQLALCHEMY_DATABASE_URL = "sqlite://"

@pytest.fixture
def session():
    engine = create_engine(
        SQLALCHEMY_DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session

@pytest.fixture
def client(session):
    def get_session_override():
        return session

    app.dependency_overrides[get_session] = get_session_override
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()

def test_register_user(client):
    response = client.post(
        "/api/v1/register",
        json={
            "username": "testuser",
            "email": "test@example.com",
            "password": "testpass123",
            "role": UserRole.USER
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "testuser"
    assert data["email"] == "test@example.com"
    assert "hashed_password" not in data

def test_login_user(client):
    # First register a user
    client.post(
        "/api/v1/register",
        json={
            "username": "testuser",
            "email": "test@example.com",
            "password": "testpass123",
            "role": UserRole.USER
        },
    )
    
    # Then try to login
    response = client.post(
        "/api/v1/login",
        data={
            "username": "testuser",
            "password": "testpass123"
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer" 