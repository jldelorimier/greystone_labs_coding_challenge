# Pydantic models for validating request data and serializing response data
from pydantic import BaseModel

class LoanCreateRequest(BaseModel):
    user_id: int
    amount: float
    interest_rate: float
    term_months: int
    