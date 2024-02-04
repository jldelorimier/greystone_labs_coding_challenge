from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select
from contextlib import asynccontextmanager

from app.database import engine, SQLModel, get_db
from app.models import User

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
