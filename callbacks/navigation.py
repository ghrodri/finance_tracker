from dash import ALL, Input, Output, State, callback, ctx
from dash.exceptions import PreventUpdate

from config import SCREEN_NAME, SCREENS, START_MONTH
from utils import add_months, max_month, month_label


def clicked():
    # true only when a real click triggered the callback
    return bool(ctx.triggered_id) and bool(ctx.triggered) and bool(ctx.triggered[0]["value"])


@callback(
    Output("screen", "data"),
    [Input(f"nav-{k}", "n_clicks") for k in SCREENS] + [Input({"type": "goto", "to": ALL}, "n_clicks")],
    prevent_initial_call=True,
)
def set_screen(*_):
    if not clicked():
        raise PreventUpdate
    trig = ctx.triggered_id
    if isinstance(trig, dict):
        return trig["to"]
    return trig.split("-", 1)[1]


@callback(
    [Output(f"page-{k}", "style") for k in SCREENS]
    + [Output(f"nav-{k}", "className") for k in SCREENS]
    + [Output("hdr-title", "children"), Output("hdr-sub", "children"), Output("month-bar", "style")],
    Input("screen", "data"), Input("month", "data"),
)
def show_screen(screen, ym):
    screen = screen or "overview"
    pages = [{} if k == screen else {"display": "none"} for k in SCREENS]
    navs = ["nav-btn active" if k == screen else "nav-btn" for k in SCREENS]
    subs = {
        "overview": month_label(ym),
        "cashflow": f"Income and expenses for {month_label(ym)}",
        "accounts": f"Movements, interest and balances for {month_label(ym)}",
        "calculator": "See how a starting balance and monthly deposits grow",
        "data": "Backups and exports",
    }
    bar = {} if screen in ("overview", "cashflow", "accounts") else {"display": "none"}
    return pages + navs + [SCREEN_NAME[screen], subs[screen], bar]


@callback(
    Output("month", "data"),
    Input("m-prev", "n_clicks"), Input("m-next", "n_clicks"),
    State("month", "data"),
    prevent_initial_call=True,
)
def move_month(_prev, _next, current):
    if not ctx.triggered_id:
        raise PreventUpdate
    new = add_months(current, -1 if ctx.triggered_id == "m-prev" else 1)
    return min(max(new, START_MONTH), max_month())


@callback(
    Output("m-label", "children"), Output("m-prev", "disabled"), Output("m-next", "disabled"),
    Input("month", "data"),
)
def month_bar(ym):
    return month_label(ym), ym <= START_MONTH, ym >= max_month()
