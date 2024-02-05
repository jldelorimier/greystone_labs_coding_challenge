from sqlmodel import SQLModel, Field, Column, Relationship
from sqlalchemy import String
from typing import Optional, List

class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    email: str = Field(sa_column=Column(String, unique=True, index=True))
    first_name: str
    last_name: str
    # Creates User relationship to Loan
    loans: List["Loan"] = Relationship(back_populates="user")

class Loan(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    amount: float
    interest_rate: float
    term_months: int
    # Creates Loan relationship to User
    user: Optional["User"] = Relationship(back_populates="loans")
    