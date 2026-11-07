import calendar

from config import START_MONTH
from utils import add_months, parse_ym


def simulate_savings(base, monthly, rate, years, deposit_day, basis=365.0):
    # same method as the savings accounts: daily balance, credited at month end
    balance = float(base)
    contributed = float(base)
    total_interest = 0.0
    out = []
    ym = START_MONTH
    for i in range(years * 12):
        ndays = calendar.monthrange(*parse_ym(ym))[1]
        day_of_deposit = min(max(deposit_day, 1), ndays)
        balance_sum = 0.0
        for day in range(1, ndays + 1):
            if day == day_of_deposit:
                balance += monthly
                contributed += monthly
            balance_sum += balance
        interest = round(balance_sum * rate / 100.0 / basis, 2)
        balance += interest
        total_interest += interest
        if (i + 1) % 12 == 0:
            out.append({
                "year": (i + 1) // 12,
                "contributed": contributed,
                "interest": total_interest,
                "balance": balance,
            })
        ym = add_months(ym, 1)
    return out
