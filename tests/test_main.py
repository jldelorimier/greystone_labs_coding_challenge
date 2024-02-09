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

# loan_schedule tests
def test_fetch_loan_schedule(session: Session, client: TestClient):
    test_loan = Loan(
        amount=Decimal(100000.000000), 
        annual_interest_rate=Decimal(12.00000), 
        term_months=6, user_id=1)
    session.add(test_loan)
    session.commit()

    response = client.get(f"/loan/{test_loan.id}/schedule")
    data = response.json()
    expected_loan_schedule = [
        {
            "Month": 1,
            "Remaining balance": 83745.16,
            "Monthly payment": 17254.84
        },
        {
            "Month": 2,
            "Remaining balance": 67327.78,
            "Monthly payment": 17254.84
        },
        {
            "Month": 3,
            "Remaining balance": 50746.22,
            "Monthly payment": 17254.84
        },
        {
            "Month": 4,
            "Remaining balance": 33998.84,
            "Monthly payment": 17254.84
        },
        {
            "Month": 5,
            "Remaining balance": 17084,
            "Monthly payment": 17254.84
        },
        {
            "Month": 6,
            "Remaining balance": 0,
            "Monthly payment": 17254.84
        }
    ]

    assert response.status_code == 200
    assert data == expected_loan_schedule

def test_fetch_loan_schedule_nonexistent_loan(client: TestClient):
    nonexistent_loan_id = 99

    response = client.get(f"/loan/{nonexistent_loan_id}/schedule")
    
    assert response.status_code == 404
    assert response.json()["detail"] == "Loan not found"

# loan_summary tests
def test_fetch_loan_summary(session: Session, client: TestClient):
    test_loan = Loan(
        amount=Decimal(100000.000000), 
        annual_interest_rate=Decimal(12.00000), 
        term_months=6, user_id=1)
    session.add(test_loan)
    session.commit()
    test_month = 5

    response = client.get(f"/loan/{test_loan.id}/summary/{test_month}")
    data = response.json()

    assert response.status_code == 200
    assert data == {
        "current principal balance": 17084,
        "principal already paid": 82916,
        "interest already paid": 3358.18
    }

def test_fetch_loan_summary_month_past_loan_term(session: Session, client: TestClient):
    test_loan = Loan(
        amount=Decimal(100000.000000), 
        annual_interest_rate=Decimal(12.00000), 
        term_months=6, user_id=1)
    session.add(test_loan)
    session.commit()
    test_month = 7

    response = client.get(f"/loan/{test_loan.id}/summary/{test_month}")

    assert response.status_code == 400
    assert response.json()["detail"] == f"Month must be less than or equal to the loan term of {test_loan.term_months} months"

def test_fetch_loan_summary_nonexistent_loan(client: TestClient):
    nonexistent_loan_id = 99
    month = 1

    response = client.get(f"/loan/{nonexistent_loan_id}/summary/{month}")

    assert response.status_code == 404
    assert response.json()["detail"] == "Loan not found"

# fetch_loans_for_user tests
def test_fetch_loans_for_user(session: Session, client: TestClient):
    # create user
    userB = User(name="test_userB@null.null", first_name="userB", last_name="lastnameB")
    session.add(userB)
    session.commit()
    # post request to create loan1 and corresponding UserLoanLink
    client.post(
        "/loans/", json={
            "amount": 100000,
            "annual_interest_rate": 12,
            "term_months": 6,
            "user_id": 1
        }
    )
    # post request to create loan2 and corresponding UserLoanLink
    client.post(
        "/loans/", json={
            "amount": 50000,
            "annual_interest_rate": 24,
            "term_months": 6,
            "user_id": 1
        }
    )

    response = client.get(
        f"/users/{userB.id}/loans"
    )
    data = response.json()

    assert response.status_code == 200
    assert data == [
        {
            "term_months": 6,
            "id": 1,
            "annual_interest_rate": "12.00000",
            "amount": "100000.000000"
        },
        {
            "term_months": 6,
            "id": 2,
            "annual_interest_rate": "24.00000",
            "amount": "50000.000000"
        }
    ]

def test_fetch_loans_for_nonexistent_user(client: TestClient):
    non_existent_user_id = 999

    response = client.get(f"/users/{non_existent_user_id}/loans")

    assert response.status_code == 404
    assert response.json()["detail"] == "User not found"

def test_fetch_loans_for_user_with_no_loans(session: Session, client: TestClient):
    # create user
    userB = User(name="test_userB@null.null", first_name="userB", last_name="lastnameB")
    session.add(userB)
    session.commit()

    response = client.get(
        f"/users/{userB.id}/loans"
    )
    data = response.json()

    assert response.status_code == 404
    assert response.json()["detail"] == f"No loans found for user with ID {userB.id}"

# share_loan tests
def test_share_loan(session: Session, client: TestClient):
    # create user
    userB = User(name="test_userB@null.null", first_name="userB", last_name="lastnameB")
    session.add(userB)
    session.commit()
    # create loan
    test_loan = Loan(
        amount=Decimal(100000.000000), 
        annual_interest_rate=Decimal(12.00000), 
        term_months=6, 
        user_id=userB.id)
    session.add(test_loan)
    session.commit()
    test_target_user_id = 1

    response = client.post(
        f"/loans/{test_loan.id}/share?target_user_id={test_target_user_id}"
    )
    data = response.json()

    assert response.status_code == 200
    assert data == {
        "message": "Loan shared successfully with user 1"
    }

def test_share_loan_with_nonexistent_loan(session: Session, client: TestClient):
    # create user
    userB = User(name="test_userB@null.null", first_name="userB", last_name="lastnameB")
    session.add(userB)
    session.commit()

    nonexistent_loan_id = 999
    test_target_user_id = 1

    response = client.post(f"/loans/{nonexistent_loan_id}/share?target_user_id={test_target_user_id}")

    assert response.status_code == 404
    assert response.json()["detail"] == "Loan not found"

def test_share_loan_with_nonexistent_target_user(session: Session, client: TestClient):
    # create user
    userB = User(name="test_userB@null.null", first_name="userB", last_name="lastnameB")
    session.add(userB)
    session.commit()
    # create loan
    test_loan = Loan(amount=Decimal(100000.000000), annual_interest_rate=Decimal(12.00000), term_months=6, user_id=userB.id)
    session.add(test_loan)
    session.commit()

    nonexistent_target_user_id = 999

    response = client.post(f"/loans/{test_loan.id}/share?target_user_id={nonexistent_target_user_id}")

    assert response.status_code == 404
    assert response.json()["detail"] == "Target user not found"

def test_share_loan_with_user_already_associated_with_loan(session: Session, client: TestClient):
    # create user
    userB = User(name="test_userB@null.null", first_name="userB", last_name="lastnameB")
    session.add(userB)
    session.commit()
    # create loan
    loan_data = {
        "amount": 1000,
        "annual_interest_rate": 5,
        "term_months": 12,
        "user_id": userB.id
    }
    loan_creation_response = client.post("/loans/", json=loan_data)
    test_loan_id = loan_creation_response.json()["id"]

    
    response = client.post(f"/loans/{test_loan_id}/share?target_user_id={userB.id}")

    assert response.status_code == 400
    assert response.json()["detail"] == "User is already associated with this loan"
