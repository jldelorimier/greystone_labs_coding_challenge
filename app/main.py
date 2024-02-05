from fastapi import FastAPI, Depends, HTTPException, Path
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select
from contextlib import asynccontextmanager

from app.database import engine, SQLModel, get_db
from app.models import User, Loan
from app.financial_calculations import amortization_schedule

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
