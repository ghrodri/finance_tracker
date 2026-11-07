from collections import defaultdict

import plotly.graph_objects as go
from dash import Input, Output, callback, html

from components import base_fig, empty, graph, kpi
from config import START_MONTH, TYPE_COLOR, TYPE_LABEL
from summary import month_summary
from utils import add_months, money, money0, month_short


def months_back(ym):
    # up to 6 months ending at ym, never before the start month
    months = []
    m = max(START_MONTH, add_months(ym, -5))
    while m <= ym:
        months.append(m)
        m = add_months(m, 1)
    return months


def net_worth_chart(s, ym):
    months = months_back(ym)
    series = {k: [] for k in TYPE_LABEL}
    totals = []
    for m in months:
        total = 0.0
        for k in TYPE_LABEL:
            v = sum(rows[m]["closing"] for acc, rows in s["sts"] if acc["type"] == k and m in rows)
            series[k].append(v)
            total += v
        totals.append(total)
    if max(totals, default=0) <= 0:
        return empty("Your balance history will show up here once you add an account.", "accounts",
                     "Add your first account")
    fig = go.Figure()
    for k, label in TYPE_LABEL.items():
        fig.add_bar(
            x=[month_short(m) + " " + m[:4] for m in months], y=series[k], name=label,
            marker_color=TYPE_COLOR[k], hovertemplate="%{x}: $%{y:,.2f}<extra>" + label + "</extra>",
        )
    fig.update_layout(barmode="stack")
    return graph(base_fig(fig, 300))


def donut_chart(s):
    if s["nw"] <= 0:
        return empty("No balances yet.", "accounts", "Add an account")
    keys = [k for k in TYPE_LABEL if s["by_type"][k] > 0]
    fig = go.Figure(go.Pie(
        labels=[TYPE_LABEL[k] for k in keys], values=[s["by_type"][k] for k in keys],
        hole=0.62, marker=dict(colors=[TYPE_COLOR[k] for k in keys]), sort=False,
        textinfo="percent", hovertemplate="%{label}: $%{value:,.2f}<extra></extra>",
    ))
    fig.update_layout(
        height=280, margin=dict(l=0, r=0, t=0, b=0), paper_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter, system-ui, sans-serif", size=12),
        annotations=[dict(text=f"<b>{money0(s['nw'])}</b>", showarrow=False, font=dict(size=18))],
        legend=dict(orientation="h", y=-0.05),
    )
    return graph(fig)


def income_split(s):
    if s["income"] <= 0:
        return empty("Add your income for this month to see how it is split.", "cashflow", "Add income")
    left = max(0.0, s["left"])
    denom = max(s["income"], s["expenses"] + s["saved"], 1)
    segs = [
        ("Expenses", s["expenses"], "#3E4A44"),
        ("Moved to accounts", max(s["saved"], 0), "#2A9D8F"),
        ("Left unallocated", left, "#D3D8D0"),
    ]
    over = None
    if s["left"] < 0:
        over = html.Div(f"Over budget by {money(abs(s['left']))}: expenses plus savings exceed income.",
                        className="msg err")
    return html.Div(className="stack", children=[
        html.Div(className="bar", children=[
            html.Div(style={"width": f"{v / denom * 100:.2f}%", "background": c}) for _, v, c in segs
        ]),
        html.Div(className="legend", children=[
            html.Div([
                html.Span(className="sw", style={"background": c}),
                html.Span(label, className="muted"), html.Br(),
                html.Span(money(v), className="strong"),
                html.Span(f"  {v / denom * 100:.1f}%", className="muted"),
            ]) for label, v, c in segs
        ]),
        over,
    ])


def category_bars(s):
    totals = defaultdict(float)
    for e in s["entries"]:
        if e["kind"] == "expense":
            totals[e["category"]] += e["amount"]
    if not totals:
        return empty("No expenses logged for this month yet.", "cashflow", "Add an expense")
    items = sorted(totals.items(), key=lambda kv: -kv[1])
    top = items[0][1]
    return html.Div(className="stack-sm", children=[
        html.Div(className="catrow", children=[
            html.Span(name, className="catname"),
            html.Div(className="track", children=html.Div(className="fillbar", style={"width": f"{v / top * 100:.1f}%"})),
            html.Span(money(v), className="strong num", style={"width": "100px"}),
            html.Span(f"{v / s['expenses'] * 100:.1f}%", className="muted num", style={"width": "52px"}),
        ]) for name, v in items
    ])


@callback(
    Output("ov-kpis", "children"), Output("ov-nw", "children"), Output("ov-donut", "children"),
    Output("ov-split", "children"), Output("ov-cats", "children"),
    Input("month", "data"), Input("rev", "data"),
)
def render_overview(ym, _rev):
    s = month_summary(ym)
    n_acc = sum(1 for _, rows in s["sts"] if ym in rows)
    rate = (s["saved"] / s["income"] * 100) if s["income"] > 0 else None
    kpis = [
        kpi("Net worth", money(s["nw"]), f"across {n_acc} account(s)" if n_acc else "Add an account to start"),
        kpi("Income this month", money(s["income"]), "" if s["income"] else "Nothing added yet", "pos"),
        kpi("Expenses this month", money(s["expenses"]),
            f"{s['expenses'] / s['income'] * 100:.0f}% of income" if s["income"] else ""),
        kpi("Moved to accounts", money(s["saved"]),
            f"{rate:.0f}% of income" if rate is not None else "Log it in Accounts", "navy"),
    ]
    return kpis, net_worth_chart(s, ym), donut_chart(s), income_split(s), category_bars(s)
