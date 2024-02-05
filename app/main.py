from fastapi import FastAPI, Depends, HTTPException, Path
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select
from typing import List
from contextlib import asynccontextmanager

from app.database import engine, SQLModel, get_db
from app.models import User, Loan
from app.financial_calculations import amortization_schedule, loan_summary_for_month

@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as connection:
        await connection.run_sync(SQLModel.metadata.create_all)
    yield

app = FastAPI(lifespan=lifespan)

@app.get("/")
def read_root():
    return {"message": "Welcome to my app"}

@app.post("/users/", response_model=User)
async def create_user(user: User, db: AsyncSession = Depends(get_db)):
    statement = select(User).where(User.email == user.email)
    result = await db.execute(statement)
    existing_user = result.scalars().first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already exists")

    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user

@app.post("/loans/")
async def create_loan(loan: Loan, db: AsyncSession = Depends(get_db)):
    db.add(loan)
    await db.commit()
    await db.refresh(loan)
    return loan

@app.get("/loan/{loan_id}/schedule")
async def fetch_loan_schedule(loan_id: int = Path(..., description="The ID of the loan to fetch the schedule for"), db: AsyncSession = Depends(get_db)):
    loan = await db.get(Loan, loan_id)
    if not loan:
        raise HTTPException(status_code=404, detail="Loan not found")
    schedule = amortization_schedule(loan)
    return schedule

@app.get("/loan/{loan_id}/summary/{month}")
async def fetch_loan_summary(loan_id: int = Path(..., description="The ID of the loan to fetch the summary for"),
                             month: int = Path(..., ge=1, description="The month number to fetch the summary for"), 
                             db: AsyncSession = Depends(get_db)):
    loan = await db.get(Loan, loan_id)
    if not loan:
        raise HTTPException(status_code=404, detail="Loan not found")
    if month > loan.term_months:
        raise HTTPException(status_code=400, detail=f"Month must be less than or equal to the loan term of {loan.term_months} months")
    loan_summary = loan_summary_for_month(month, loan)
    return loan_summary

@app.get("/users/{user_id}/loans", response_model=List[Loan])
async def fetch_loans_for_user(user_id: int, db: AsyncSession = Depends(get_db)): 
    user = await db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    find_loans_by_user_id = select(Loan).where(Loan.user_id == user_id)
    query_result = await db.execute(find_loans_by_user_id)
    loans = query_result.scalars().all()
    if not loans:
        raise HTTPException(status_code=404, detail=f"No loans found for user with ID {user_id}")
    return loans
