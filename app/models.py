from sqlmodel import SQLModel, Field, Column, Relationship
from sqlalchemy import String, Numeric
from typing import Optional, List
from decimal import Decimal

class UserLoanLink(SQLModel, table=True):
    user_id: Optional[int] = Field(default=None, foreign_key="user.id", primary_key=True)
    loan_id: Optional[int] = Field(default=None, foreign_key="loan.id", primary_key=True)

class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    email: str = Field(sa_column=Column(String, unique=True, index=True))
    first_name: str
    last_name: str
    # Creates User relationship to Loans
    loans: List["Loan"] = Relationship(back_populates="users", link_model=UserLoanLink)

class Loan(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    amount: Decimal = Field(sa_column=Column(Numeric(18, 6)))
    annual_interest_rate: Decimal = Field(sa_column=Column(Numeric(8, 5)))
    term_months: int
    # Creates Loan relationship to Users
    users: List["User"] = Relationship(back_populates="loans", link_model=UserLoanLink)
