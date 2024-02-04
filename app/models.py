from sqlmodel import SQLModel, Field, Column
from sqlalchemy import String
from typing import Optional

class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    email: str = Field(sa_column=Column(String, unique=True, index=True))
    first_name: str
    last_name: str

class Loan(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    amount: float
    interest_rate: float
    term_months: int