from app.models import Loan

def amortization_schedule(loan: Loan):
  schedule = []
  i = loan.annual_interest_rate / 100 / 12
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

def loan_summary_for_month(month, loan: Loan):
  i = loan.annual_interest_rate / 100 / 12
  n = loan.term_months
  current_principal_balance = loan.amount
  monthly_payment = current_principal_balance * ((i * (1 + i) ** n) / ((1 + i) ** n - 1))
  total_payment_remaining = monthly_payment * n
  interest_paid_this_month = 0
  principal_already_paid = 0
  interest_already_paid = 0
  for m in range(1, month + 1):
    interest_paid_this_month = current_principal_balance * i
    principal_paid_this_month = monthly_payment - interest_paid_this_month
    principal_already_paid += principal_paid_this_month
    interest_already_paid += interest_paid_this_month
    current_principal_balance -= principal_paid_this_month
    total_payment_remaining -= monthly_payment
  return {
    "current principal balance": round(current_principal_balance, 2),
    "principal already paid": round(principal_already_paid, 2),
    "interest already paid": round(interest_already_paid, 2)
  }
