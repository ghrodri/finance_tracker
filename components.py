import plotly.graph_objects as go
from dash import dcc, html


def card(title, subtitle=None, children=None, cls=""):
    head = [html.H2(title, className="h2")]
    if subtitle:
        head.append(html.P(subtitle, className="sub"))
    return html.Section(className=f"card {cls}".strip(), children=[html.Div(head)] + (children or []))


def kpi(label, value, sub="", tone=""):
    return html.Div(className="kpi", children=[
        html.Div(label, className="kpi-label"),
        html.Div(value, className=f"kpi-value {tone}".strip()),
        html.Div(sub, className="kpi-sub"),
    ])


def empty(text, goto=None, button=None):
    # optional button jumps to another screen
    kids = [html.Div(text)]
    if goto and button:
        kids.append(html.Button(button, id={"type": "goto", "to": goto}, n_clicks=0, className="btn btn-primary"))
    return html.Div(className="empty", children=kids)


def field(label, comp):
    return html.Div(className="field", children=[html.Span(label, className="lbl"), comp])


def base_fig(fig, height=300):
    fig.update_layout(
        height=height,
        margin=dict(l=48, r=12, t=12, b=36),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter, system-ui, sans-serif", size=12, color="#38453E"),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, x=0),
    )
    fig.update_xaxes(showgrid=False, linecolor="#CBD1C9")
    fig.update_yaxes(gridcolor="#E8EBE6", zeroline=False, tickprefix="$")
    return fig


def graph(fig):
    height = fig.layout.height or 300
    return dcc.Graph(figure=fig, config={"displayModeBar": False}, style={"width": "100%", "height": f"{height}px"})
