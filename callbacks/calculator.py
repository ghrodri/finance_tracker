import plotly.graph_objects as go
from dash import Input, Output, callback, html

from components import base_fig, card, empty, graph, kpi
from projection import simulate_savings
from utils import money0, parse_amount

YEAR_COLUMNS = {"gridTemplateColumns": "70px 1fr 1fr 1fr"}


@callback(
    Output("calc-out", "children"),
    Input("c-base", "value"), Input("c-monthly", "value"), Input("c-rate", "value"),
    Input("c-years", "value"), Input("c-day", "value"),
)
def render_calc(base, monthly, rate, years, day):
    base = parse_amount(base) or 0.0
    monthly = parse_amount(monthly) or 0.0
    rate = parse_amount(rate) or 0.0
    yrs = int(min(40, round(parse_amount(years) or 0)))
    deposit_day = int(min(31, max(1, round(parse_amount(day) or 15))))
    if yrs < 1 or (base <= 0 and monthly <= 0):
        return card("Result", None, [empty("Enter a starting balance or a monthly deposit, plus the number of years.")])

    data = simulate_savings(base, monthly, rate, yrs, deposit_day)
    last = data[-1]
    early = simulate_savings(base, monthly, rate, yrs, 1)[-1]["balance"]
    late = simulate_savings(base, monthly, rate, yrs, 28)[-1]["balance"]

    on_top = f"{last['interest'] / last['contributed'] * 100:.1f}% on top of what you put in" if last["contributed"] else ""
    kpis = html.Div(className="grid-kpi", children=[
        kpi("Final balance", money0(last["balance"]), f"after {yrs} year(s)"),
        kpi("Total contributed", money0(last["contributed"]), "starting balance plus deposits", "navy"),
        kpi("Interest earned", money0(last["interest"]), on_top, "pos"),
    ])

    xs = [f"Year {r['year']}" for r in data]
    fig = go.Figure()
    fig.add_bar(x=xs, y=[r["contributed"] for r in data], name="What you put in", marker_color="#1B3A6B")
    fig.add_bar(x=xs, y=[r["interest"] for r in data], name="Interest", marker_color="#E9A23B")
    fig.update_layout(barmode="stack")

    head = html.Div(className="row head", style=YEAR_COLUMNS, children=[
        html.Span("Year"), html.Span("Contributed", className="num"),
        html.Span("Interest", className="num"), html.Span("Balance", className="num"),
    ])
    rows = [
        html.Div(className="row", style=YEAR_COLUMNS, children=[
            html.Span(str(r["year"]), className="muted"),
            html.Span(money0(r["contributed"]), className="num"),
            html.Span(money0(r["interest"]), className="num pos"),
            html.Span(money0(r["balance"]), className="num strong"),
        ]) for r in data
    ]

    timing = ""
    if monthly > 0 and rate > 0:
        timing = (f" Timing matters: depositing on day 1 instead of day 28 ends about "
                  f"{money0(early - late)} higher after {yrs} year(s).")
    note = "Deposits count from the day they land, so a deposit late in the month earns less that month." + timing
    subtitle = f"{money0(base)} to start, {money0(monthly)} each month on day {deposit_day}, {rate:g}% a year."
    return html.Div(className="fill", children=[
        kpis,
        card("Growth year by year", subtitle, [graph(base_fig(fig, 320)), html.P(note, className="note")]),
        card("Detail by year", None, [html.Div(className="scroll", children=html.Div(className="min560", children=[head] + rows))]),
    ])
