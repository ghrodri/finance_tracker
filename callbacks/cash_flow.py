from dash import ALL, Input, Output, State, callback, ctx, dcc, html, no_update
from dash.exceptions import PreventUpdate

from callbacks.navigation import clicked
from components import empty, kpi
from config import EXPENSE_CATS, INCOME_CATS
from entries import add_entry, entries_for_month, remove_entry, update_entry_amount
from summary import month_summary
from utils import money, month_label, parse_amount


def entry_rows(items, empty_text):
    if not items:
        return empty(empty_text)
    rows = []
    for e in items:
        repeat = "Every month" if e["recurring"] else "This month only"
        rows.append(html.Div(className="row cf-row", children=[
            html.Div([
                html.Div(e["name"], className="strong"),
                html.Div(f"{e['category']} · {repeat}", className="muted small"),
            ]),
            dcc.Input(id={"type": "ent-amt", "id": e["id"]}, type="text", value=f"{e['amount']:.2f}",
                      debounce=True, className="cell-input", name=f"Amount for {e['name']}"),
            html.Button("×", id={"type": "ent-del", "id": e["id"]}, n_clicks=0, className="icon-btn",
                        title="Remove from this month onward", **{"aria-label": f"Remove {e['name']}"}),
        ]))
    return html.Div(className="scroll", children=html.Div(className="min560", children=rows))


@callback(
    Output("cf-kpis", "children"), Output("cf-income", "children"), Output("cf-expenses", "children"),
    Input("month", "data"), Input("rev", "data"),
)
def render_cashflow(ym, _rev):
    s = month_summary(ym)
    incomes = [e for e in s["entries"] if e["kind"] == "income"]
    expenses = [e for e in s["entries"] if e["kind"] == "expense"]
    left = s["left"]
    kpis = [
        kpi("Income", money(s["income"]), f"{len(incomes)} item(s)", "pos"),
        kpi("Expenses", money(s["expenses"]), f"{len(expenses)} item(s)"),
        kpi("Moved to accounts", money(s["saved"]), "deposits minus withdrawals", "navy"),
        kpi("Left unallocated", money(left), "Over budget" if left < 0 else "Available to save or spend",
            "neg" if left < 0 else ""),
    ]
    income_list = entry_rows(
        incomes, f"No income added for {month_label(ym)}. Add your salary or other income on the left.")
    expense_list = entry_rows(
        expenses, f"No expenses added for {month_label(ym)}. Add rent, food, gas, subscriptions...")
    return kpis, income_list, expense_list


@callback(Output("ef-cat", "options"), Output("ef-cat", "value"), Input("ef-kind", "value"))
def kind_changed(kind):
    cats = INCOME_CATS if kind == "income" else EXPENSE_CATS
    return cats, cats[0] if kind == "income" else "Food"


@callback(
    Output("rev", "data", allow_duplicate=True), Output("ef-name", "value"), Output("ef-amount", "value"),
    Output("ef-msg", "children"), Output("ef-msg", "className"),
    Input("add-entry", "n_clicks"),
    State("ef-kind", "value"), State("ef-name", "value"), State("ef-amount", "value"), State("ef-cat", "value"),
    State("ef-rec", "value"), State("month", "data"), State("rev", "data"),
    prevent_initial_call=True,
)
def on_add_entry(n, kind, name, amount, cat, rec, ym, rev):
    if not n:
        raise PreventUpdate
    amt = parse_amount(amount)
    if not (name or "").strip() or amt is None or amt <= 0:
        return no_update, no_update, no_update, "Enter a name and an amount greater than zero.", "msg err"
    add_entry(kind, name.strip(), cat, amt, ym, bool(rec))
    return rev + 1, "", "", f"Added to {month_label(ym)}.", "msg ok"


@callback(
    Output("rev", "data", allow_duplicate=True),
    Input({"type": "ent-amt", "id": ALL}, "value"),
    State({"type": "ent-amt", "id": ALL}, "id"), State("month", "data"), State("rev", "data"),
    prevent_initial_call=True,
)
def on_edit_entry(values, ids, ym, rev):
    if not ids:
        raise PreventUpdate
    stored = {e["id"]: e["amount"] for e in entries_for_month(ym)}
    changed = invalid = False
    for value, comp_id in zip(values, ids):
        current = stored.get(comp_id["id"])
        if current is None:
            continue
        new = parse_amount(value)
        if new is None or new <= 0:
            invalid = True
        elif abs(new - current) >= 0.005:
            update_entry_amount(comp_id["id"], ym, new)
            changed = True
    # a bad value also refreshes so the old amount comes back
    if changed or invalid:
        return rev + 1
    raise PreventUpdate


@callback(
    Output("rev", "data", allow_duplicate=True),
    Input({"type": "ent-del", "id": ALL}, "n_clicks"),
    State("month", "data"), State("rev", "data"),
    prevent_initial_call=True,
)
def on_delete_entry(_clicks, ym, rev):
    if not clicked():
        raise PreventUpdate
    remove_entry(ctx.triggered_id["id"], ym)
    return rev + 1
