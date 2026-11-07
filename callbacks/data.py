import csv
import io

from dash import Input, Output, callback, ctx, dcc
from dash.exceptions import PreventUpdate

from callbacks.navigation import clicked
from db import fetch

# button id -> (sql file, download name)
EXPORTS = {
    "exp-accounts": ("all_accounts", "accounts"),
    "exp-tx": ("all_transactions", "transactions"),
    "exp-entries": ("all_entries", "entries"),
}


@callback(
    Output("download", "data"),
    Input("exp-accounts", "n_clicks"), Input("exp-tx", "n_clicks"), Input("exp-entries", "n_clicks"),
    prevent_initial_call=True,
)
def export_csv(*_):
    if not clicked():
        raise PreventUpdate
    query, label = EXPORTS[ctx.triggered_id]
    rows = fetch(query)
    buf = io.StringIO()
    if rows:
        writer = csv.DictWriter(buf, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)
    return dcc.send_string(buf.getvalue(), f"wealth_tracker_{label}.csv")
