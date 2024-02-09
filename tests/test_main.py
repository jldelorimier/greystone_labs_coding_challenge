import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine, select
from sqlmodel.pool import StaticPool
from decimal import Decimal

from app.main import app, get_session
from app.models import User, Loan, UserLoanLink

@pytest.fixture(name="session")
def session_fixture():
    engine = create_engine(
      "sqlite://",
      connect_args={"check_same_thread": False}, 
      poolclass=StaticPool
    )
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session

@pytest.fixture(name="client")
def client_fixture(session: Session):
    def get_session_override():
        return session
    
    app.dependency_overrides[get_session] = get_session_override

    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()

# create_user tests
def test_create_user(client: TestClient):
    response = client.post(
        "/users/", json={
            "email": "test_userA@null.null", 
            "first_name": "userA", 
            "last_name": "LastnameA"
        }
    )
    
    data = response.json()

    assert response.status_code == 200
    assert data["email"] == "test_userA@null.null"
    assert data["first_name"] == "userA"
    assert data["last_name"] == "LastnameA"
    assert "id" in data

def test_create_user_duplicate_email(client: TestClient):
    user_data = {
        "email": "test_userA@null.null", 
        "first_name": "userA", 
        "last_name": "LastnameA"
    }
    first_request_response = client.post("/users/", json=user_data)
    assert first_request_response.status_code == 200
    second_request_response = client.post("/users/", json=user_data)
    assert second_request_response.status_code == 400
    assert second_request_response.json().get('detail') == "Email already exists"

