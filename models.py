from pydantic import BaseModel
from typing import Optional

class User(BaseModel):
    id: int
    email: str
    first_name: str
    last_name: str

class Loan(BaseModel):
    id: int
    user_id: int
    amount: float
    interest_rate: float
    term_months: int