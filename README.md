# Finance Tracker

A simple personal finance tracker built with Python and Plotly Dash. Everything is stored locally in a SQLite file.

## Features

- Track income and expenses by month (one-time or monthly items)
- Savings, fixed deposit, investment and pension accounts
- Savings interest is compounded and calculated on the average daily balance of the month
- Log deposits, withdrawals, bank-reported interest, fees and adjustments
- Net worth over time and balance by account type
- Savings calculator
- CSV export

Tracking starts in November 2026.

## Setup

```
pip install -r requirements.txt
python app.py
```

The app opens at http://127.0.0.1:8050. The database `wealth_tracker.db` is created next to `config.py`.
Set the `WT_DB` environment variable to use another file.

## Project layout

```
app.py         entry point
config.py      constants
db.py          runs the queries in sql/
sql/           all SQL files
callbacks/     Dash callbacks
layouts.py     page layouts
assets/        CSS
```