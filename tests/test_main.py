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

# create_loan tests
def test_create_loan(session: Session, client: TestClient): 
    userB = User(name="test_userB@null.null", first_name="userB", last_name="lastnameB")
    session.add(userB)
    session.commit()

    response = client.post(
        "/loans/", json={
            "amount": 1000,
            "annual_interest_rate": 24,
            "term_months": 36,
            "user_id": 1
        }
    )

    data = response.json()

    # Assert loan creation response
    assert response.status_code == 200
    assert data["amount"] == "{:.6f}".format(Decimal(1000))
    assert data["annual_interest_rate"] == "{:.5f}".format(Decimal(24))
    assert data["term_months"] == 36
    assert data ["id"] 

    # Fetch UserLoanLink to verify creation
    loan_id = data.get("id")
    user_loan_link_query = select(UserLoanLink).filter_by(user_id=userB.id, loan_id=loan_id)
    user_loan_link = session.exec(user_loan_link_query).first()

    assert user_loan_link is not None
    assert user_loan_link.user_id == userB.id
    assert user_loan_link.loan_id == loan_id

def test_create_loan_user_does_not_exist(client: TestClient):
    nonexistent_user_id = 999
    loan_data = {
        "amount": 1000,
        "annual_interest_rate": 5,
        "term_months": 12,
        "user_id": nonexistent_user_id
    }
    response = client.post("/loans/", json=loan_data)

    assert response.status_code == 404
    assert response.json()["detail"] == "User not found"
