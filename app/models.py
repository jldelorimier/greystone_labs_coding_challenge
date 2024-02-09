from sqlmodel import SQLModel, Field, Column, Relationship
from sqlalchemy import String, Numeric
from typing import Optional, List
from decimal import Decimal
from pydantic import EmailStr

class UserLoanLink(SQLModel, table=True):
    user_id: Optional[int] = Field(default=None, foreign_key="user.id", primary_key=True)
    loan_id: Optional[int] = Field(default=None, foreign_key="loan.id", primary_key=True)

# User Models:
class UserBase(SQLModel):
    email: EmailStr = Field(sa_column=Column(String, unique=True, index=True))
    first_name: str
    last_name: str

class User(UserBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    loans: List["Loan"] = Relationship(back_populates="users", link_model=UserLoanLink)

class UserCreate(UserBase):
    pass
    
class UserRead(UserBase):
    id: int

# Loan Models:
class LoanBase(SQLModel):
    amount: Decimal = Field(sa_column=Column(Numeric(18, 6)))
    annual_interest_rate: Decimal = Field(sa_column=Column(Numeric(8, 5)))
    term_months: int
    
class Loan(LoanBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    users: List["User"] = Relationship(back_populates="loans", link_model=UserLoanLink)

class LoanCreate(LoanBase):
    user_id: int

class LoanRead(LoanBase):
    id: int
