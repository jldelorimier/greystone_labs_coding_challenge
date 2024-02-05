from app.models import Loan

def amortization_schedule(loan: Loan):
  schedule = []
  i = loan.interest_rate / 100 / 12
  l = loan.amount
  n = loan.term_months
  monthly_payment = l * ((i * (1 + i) ** n) / ((1 + i) ** n - 1))
  for m in range(1, n + 1):
    obj = {
        "Month": m,
        "Remaining balance": round(l * (((1 + i) ** n - (1 + i) ** m) / ((1 + i) ** n - 1)), 2),
        "Monthly payment": round(monthly_payment, 2),
    }
    schedule.append(obj)
  return schedule
