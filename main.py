from contextlib import asynccontextmanager
from fastapi import FastAPI
from database import engine, SQLModel, AsyncSessionLocal

@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as connection:
        await connection.run_sync(SQLModel.metadata.create_all)
    yield

app = FastAPI(lifespan=lifespan)

async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()

@app.get("/")
def read_root():
    return {"message": "Welcome to my app"}
