from fastapi.testclient import TestClient
import pytest
from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool
from ..main import app
from ..db.session import get_session
from ..models.user import User, UserRole
from ..core.security import get_password_hash

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

@pytest.fixture
def admin_token(client, session):
    # Create admin user
    admin = User(
        username="admin",
        email="admin@example.com",
        hashed_password=get_password_hash("admin123"),
        role=UserRole.ADMIN
    )
    session.add(admin)
    session.commit()
    
    # Login and get token
    response = client.post(
        "/api/v1/login",
        data={
            "username": "admin",
            "password": "admin123"
        }
    )
    return response.json()["access_token"]

@pytest.fixture
def user_token(client, session):
    # Create regular user
    user = User(
        username="user",
        email="user@example.com",
        hashed_password=get_password_hash("user123"),
        role=UserRole.USER
    )
    session.add(user)
    session.commit()
    
    # Login and get token
    response = client.post(
        "/api/v1/login",
        data={
            "username": "user",
            "password": "user123"
        }
    )
    return response.json()["access_token"]

def test_create_project_admin(client, admin_token):
    response = client.post(
        "/api/v1/projects",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={
            "name": "Test Project",
            "description": "A test project"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Test Project"
    assert data["description"] == "A test project"

def test_create_project_user(client, user_token):
    response = client.post(
        "/api/v1/projects",
        headers={"Authorization": f"Bearer {user_token}"},
        json={
            "name": "Test Project",
            "description": "A test project"
        }
    )
    assert response.status_code == 403

def test_list_projects(client, admin_token, user_token):
    # Create a project as admin
    client.post(
        "/api/v1/projects",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={
            "name": "Test Project",
            "description": "A test project"
        }
    )
    
    # List projects as user
    response = client.get(
        "/api/v1/projects",
        headers={"Authorization": f"Bearer {user_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["name"] == "Test Project" 