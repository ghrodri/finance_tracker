from datetime import date

from dash import dcc, html

from components import card, field
from config import (
    BASIS_OPTIONS, DB_PATH, EXPENSE_CATS, KIND_OPTIONS, SCREEN_NAME, SCREENS,
    START_DATE, TYPE_OPTIONS,
)
from utils import current_month


def layout_overview():
    return html.Div(id="page-overview", className="page", children=[
        html.Div(id="ov-kpis", className="grid-kpi"),
        html.Div(className="row2", children=[
            card("Net worth over time", "Last 6 months, up to the selected month",
                 [html.Div(id="ov-nw")], cls="grow2"),
            card("Where your money is", "Balance by account type", [html.Div(id="ov-donut")], cls="grow1"),
        ]),
        card("Where your income goes", "Expenses, money moved to accounts and what is left", [html.Div(id="ov-split")]),
        card("Expenses by category", None, [html.Div(id="ov-cats")]),
    ])


def layout_cashflow():
    form = card("Add income or expense", None, [
        dcc.RadioItems(
            id="ef-kind",
            options=[{"label": "Expense", "value": "expense"}, {"label": "Income", "value": "income"}],
            value="expense", inline=True, className="seg",
        ),
        field("Name", dcc.Input(id="ef-name", type="text", placeholder="e.g. Groceries", value="")),
        field("Amount ($)", dcc.Input(id="ef-amount", type="text", placeholder="0.00", value="")),
        field("Category", dcc.Dropdown(id="ef-cat", options=EXPENSE_CATS, value="Food", clearable=False)),
        dcc.Checklist(id="ef-rec", options=[{"label": " Repeats every month", "value": "yes"}], value=["yes"]),
        html.Button("Add to selected month", id="add-entry", n_clicks=0, className="btn btn-primary"),
        html.Div(id="ef-msg", className="msg"),
        html.P("Monthly items carry forward. Changing or removing one applies from the selected month onward; "
               "earlier months keep their history.", className="note"),
    ], cls="side-form")
    return html.Div(id="page-cashflow", className="page", children=[
        html.Div(id="cf-kpis", className="grid-kpi"),
        html.Div(className="row2", children=[
            form,
            html.Div(className="fill", children=[
                card("Income", None, [html.Div(id="cf-income")]),
                card("Expenses", None, [html.Div(id="cf-expenses")]),
            ]),
        ]),
    ])


def layout_accounts():
    default_date = max(date.today(), START_DATE)
    tx_form = card("Add a transaction", "Deposits and withdrawals are weighted by the days they stay in the account.", [
        html.Div(className="formgrid", children=[
            field("Account", dcc.Dropdown(id="tx-account", options=[], value=None, clearable=False,
                                          placeholder="Add an account first")),
            field("Date", dcc.DatePickerSingle(id="tx-date", date=default_date, min_date_allowed=START_DATE,
                                               display_format="YYYY-MM-DD")),
            field("Kind", dcc.Dropdown(id="tx-kind", options=KIND_OPTIONS, value="deposit", clearable=False)),
            field("Amount ($)", dcc.Input(id="tx-amount", type="text", placeholder="0.00", value="")),
            field("Note (optional)", dcc.Input(id="tx-note", type="text", placeholder="e.g. 15th payroll", value="")),
        ]),
        html.Div(html.Button("Add transaction", id="add-tx", n_clicks=0, className="btn btn-primary")),
        html.Div(id="tx-msg", className="msg"),
        html.P('Use "Interest / return" to record what your bank actually paid. It replaces the estimate for that month. '
               "Use Adjustment (+/-) to fix a balance that does not match your statement.", className="note"),
    ])
    acc_form = card("Add an account", None, [
        html.Div(className="formgrid", children=[
            field("Name", dcc.Input(id="af-name", type="text", placeholder="e.g. Emergency fund", value="")),
            field("Type", dcc.Dropdown(id="af-type", options=TYPE_OPTIONS, value="savings", clearable=False)),
            field("Opening balance ($)", dcc.Input(id="af-open", type="text", placeholder="0.00", value="")),
            field("Opening date", dcc.DatePickerSingle(id="af-date", date=START_DATE, min_date_allowed=START_DATE,
                                                       display_format="YYYY-MM-DD")),
            field("Annual rate % (optional)", dcc.Input(id="af-rate", type="text", placeholder="e.g. 4", value="")),
            field("Interest method", dcc.Dropdown(id="af-basis", options=BASIS_OPTIONS, value="act365",
                                                  clearable=False)),
            field("Notes (optional)", dcc.Input(id="af-note", type="text", placeholder="e.g. matures May 2032",
                                                value="")),
        ]),
        dcc.Checklist(
            id="af-auto",
            options=[{"label": " Estimate interest automatically (savings and fixed deposits)", "value": "yes"}],
            value=["yes"],
        ),
        html.Div(html.Button("Add account", id="add-acc", n_clicks=0, className="btn btn-primary")),
        html.Div(id="af-msg", className="msg"),
    ])
    return html.Div(id="page-accounts", className="page", children=[
        html.Div(id="ac-kpis", className="grid-kpi"),
        card("Accounts this month", "Opening, movements and closing balance. Interest compounds into the next month.",
             [html.Div(id="ac-table")]),
        card("How the interest was calculated", None, [
            field("Account", dcc.Dropdown(id="ex-account", options=[], value=None, clearable=False,
                                          placeholder="Add an account first")),
            html.Div(id="ac-explain"),
        ]),
        tx_form,
        card("Transactions this month", None, [html.Div(id="ac-txs")]),
        acc_form,
        dcc.ConfirmDialog(id="confirm-acc", message="Delete this account and all of its transactions?"),
    ])


def layout_calculator():
    return html.Div(id="page-calculator", className="page", children=[
        html.Div(className="row2", children=[
            card("Your scenario", None, [
                field("Starting balance ($)", dcc.Input(id="c-base", type="text", placeholder="0.00", value="")),
                field("Monthly deposit ($)", dcc.Input(id="c-monthly", type="text", placeholder="0.00", value="")),
                field("Annual interest rate (%)", dcc.Input(id="c-rate", type="text", placeholder="0.0", value="")),
                field("Years (1 to 40)", dcc.Input(id="c-years", type="text", placeholder="5", value="")),
                field("Deposit day of the month", dcc.Input(id="c-day", type="text", placeholder="15", value="15")),
                html.P("Starts in November 2026. Interest uses the average daily balance (daily balance x rate / 365), "
                       "credited at month end and compounded, like the savings accounts above.", className="note"),
            ], cls="side-form"),
            html.Div(className="fill", id="calc-out"),
        ]),
    ])


def layout_data():
    return html.Div(id="page-data", className="page", children=[
        card("Your data", "Everything is stored locally in a SQLite file.", [
            html.Div(f"Database file: {DB_PATH}", className="explain"),
            html.Div(className="formgrid", children=[
                html.Button("Export accounts (CSV)", id="exp-accounts", n_clicks=0, className="btn"),
                html.Button("Export transactions (CSV)", id="exp-tx", n_clicks=0, className="btn"),
                html.Button("Export income and expenses (CSV)", id="exp-entries", n_clicks=0, className="btn"),
            ]),
            html.P("To back up, copy the .db file while the app is closed.", className="note"),
        ]),
    ])


def serve_layout():
    return html.Div(className="app", children=[
        dcc.Store(id="screen", data="overview"),
        dcc.Store(id="month", data=current_month()),
        dcc.Store(id="rev", data=0),
        dcc.Store(id="pending-acc", data=None),
        dcc.Download(id="download"),
        html.Aside(className="side", children=[
            html.Div(className="brand", children=[
                html.Div("W", className="logo"),
                html.Div([html.Div("Wealth Tracker", className="brand-name"),
                          html.Div("Personal finance", className="brand-sub")]),
            ]),
            html.Nav(className="nav", children=[
                html.Button(SCREEN_NAME[k], id=f"nav-{k}", n_clicks=0, className="nav-btn") for k in SCREENS
            ]),
            html.Div(className="side-note", children=[
                html.Div("Local and private", className="side-note-title"),
                "Your data stays in a file on this computer. Tracking starts in November 2026.",
            ]),
        ]),
        html.Main(className="main", children=[
            html.Header(className="hdr", children=[
                html.Div([html.H1(id="hdr-title", className="h1"), html.P(id="hdr-sub", className="hdr-sub")]),
                html.Div(id="month-bar", className="mbar", children=[
                    html.Button("<", id="m-prev", n_clicks=0, className="btn", **{"aria-label": "Previous month"}),
                    html.Div(id="m-label", className="mlabel"),
                    html.Button(">", id="m-next", n_clicks=0, className="btn", **{"aria-label": "Next month"}),
                ]),
            ]),
            layout_overview(), layout_cashflow(), layout_accounts(), layout_calculator(), layout_data(),
        ]),
    ])
