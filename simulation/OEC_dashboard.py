import OEC_config as config

from dash import Dash, html, dcc, Output, Input, State, ctx, no_update
from dash.exceptions import PreventUpdate
import pandas as pd

MAX_HOUR = config.simulation_days * 24
TICK_MS = 300

STATUS_COLORS = {
    "assigned": "#1e8e3e",
    "idle": "#9aa0a6",
}

INCIDENT_COLORS = ["#1a73e8", "#e8710a", "#a142f4", "#1e8e3e", "#d93025", "#12b5cb"]

def prepare_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    df["timestamp_dt"] = pd.to_datetime(df["timestamp"], format="%Y-%m-%d %H:%M:%S.%f")
    df["timestamp_hour"] = (df["timestamp_dt"] - config.start_datetime).dt.total_seconds() / 3600
    df = df.sort_values(["timestamp_hour", "incident_itemno", "sequence"]).reset_index(drop = True)

    return df

def compute_assignment_intervals(df: pd.DataFrame) -> pd.DataFrame:
    intervals = []
    open_by_employee = {}

    for row in df.itertuples(index = False):
        current = open_by_employee.get(row.username)

        if current is None or current[0] != row.incident_itemno:
            if current is not None:
                intervals.append({"employee": row.username, "incident": current[0], "start": current[1], "end": row.timestamp_hour})
                
            open_by_employee[row.username] = (row.incident_itemno, row.timestamp_hour)
            current = open_by_employee[row.username]

        if row.action in ("Closed", "Handoff"):
            intervals.append({"employee": row.username, "incident": row.incident_itemno, "start": current[1], "end": row.timestamp_hour})
            del open_by_employee[row.username]

    for username, (incident, start) in open_by_employee.items():
        intervals.append({"employee": username, "incident": incident, "start": start, "end": MAX_HOUR})

    return pd.DataFrame(intervals, columns = ["employee", "incident", "start", "end"])

def assignment_at(intervals_df: pd.DataFrame, employee: str, hour: float):
    match = intervals_df[
        (intervals_df["employee"] == employee)
        & (intervals_df["start"] <= hour)
        & (hour < intervals_df["end"])
    ]

    return match["incident"].iloc[0] if not match.empty else None

def build_slider_marks(max_hour: float, target_marks: int = 8) -> dict:
    total_months = max_hour / 24 / 30
    step_months = max(1, round(total_months / target_marks))
    step_hours = step_months * 30 * 24

    return {
        int(h): (config.start_datetime + pd.Timedelta(hours = h)).strftime("%b '%y")
        for h in range(0, int(max_hour) + 1, int(step_hours))
    }

def format_hour(hour: float) -> str:
    return (config.start_datetime + pd.Timedelta(hours = hour)).strftime("%b %d, %H:%M")

def incident_summary_text(df: pd.DataFrame, incident_itemno: str) -> str:
    rows = df[df["incident_itemno"] == incident_itemno]
    last = rows.iloc[-1]
    opened = rows.iloc[0]["timestamp_dt"]
    status = "Closed" if (rows["action"] == "Closed").any() else "Open"

    if last["incidenttype"] == "Complaints":
        classifier = f"{last['complainttype']} / {last['prodchannel']}"
        
    else:
        classifier = f"{last['category']} / {last['subcategory']}"

    return f"{last['incidenttype']}  |  {classifier}  |  {status}  |  Opened {opened:%b %d, %Y}"

def compute_incident_blocks(df: pd.DataFrame, intervals_df: pd.DataFrame, incident_itemno: str) -> list:
    segments = intervals_df[intervals_df["incident"] == incident_itemno].sort_values("start")
    incident_events = df[df["incident_itemno"] == incident_itemno].sort_values("timestamp_hour")

    blocks = []
    prev_end = None

    for seg in segments.itertuples(index = False):
        if prev_end is not None and seg.start - prev_end > 0.01:
            blocks.append({"kind": "gap", "start": prev_end, "end": seg.start})

        events = incident_events[
            (incident_events["username"] == seg.employee)
            & (incident_events["timestamp_hour"] >= seg.start)
            & (incident_events["timestamp_hour"] <= seg.end)
        ]
        blocks.append({"kind": "segment", "employee": seg.employee, "start": seg.start, "end": seg.end, "events": events})
        prev_end = seg.end

    return blocks

def render_incident_journey(df: pd.DataFrame, intervals_df: pd.DataFrame, incident_itemno: str) -> list:
    blocks = compute_incident_blocks(df, intervals_df, incident_itemno)
    color_by_employee = {}
    items = []

    for block in blocks:
        if block["kind"] == "gap":
            items.append(
                html.Div(
                    f"Unassigned - waiting in queue  ({format_hour(block['start'])} - {format_hour(block['end'])})",
                    style = {"color": "#999", "fontStyle": "italic", "fontSize": "13px", "padding": "8px 0 8px 16px"},
                )
            )
            continue

        employee = block["employee"]
        if employee not in color_by_employee:
            color_by_employee[employee] = INCIDENT_COLORS[len(color_by_employee) % len(INCIDENT_COLORS)]
        color = color_by_employee[employee]

        event_rows = []
        last_date = None

        for row in block["events"].itertuples(index = False):
            row_date = row.timestamp_dt.date()

            if row_date != last_date:
                event_rows.append(
                    html.Div(
                        row.timestamp_dt.strftime("%A, %b %d"),
                        style = {
                            "fontSize": "11px", "fontWeight": "bold", "color": "#999",
                            "textTransform": "uppercase", "letterSpacing": "0.5px",
                            "marginTop": "10px" if last_date else "0px",
                            "borderTop": "1px dashed #ddd" if last_date else "none",
                            "paddingTop": "6px" if last_date else "0px",
                        },
                    )
                )
                last_date = row_date

            event_rows.append(
                html.Div(
                    f"{row.timestamp_dt.strftime('%H:%M')}  —  {row.action}"
                    + (f":  {row.field} : {row.newval}" if pd.notna(row.field) else ""),
                    style = {"fontSize": "13px", "color": "#444", "padding": "2px 0"},
                )
            )

        items.append(
            html.Div(
                [
                    html.Div(
                        f"{employee}   ({format_hour(block['start'])} - {format_hour(block['end'])})",
                        style = {"fontWeight": "bold", "color": color, "marginBottom": "4px"},
                    ),
                    html.Div(event_rows),
                ],
                style = {"borderLeft": f"4px solid {color}", "paddingLeft": "12px", "margin": "12px 0"},
            )
        )

    return items

def build_dashboard(df: pd.DataFrame) -> Dash:
    df = prepare_dataframe(df)
    intervals_df = compute_assignment_intervals(df)
    employees = sorted(df["username"].dropna().unique().tolist())

    slider_marks = build_slider_marks(MAX_HOUR)

    app = Dash(__name__, update_title = None)
    app.title = "OEC Simulation"

    live_view = html.Div(
        [
            html.Div(
                [
                    html.Button("Play", id = "play-btn", n_clicks = 0),
                    html.Button("Pause", id = "pause-btn", n_clicks = 0),
                    html.Label("Speed (Hours):", style = {"marginLeft": "24px"}),
                    dcc.Input(id = "speed-input", type = "number", value = 4, min = 0.1, step = 0.1, style = {"width": "70px", "marginLeft": "8px"}),
                    html.Span(id = "timestamp-display", style = {"marginLeft": "32px", "fontWeight": "bold"}),
                ],
                style = {"display": "flex", "alignItems": "center", "marginBottom": "16px"},
            ),
            html.Div(
                dcc.Slider(
                    id = "time-slider",
                    min = 0,
                    max = MAX_HOUR,
                    step = 0.25,
                    value = 0,
                    marks = slider_marks,
                    updatemode = "mouseup",
                    tooltip = {"placement": "bottom", "always_visible": False},
                ),
                style = {"padding": "0 24px"},
            ),
            html.Div(
                id = "employee-grid",
                style = {
                    "display": "grid",
                    "gridTemplateColumns": "repeat(auto-fill, minmax(160px, 1fr))",
                    "gap": "10px",
                    "marginTop": "24px",
                },
            ),
            dcc.Store(id = "current-hour-store", data = 0),
            dcc.Interval(id = "tick-interval", interval = TICK_MS, disabled = True, n_intervals = 0),
        ]
    )

    incident_options = sorted(df["incident_itemno"].dropna().unique().tolist())

    journey_view = html.Div(
        [
            dcc.Dropdown(
                id = "incident-dropdown",
                options = incident_options,
                value = incident_options[0] if incident_options else None,
                style = {"width": "320px"},
            ),
            html.Div(id = "incident-summary", style = {"margin": "16px 0", "color": "#555"}),
            html.Div(id = "incident-journey"),
        ]
    )

    app.layout = html.Div(
        [
            html.H2("OEC Simulation Dashboard"),
            dcc.Tabs(
                [
                    dcc.Tab(label = "Employee View", children = [live_view]),
                    dcc.Tab(label = "Incident Journey", children = [journey_view]),
                ]
            ),
        ],
        style = {"fontFamily" : "Arial, sans-serif", "margin" : "24px"},
    )

    @app.callback(
        Output("tick-interval", "disabled"),
        Input("play-btn", "n_clicks"),
        Input("pause-btn", "n_clicks"),
        prevent_initial_call = True,
    )
    def toggle_playing(_play_clicks, _pause_clicks):
        return ctx.triggered_id != "play-btn"

    @app.callback(
        Output("current-hour-store", "data"),
        Output("time-slider", "value"),
        Output("tick-interval", "disabled", allow_duplicate = True),
        Input("tick-interval", "n_intervals"),
        Input("time-slider", "value"),
        State("current-hour-store", "data"),
        State("speed-input", "value"),
        prevent_initial_call = True,
    )
    def advance_hour(_n_intervals, slider_value, current_hour, speed):
        if ctx.triggered_id == "time-slider":
            if slider_value == current_hour:
                raise PreventUpdate
            
            return slider_value, no_update, True

        new_hour = min(current_hour + (speed or 1), MAX_HOUR)
        return new_hour, new_hour, no_update

    @app.callback(
        Output("timestamp-display", "children"),
        Output("employee-grid", "children"),
        Input("current-hour-store", "data"),
    )
    def render_frame(hour):
        ts = config.start_datetime + pd.Timedelta(hours = hour)
        cards = []

        for name in employees:
            incident = assignment_at(intervals_df, name, hour)
            assigned = incident is not None
            color = STATUS_COLORS["assigned"] if assigned else STATUS_COLORS["idle"]

            cards.append(
                html.Div(
                    [
                        html.Div(name, style = {"color": color, "fontWeight": "bold"}),
                        html.Div(incident if assigned else "idle", style = {"fontSize": "12px", "color": "#666"}),
                    ],
                    style = {"border": "1px solid #ddd", "borderRadius": "6px", "padding": "8px", "textAlign": "center"},
                )
            )

        return ts.strftime("%A, %B %d %Y  %H:%M"), cards
    
    @app.callback(
        Output("incident-summary", "children"),
        Output("incident-journey", "children"),
        Input("incident-dropdown", "value"),
    )
    def render_incident(incident_itemno):
        if not incident_itemno:
            raise PreventUpdate

        summary = incident_summary_text(df, incident_itemno)
        journey = render_incident_journey(df, intervals_df, incident_itemno)

        return summary, journey

    return app

def launch_dashboard(df: pd.DataFrame):
    app = build_dashboard(df)
    app.run(debug = False)