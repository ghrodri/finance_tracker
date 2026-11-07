from collections import defaultdict

import plotly.graph_objects as go
from dash import ALL, Input, Output, State, callback, ctx, dcc, html, no_update
from dash.exceptions import PreventUpdate

from callbacks.navigation import clicked
from components import base_fig, empty, graph, kpi
from config import BASIS_TEXT, KIND_LABEL, START_DATE, TYPE_COLOR, TYPE_LABEL
from db import execute, fetch
from statements import build_statement
from summary import month_summary
from utils import money, month_first, month_label, month_last, parse_amount, parse_iso

SOURCE_BADGE = {"auto": "Estimated from daily balance", "bank": "Reported by bank", "none": ""}


def account_table(s, ym):
    present = [(acc, rows[ym]) for acc, rows in s["sts"] if ym in rows]
    if not present:
        text = "No accounts yet. Add your first one below." if not s["sts"] else "None of your accounts has started by this month."
        return empty(text)
    head = html.Div(className="row ac-head head", children=[
        html.Span("Account"), html.Span("Opening", className="num"), html.Span("Deposits", className="num"),
        html.Span("Withdrawals", className="num"), html.Span("Interest / returns", className="num"),
        html.Span("Fees", className="num"), html.Span("Closing", className="num"), html.Span(),
    ])
    body = []
    tot = defaultdict(float)
    for acc, r in present:
        badge = SOURCE_BADGE[r["source"]]
        if r["source"] == "auto" and r["projected"]:
            badge = "Projected (month in progress)"
        for key in ("opening", "deposits", "withdrawals", "interest", "fees", "closing"):
            tot[key] += r[key]
        meta = [html.Span(TYPE_LABEL[acc["type"]], className=f"chip chip-{acc['type']}")]
        if acc["rate"]:
            meta.append(html.Span(f"{acc['rate']:g}%", className="muted small"))
        body.append(html.Div(className="row ac-row", children=[
            html.Div([
                html.Div(acc["name"], className="strong"),
                html.Div(meta),
                html.Div(acc["note"], className="muted small") if acc["note"] else None,
            ]),
            html.Span(money(r["opening"]), className="num"),
            html.Span(money(r["deposits"]), className="num"),
            html.Span(money(r["withdrawals"]), className="num"),
            html.Span([money(r["interest"]), html.Span(badge, className="badge")], className="num"),
            html.Span(money(r["fees"]), className="num"),
            html.Span(money(r["closing"]), className="num strong"),
            html.Button("×", id={"type": "acc-del", "id": acc["id"]}, n_clicks=0, className="icon-btn",
                        title="Delete account", **{"aria-label": f"Delete account {acc['name']}"}),
        ]))
    foot = html.Div(className="row ac-tot tot", children=[
        html.Span("Total"),
        html.Span(money(tot["opening"]), className="num"),
        html.Span(money(tot["deposits"]), className="num"),
        html.Span(money(tot["withdrawals"]), className="num"),
        html.Span(money(tot["interest"]), className="num"),
        html.Span(money(tot["fees"]), className="num"),
        html.Span(money(tot["closing"]), className="num"),
        html.Span(),
    ])
    return html.Div(className="scroll", children=html.Div(className="min900", children=[head] + body + [foot]))


def transaction_list(s, ym):
    names = {acc["id"]: acc["name"] for acc, _ in s["sts"]}
    txs = fetch("month_transactions", (month_first(ym).isoformat(), month_last(ym).isoformat()))
    txs = [t for t in txs if t["account_id"] in names]
    if not txs:
        return empty(f"No transactions in {month_label(ym)} yet.")
    rows = [html.Div(className="row tx-row head", children=[
        html.Span("Date"), html.Span("Account"), html.Span("Kind"), html.Span("Note"),
        html.Span("Amount", className="num"), html.Span(),
    ])]
    for t in txs:
        shown = t["amount"] if t["kind"] == "adjustment" else abs(t["amount"])
        rows.append(html.Div(className="row tx-row", children=[
            html.Span(t["date"]),
            html.Span(names[t["account_id"]], className="strong"),
            html.Span(KIND_LABEL[t["kind"]]),
            html.Span(t["note"], className="muted"),
            dcc.Input(id={"type": "tx-amt", "id": t["id"]}, type="text", value=f"{shown:.2f}",
                      debounce=True, className="cell-input", name="Amount"),
            html.Button("×", id={"type": "tx-del", "id": t["id"]}, n_clicks=0, className="icon-btn",
                        title="Delete transaction", **{"aria-label": "Delete transaction"}),
        ]))
    return html.Div(className="scroll", children=html.Div(className="min720", children=rows))


@callback(
    Output("tx-account", "options"), Output("tx-account", "value"),
    Output("ex-account", "options"), Output("ex-account", "value"),
    Input("rev", "data"), State("tx-account", "value"), State("ex-account", "value"),
)
def account_options(_rev, tx_val, ex_val):
    accounts = fetch("account_names")
    options = [{"label": a["name"], "value": a["id"]} for a in accounts]
    ids = [a["id"] for a in accounts]
    first = ids[0] if ids else None
    return options, tx_val if tx_val in ids else first, options, ex_val if ex_val in ids else first


@callback(
    Output("ac-kpis", "children"), Output("ac-table", "children"), Output("ac-txs", "children"),
    Input("month", "data"), Input("rev", "data"),
)
def render_accounts(ym, _rev):
    s = month_summary(ym)
    kpis = [
        kpi("Total balance", money(s["nw"]), f"at the end of {month_label(ym)}"),
        kpi("Moved this month", money(s["saved"]),
            f"{money(s['deposits'])} in, {money(s['withdrawals'])} out", "navy"),
        kpi("Interest / returns", money(s["interest"] - s["fees"]), "net of fees",
            "pos" if s["interest"] >= s["fees"] else "neg"),
    ]
    return kpis, account_table(s, ym), transaction_list(s, ym)


def explain_text(acc, r):
    if not (acc["type"] in ("savings", "fixed") and acc["rate"] > 0 and acc["auto_interest"]):
        return "Interest is not estimated for this account. Record returns and fees as transactions."
    parts = [
        f"Average daily balance over {r['days']} days: {money(r['avg'])}. "
        f"Estimated interest at {acc['rate']:g}% ({BASIS_TEXT[acc['basis']]}): {money(r['auto'])}."
    ]
    if r["source"] == "bank":
        parts.append(f"You recorded {money(r['manual'])} reported by the bank, which replaces the estimate "
                     f"(difference {money(r['manual'] - r['auto'])}).")
    if acc["type"] != "fixed":
        parts.append("Interest is credited on the last day of the month and added to the balance, "
                     "so it earns interest from next month.")
    else:
        parts.append("Interest is credited on the last day of the month and accrued separately "
                     "(simple interest, it does not compound).")
    if r["projected"]:
        parts.append("This month is still in progress, so the figure assumes no more movements.")
    return " ".join(parts)


@callback(
    Output("ac-explain", "children"),
    Input("ex-account", "value"), Input("month", "data"), Input("rev", "data"),
)
def render_explain(acc_id, ym, _rev):
    if acc_id is None:
        return empty("Add an account to see its interest calculation.")
    found = fetch("get_account", (acc_id,))
    if not found:
        raise PreventUpdate
    acc = found[0]
    rows = build_statement(acc, fetch("account_transactions", (acc_id,)), ym)
    r = rows.get(ym)
    if not r:
        return empty(f"{acc['name']} starts on {acc['open_date']}.")

    xs = [d for d, _ in r["daily"]]
    ys = [b for _, b in r["daily"]]
    fig = go.Figure()
    fig.add_scatter(x=xs, y=ys, mode="lines", line=dict(shape="hv", color=TYPE_COLOR[acc["type"]], width=3),
                    name="Daily balance", hovertemplate="Day %{x}: $%{y:,.2f}<extra></extra>")
    fig.add_hline(y=r["avg"], line=dict(color="#E9A23B", dash="dash"),
                  annotation_text=f"Average {money(r['avg'])}", annotation_position="top left")
    fig = base_fig(fig, 260)
    fig.update_xaxes(title="Day of month", dtick=2)
    low, high = min(ys + [r["avg"]]), max(ys + [r["avg"]])
    pad = max((high - low) * 0.2, 1)
    fig.update_yaxes(range=[max(0, low - pad), high + pad])
    return html.Div([graph(fig), html.Div(explain_text(acc, r), className="explain")])


@callback(
    Output("rev", "data", allow_duplicate=True), Output("tx-amount", "value"), Output("tx-note", "value"),
    Output("tx-msg", "children"), Output("tx-msg", "className"),
    Input("add-tx", "n_clicks"),
    State("tx-account", "value"), State("tx-date", "date"), State("tx-kind", "value"),
    State("tx-amount", "value"), State("tx-note", "value"), State("rev", "data"),
    prevent_initial_call=True,
)
def on_add_tx(n, acc_id, picked, kind, amount, note, rev):
    if not n:
        raise PreventUpdate

    def fail(text):
        return no_update, no_update, no_update, text, "msg err"

    if acc_id is None:
        return fail("Add an account first.")
    day = parse_iso(picked)
    if day is None:
        return fail("Pick a date.")
    amt = parse_amount(amount)
    if amt is None or amt == 0 or (kind != "adjustment" and amt < 0):
        return fail("Enter a non-zero amount." if kind == "adjustment" else "Enter an amount greater than zero.")
    found = fetch("get_account", (acc_id,))
    if not found:
        return fail("That account no longer exists.")
    earliest = max(START_DATE, parse_iso(found[0]["open_date"]))
    if day < earliest:
        return fail(f"The date must be on or after {earliest.isoformat()} (the account's opening date).")
    execute("insert_transaction", (acc_id, day.isoformat(), kind, round(amt, 2), (note or "").strip()))
    return rev + 1, "", "", f"Added {KIND_LABEL[kind].lower()} on {day.isoformat()}.", "msg ok"


@callback(
    Output("rev", "data", allow_duplicate=True),
    Input({"type": "tx-amt", "id": ALL}, "value"),
    State({"type": "tx-amt", "id": ALL}, "id"), State("rev", "data"),
    prevent_initial_call=True,
)
def on_edit_tx(values, ids, rev):
    if not ids:
        raise PreventUpdate
    stored = {t["id"]: t for t in fetch("all_transactions")}
    changed = invalid = False
    for value, comp_id in zip(values, ids):
        tx = stored.get(comp_id["id"])
        if tx is None:
            continue
        new = parse_amount(value)
        valid = new is not None and new != 0 and (tx["kind"] == "adjustment" or new > 0)
        current = tx["amount"] if tx["kind"] == "adjustment" else abs(tx["amount"])
        if not valid:
            invalid = True
        elif abs(new - current) >= 0.005:
            execute("update_transaction_amount", (round(new, 2), tx["id"]))
            changed = True
    if changed or invalid:
        return rev + 1
    raise PreventUpdate


@callback(
    Output("rev", "data", allow_duplicate=True),
    Input({"type": "tx-del", "id": ALL}, "n_clicks"), State("rev", "data"),
    prevent_initial_call=True,
)
def on_delete_tx(_clicks, rev):
    if not clicked():
        raise PreventUpdate
    execute("delete_transaction", (ctx.triggered_id["id"],))
    return rev + 1


@callback(
    Output("rev", "data", allow_duplicate=True), Output("af-name", "value"), Output("af-open", "value"),
    Output("af-rate", "value"), Output("af-note", "value"),
    Output("af-msg", "children"), Output("af-msg", "className"),
    Input("add-acc", "n_clicks"),
    State("af-name", "value"), State("af-type", "value"), State("af-open", "value"), State("af-date", "date"),
    State("af-rate", "value"), State("af-basis", "value"), State("af-note", "value"), State("af-auto", "value"),
    State("rev", "data"),
    prevent_initial_call=True,
)
def on_add_account(n, name, acc_type, opening, picked, rate, basis, note, auto, rev):
    if not n:
        raise PreventUpdate

    def fail(text):
        return (no_update,) * 5 + (text, "msg err")

    if not (name or "").strip():
        return fail("Give the account a name.")
    open_amt = parse_amount(opening) if (opening or "").strip() else 0.0
    if open_amt is None or open_amt < 0:
        return fail("The opening balance must be a number, zero or more.")
    rate_val = parse_amount(rate) if (rate or "").strip() else 0.0
    if rate_val is None or rate_val < 0 or rate_val > 100:
        return fail("The rate must be a number between 0 and 100.")
    day = parse_iso(picked)
    if day is None or day < START_DATE:
        return fail(f"The opening date must be {START_DATE.isoformat()} or later.")
    execute("insert_account", (
        name.strip(), acc_type, round(open_amt, 2), day.isoformat(), rate_val, basis,
        1 if auto else 0, (note or "").strip(),
    ))
    return rev + 1, "", "", "", "", f"Account '{name.strip()}' added.", "msg ok"


@callback(
    Output("confirm-acc", "displayed"), Output("pending-acc", "data"),
    Input({"type": "acc-del", "id": ALL}, "n_clicks"),
    prevent_initial_call=True,
)
def ask_delete_account(_clicks):
    if not clicked():
        raise PreventUpdate
    return True, ctx.triggered_id["id"]


@callback(
    Output("rev", "data", allow_duplicate=True), Output("pending-acc", "data", allow_duplicate=True),
    Input("confirm-acc", "submit_n_clicks"), State("pending-acc", "data"), State("rev", "data"),
    prevent_initial_call=True,
)
def delete_account(n, acc_id, rev):
    if not n or acc_id is None:
        raise PreventUpdate
    execute("delete_account_transactions", (acc_id,))
    execute("delete_account", (acc_id,))
    return rev + 1, None
