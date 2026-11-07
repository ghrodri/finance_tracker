import os
from datetime import date
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = Path(os.environ.get("WT_DB") or BASE_DIR / "wealth_tracker.db")
SQL_DIR = BASE_DIR / "sql"

# tracking starts here, there are no earlier months
START_MONTH = "2026-11"
START_DATE = date(2026, 11, 1)

MONTHS = [
    "January", "February", "March", "April", "May", "June",
    "July", "August", "September", "October", "November", "December",
]

TYPE_LABEL = {
    "savings": "Savings",
    "fixed": "Fixed deposit",
    "investment": "Investment",
    "pension": "Pension",
}
TYPE_OPTIONS = [
    {"label": "Savings account (compound, average daily balance)", "value": "savings"},
    {"label": "Fixed-term deposit (simple interest)", "value": "fixed"},
    {"label": "Investment (you log returns)", "value": "investment"},
    {"label": "Pension plan (you log returns)", "value": "pension"},
]
TYPE_COLOR = {
    "savings": "#2A9D8F",
    "fixed": "#1B3A6B",
    "investment": "#E9A23B",
    "pension": "#7B4FA3",
}

BASIS_OPTIONS = [
    {"label": "Daily balance x rate / 365", "value": "act365"},
    {"label": "Daily balance x rate / 360", "value": "act360"},
    {"label": "Average balance x rate / 12", "value": "avg12"},
]
BASIS_TEXT = {
    "act365": "daily balance x rate / 365",
    "act360": "daily balance x rate / 360",
    "avg12": "average balance x rate / 12",
}

KIND_LABEL = {
    "deposit": "Deposit",
    "withdrawal": "Withdrawal",
    "interest": "Interest / return",
    "fee": "Fee",
    "adjustment": "Adjustment (+/-)",
}
KIND_OPTIONS = [{"label": label, "value": kind} for kind, label in KIND_LABEL.items()]

EXPENSE_CATS = [
    "Housing", "Food", "Transport", "Health", "Pets",
    "Phone & internet", "Leisure", "Subscriptions", "Other",
]
INCOME_CATS = ["Salary", "Bonus", "Side income", "Other"]

SCREENS = ["overview", "cashflow", "accounts", "calculator", "data"]
SCREEN_NAME = {
    "overview": "Overview",
    "cashflow": "Cash flow",
    "accounts": "Accounts",
    "calculator": "Calculator",
    "data": "Data",
}
