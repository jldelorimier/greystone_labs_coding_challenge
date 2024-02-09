from fastapi import FastAPI, Depends, HTTPException, Path
from sqlmodel import select, Session
from typing import List

from app.database import create_db_and_tables, get_session
from app.models import User, UserCreate, UserRead, Loan, LoanCreate, LoanRead, UserLoanLink
from app.financial_calculations import amortization_schedule, loan_summary_for_month

app = FastAPI()

@app.on_event("startup")
def on_startup():
    create_db_and_tables()

@app.post("/users/", response_model=UserRead)
def create_user(user: UserCreate, session: Session = Depends(get_session)):
    # check if user email already exists
    statement = select(User).where(User.email == user.email)
    result = session.execute(statement)
    existing_user = result.scalars().first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already exists")
    # assuming email doesn't already exist, add the user to the db:
    db_user = User.model_validate(user)
    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    return db_user

@app.post("/loans/", response_model=LoanRead)
def create_loan(loan_create: LoanCreate, session: Session = Depends(get_session)):
    # check that the User for whom the loan is being created exists
    user = session.get(User, loan_create.user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    # Create and add the new loan to the session
    loan = Loan(
        amount=loan_create.amount, 
        annual_interest_rate=loan_create.annual_interest_rate, 
        term_months=loan_create.term_months)
    db_loan = Loan.model_validate(loan)
    session.add(db_loan)
    session.commit()
    session.refresh(db_loan)
    # Link the loan to the user
    loan_user_record = UserLoanLink(
        user_id=loan_create.user_id, 
        loan_id=db_loan.id)
    session.add(loan_user_record)
    session.commit()

    return db_loan

@app.get("/loan/{loan_id}/schedule")
def fetch_loan_schedule(
    loan_id: int = Path(..., description="The ID of the loan to fetch the schedule for"), 
    session: Session = Depends(get_session)):
    loan = session.get(Loan, loan_id)
    if not loan:
        raise HTTPException(status_code=404, detail="Loan not found")
    schedule = amortization_schedule(loan)
    return schedule

@app.get("/loan/{loan_id}/summary/{month}")
def fetch_loan_summary(loan_id: int = Path(..., description="The ID of the loan to fetch the summary for"),
                       month: int = Path(..., ge=1, description="The month number to fetch the summary for"), 
                       session: Session = Depends(get_session)):
    loan = session.get(Loan, loan_id)
    if not loan:
        raise HTTPException(status_code=404, detail="Loan not found")
    if month > loan.term_months:
        raise HTTPException(status_code=400, detail=f"Month must be less than or equal to the loan term of {loan.term_months} months")
    loan_summary = loan_summary_for_month(month, loan)
    return loan_summary

@app.get("/users/{user_id}/loans", response_model=List[Loan])
def fetch_loans_for_user(user_id: int, session: Session = Depends(get_session)): 
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    find_loans_by_user_id = select(Loan).join(UserLoanLink).where(UserLoanLink.user_id == user_id)
    query_result = session.execute(find_loans_by_user_id)
    loans = query_result.scalars().all()
    if not loans:
        raise HTTPException(status_code=404, detail=f"No loans found for user with ID {user_id}")
    return loans

@app.post("/loans/{loan_id}/share")
def share_loan(loan_id: int, target_user_id: int, session: Session = Depends(get_session)):
    loan = session.get(Loan, loan_id)
    if not loan:
        raise HTTPException(status_code=404, detail="Loan not found")
    target_user = session.get(User, target_user_id)
    if not target_user:
        raise HTTPException(status_code=404, detail="Target user not found")
    # check if User is already associated with Loan
    existing_link_query = select(UserLoanLink).filter_by(user_id=target_user_id, loan_id=loan_id)
    existing_link = session.execute(existing_link_query).first()
    if existing_link:
        raise HTTPException(status_code=400, detail="User is already associated with this loan")
    
    loan_user_association = UserLoanLink(user_id=target_user_id, loan_id=loan_id)
    session.add(loan_user_association)
    session.commit()
    return {"message": f"Loan shared successfully with user {target_user_id}"}
