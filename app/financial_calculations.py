from app.models import Loan
from decimal import Decimal

def amortization_schedule(loan: Loan):
  schedule = []
  i = loan.annual_interest_rate / Decimal("100") / Decimal("12")
  l = loan.amount
  n = loan.term_months
  monthly_payment = l * ((i * (Decimal("1") + i) ** n) / ((Decimal("1") + i) ** n - Decimal("1")))
  for m in range(1, n + 1):
    obj = {
        "Month": m,
        "Remaining balance": (l * (((Decimal("1") + i) ** n - (Decimal("1") + i) ** m) / ((Decimal("1") + i) ** n - Decimal("1")))).quantize(Decimal("1.00")),
        "Monthly payment": monthly_payment.quantize(Decimal("1.00")),
    }
    schedule.append(obj)
  return schedule

def loan_summary_for_month(month, loan: Loan):
  i = loan.annual_interest_rate / Decimal("100") / Decimal("12")
  n = loan.term_months
  current_principal_balance = loan.amount
  monthly_payment = current_principal_balance * ((i * (Decimal("1") + i) ** n) / ((Decimal("1") + i) ** n - Decimal("1")))

  total_payment_remaining = monthly_payment * n
  interest_paid_this_month = Decimal("0")
  principal_already_paid = Decimal("0")
  interest_already_paid = Decimal("0")

  for m in range(1, month + 1):
    interest_paid_this_month = current_principal_balance * i
    principal_paid_this_month = monthly_payment - interest_paid_this_month
    principal_already_paid += principal_paid_this_month
    interest_already_paid += interest_paid_this_month
    current_principal_balance -= principal_paid_this_month
    total_payment_remaining -= monthly_payment

  return {
    "current principal balance": current_principal_balance.quantize(Decimal("1.00")),
    "principal already paid": principal_already_paid.quantize(Decimal("1.00")),
    "interest already paid": interest_already_paid.quantize(Decimal("1.00"))
  }
