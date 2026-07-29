import OEC_config as config
from OEC_simulation import run_simulation

from dash import Dash, html, dcc, Output, Input, State, ctx, no_update, ALL
from dash.exceptions import PreventUpdate
import pandas as pd
import logging

TICK_MS = 300
simulation_state = {}

STATUS_COLORS = {
    "assigned": "#1e8e3e",
    "idle": "#9aa0a6",
}

INCIDENT_COLORS = ["#1a73e8", "#e8710a", "#a142f4", "#1e8e3e", "#d93025", "#12b5cb"]

def build_settings_fields(settings: dict) -> html.Div:
    return html.Div(
        [
            html.H4("Simulation Settings"),

            html.Div(
                [
                    html.Label("Start Date (Y / M / D)"),
                    dcc.Input(id = "setting-start-year", type = "number", value = settings["start_date"]["year"], style = {"width": "80px", "marginLeft": "8px"}),
                    dcc.Input(id = "setting-start-month", type = "number", value = settings["start_date"]["month"], min = 1, max = 12, style = {"width": "60px", "marginLeft": "6px"}),
                    dcc.Input(id = "setting-start-day", type = "number", value = settings["start_date"]["day"], min = 1, max = 31, style = {"width": "60px", "marginLeft": "6px"}),
                ],
                style = {"marginBottom": "12px"},
            ),

            html.Div(
                [
                    html.Label("Simulation Days"),
                    dcc.Input(id = "setting-simulation-days", type = "number", value = settings["simulation_days"], style = {"width": "100px", "marginLeft": "8px"}),
                ],
                style = {"marginBottom": "12px"},
            ),

            html.Div(
                [
                    html.Label("Work Day (Start - End)"),
                    dcc.Input(id = "setting-work-day-start", type = "number", value = settings["work_day"]["start"], min = 0, max = 23, style = {"width": "60px", "marginLeft": "8px"}),
                    dcc.Input(id = "setting-work-day-end", type = "number", value = settings["work_day"]["end"], min = 0, max = 23, style = {"width": "60px", "marginLeft": "6px"}),
                ],
                style = {"marginBottom": "12px"},
            ),

            html.Div(
                [
                    html.Label("Employee Count"),
                    dcc.Input(id = "setting-employee-count", type = "number", value = settings["employee_count"], style = {"width": "100px", "marginLeft": "8px"}),
                ],
                style = {"marginBottom": "12px"},
            ),

            html.Div(
                [
                    html.Label("Transaction Date Window (Days)"),
                    dcc.Input(id = "setting-transaction-window", type = "number", value = settings["transaction_date_window"], style = {"width": "100px", "marginLeft": "8px"}),
                ],
                style = {"marginBottom": "12px"},
            ),

            html.Div(
                [
                    html.Label("Employee Timeout (Hours, Min - Max)"),
                    dcc.Input(id = "setting-timeout-min", type = "number", value = settings["employee_timeout"]["minimum"], step = "any", style = {"width": "80px", "marginLeft": "8px"}),
                    dcc.Input(id = "setting-timeout-max", type = "number", value = settings["employee_timeout"]["maximum"], step = "any", style = {"width": "80px", "marginLeft": "6px"}),
                ],
                style = {"marginBottom": "12px"},
            ),

            html.Div(
                [
                    html.Label("Employee Work Session (Hours, Min - Max)"),
                    dcc.Input(id = "setting-session-min", type = "number", value = settings["employee_work_session"]["minimum"], step = "any", style = {"width": "80px", "marginLeft": "8px"}),
                    dcc.Input(id = "setting-session-max", type = "number", value = settings["employee_work_session"]["maximum"], step = "any", style = {"width": "80px", "marginLeft": "6px"}),
                ],
                style = {"marginBottom": "12px"},
            ),

            html.Div(
                [
                    html.Label("Employee Work Break (Hours)"),
                    dcc.Input(id = "setting-work-break", type = "number", value = settings["employee_work_break"], step = "any", style = {"width": "100px", "marginLeft": "8px"}),
                ],
                style = {"marginBottom": "12px"},
            ),

            html.Div(
                [
                    html.Label("Employee Clarification Wait (Hours, Min - Max)"),
                    dcc.Input(id = "setting-clarify-min", type = "number", value = settings["employee_clarification_wait"]["minimum"], step = "any", style = {"width": "80px", "marginLeft": "8px"}),
                    dcc.Input(id = "setting-clarify-max", type = "number", value = settings["employee_clarification_wait"]["maximum"], step = "any", style = {"width": "80px", "marginLeft": "6px"}),
                ],
                style = {"marginBottom": "12px"},
            ),
        ]
    )

def build_weighted_options_fields(section_id: str, label: str, options: dict) -> html.Div:
    rows = []

    for option_name, option_weight in options.items():
        rows.append(
            html.Div(
                [
                    html.Label(option_name),
                    dcc.Input(
                        id = {"type": section_id, "index": option_name},
                        type = "number",
                        value = option_weight,
                        step = "any",
                        style = {"width": "80px", "marginLeft": "6px"},
                    ),
                ],
                style = {"marginBottom": "6px"},
            )
        )

    return html.Div(
        [
            html.Label(label, style = {"fontWeight": "bold"}),
            html.Div(rows, style = {"marginTop": "6px"}),
        ],
        style = {"marginBottom": "12px"},
    )

def build_weighted_sections(weights: dict, incident_variants: dict) -> html.Div:
    return html.Div(
        [
            html.H4("Weights"),

            html.Div(
                [
                    build_weighted_options_fields(
                        "prob-reception-weight",
                        "Reception Channels",
                        weights["reception_channels"]
                    ),

                    html.Div(
                        [
                            build_weighted_options_fields(
                                "prob-missing-fields-weight",
                                "Missing Fields",
                                weights["missing_fields"]
                            ),

                            build_weighted_options_fields(
                                "prob-clarification-reasons-weight",
                                "Clarification Reasons",
                                weights["clarification_reasons"]
                            ),
                        ],
                        style = {
                            "display": "flex",
                            "flexDirection": "column",
                            "gap": "5px",
                        }
                    ),

                    html.Div(
                        [
                            build_weighted_options_fields(
                                "prob-provider-weight",
                                "Providers",
                                weights["providers"]
                            ),
                            build_weighted_options_fields(
                                "prob-priority-weight",
                                "Priorities",
                                weights["priorities"]
                            ),
                        ],
                        style = {
                            "display": "flex",
                            "flexDirection": "column",
                            "gap": "5px",
                        }
                    ),

                    build_weighted_options_fields(
                        "incident-type-weight",
                        "Incident Types",
                        {name: variant["weight"] for name, variant in incident_variants.items()}
                    )

                ],
                style = {
                    "display": "flex",
                    "flexWrap": "wrap",
                    "gap": "40px",
                },
            ),
        ],
        style = {
            "width": "100%",
            "marginTop": "24px",
        },
    )

def build_probabilities_fields(probabilities: dict) -> html.Div:
    return html.Div(
        [
            html.H4("Probabilities"),

            html.Div(
                [
                    html.Label("Select Unassigned Incident Chance"),
                    dcc.Input(id = "prob-select-unassigned", type = "number", value = probabilities["select_unassigned_incident_chance"], step = "any", style = {"width": "80px", "marginLeft": "8px"})
                ],
                style = {"marginBottom": "12px"}
            ),

            html.Div(
                [
                    html.Label("Select New Incident Chance"),
                    dcc.Input(id = "prob-select-new", type = "number", value = probabilities["select_new_incident_chance"], step = "any", style = {"width": "80px", "marginLeft": "8px"})
                ],
                style = {"marginBottom": "12px"}
            ),

            html.Div(
                [
                    html.Label("Favourable Outcome Chance"),
                    dcc.Input(id = "prob-fav-outcome", type = "number", value = probabilities["favourable_outcome_chance"], step = "any", style = {"width": "80px", "marginLeft": "8px"})
                ],
                style = {"marginBottom": "12px"}
            ),

            html.Div(
                [
                    html.Label("SLA Multiplier"),
                    dcc.Input(id = "prob-sla-multiplier", type = "number", value = probabilities["sla_multiplier"], step = "any", style = {"width": "80px", "marginLeft": "8px"})
                ],
                style = {"marginBottom": "12px"}
            ),

            html.Div(
                [
                    html.Label("Potential Fraud Chance"),
                    dcc.Input(id = "prob-potential-fraud", type = "number", value = probabilities["potential_fraud_chance"], step = "any", style = {"width": "80px", "marginLeft": "8px"})
                ],
                style = {"marginBottom": "12px"}
            ),

            html.Div(
                [
                    html.Label("Incident High Priority Threshold"),
                    dcc.Input(id = "prob-high-priority-threshold", type = "number", value = probabilities["incident_high_priority_threshold"], step = "any", style = {"width": "80px", "marginLeft": "8px"})
                ],
                style = {"marginBottom": "12px"}
            ),

            html.Div(
                [
                    html.Label("Hand Over Chance"),
                    dcc.Input(id = "prob-hand-over", type = "number", value = probabilities["hand_over_chance"], step = "any", style = {"width": "80px", "marginLeft": "8px"})
                ],
                style = {"marginBottom": "12px"}
            ),

            html.Div(
                [
                    html.Label("Base Clarification Chance"),
                    dcc.Input(id = "prob-base-clarification", type = "number", value = probabilities["base_clarification_chance"], step = "any", style = {"width": "80px", "marginLeft": "8px"})
                ],
                style = {"marginBottom": "12px"}
            ),

            html.Div(
                [
                    html.Label("Incident Resolution Sessions Weight"),
                    dcc.Input(id = "prob-resolution-sessions-weight", type = "number", value = probabilities["incident_resolution_sessions_weight"], step = "any", style = {"width": "80px", "marginLeft": "8px"})
                ],
                style = {"marginBottom": "12px"}
            )
        ]
    )

def build_setup_view() -> html.Div:
    settings, probabilities, weights = config.load_preferences()
    incident_variants = config.load_incidents()

    return html.Div(
        [
            html.H2("OEC Simulation Setup"),
            html.Button("Run Simulation", id = "run-simulation-btn", n_clicks = 0),
            html.Div(
                [
                    html.Div(build_settings_fields(settings)),
                    html.Div(build_probabilities_fields(probabilities))
                ],
                style = {"display": "flex", "flexWrap": "wrap", "gap": "40px"}
            ),
            html.Div(
                build_weighted_sections(weights, incident_variants)
            )
        ],
        style = {"fontFamily": "Arial, sans-serif", "margin": "24px"}
    )

def build_loading_view() -> html.Div:
    return html.Div(
        html.H3("Running simulation..."),
        style = {"fontFamily": "Arial, sans-serif", "margin": "24px", "textAlign": "center"}
    )

def prepare_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    df["timestamp_dt"] = pd.to_datetime(df["timestamp"], format="%Y-%m-%d %H:%M:%S.%f")
    df["timestamp_hour"] = (df["timestamp_dt"] - config.start_datetime).dt.total_seconds() / 3600
    df = df.sort_values(["timestamp_hour", "incident_itemno", "sequence"]).reset_index(drop = True)

    return df

def compute_assignment_intervals(df: pd.DataFrame, max_hour: float) -> pd.DataFrame:
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
        intervals.append({"employee": username, "incident": incident, "start": start, "end": max_hour})

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
    return (config.start_datetime + pd.Timedelta(hours = hour)).strftime("%b %d, %H:%M %Y")

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

def build_results_view() -> html.Div:
    df = simulation_state["df"]
    max_hour = simulation_state["max_hour"]

    slider_marks = build_slider_marks(max_hour)

    live_view = html.Div(
        [
            html.Div(
                [
                    html.Button("Play", id = "play-btn", n_clicks = 0),
                    html.Button("Pause", id = "pause-btn", n_clicks = 0),
                    html.Label("Speed (Hours):", style = {"marginLeft": "24px"}),
                    dcc.Input(id = "speed-input", type = "number", value = 4, min = 0.1, step = "any", style = {"width": "70px", "marginLeft": "8px"}),
                    html.Span(id = "timestamp-display", style = {"marginLeft": "32px", "fontWeight": "bold"}),
                ],
                style = {"display": "flex", "alignItems": "center", "marginBottom": "16px"},
            ),
            html.Div(
                dcc.Slider(
                    id = "time-slider",
                    min = 0,
                    max = max_hour,
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

    return html.Div(
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

def build_app() -> Dash:
    app = Dash(__name__, update_title = None, suppress_callback_exceptions = True)
    app.title = "OEC Simulation"

    app.layout = html.Div(
        [
            dcc.Store(id = "page-stage", data = "setup"),
            dcc.Interval(id = "run-trigger", interval = 200, disabled = True, n_intervals = 0, max_intervals = 1),
            html.Div(
                html.Button("Back to Setup", id = "back-to-setup-btn", n_clicks = 0),
                id = "back-to-setup-container",
                style = {"display": "none", "margin": "24px 24px 0 24px"},
            ),
            html.Div(id = "setup-container", children = build_setup_view()),
            html.Div(id = "loading-container", children = build_loading_view(), style = {"display": "none"}),
            html.Div(id = "results-container", style = {"display": "none"}),
        ]
    )

    @app.callback(
        Output("setup-container", "style"),
        Output("loading-container", "style"),
        Output("results-container", "style"),
        Output("back-to-setup-container", "style"),
        Input("page-stage", "data"),
    )
    def switch_stage(stage):
        return (
            {"display": "block"} if stage == "setup" else {"display": "none"},
            {"display": "block"} if stage == "loading" else {"display": "none"},
            {"display": "block"} if stage == "results" else {"display": "none"},
            {"display": "block", "margin": "24px 24px 0 24px"} if stage == "results" else {"display": "none"},
        )

    @app.callback(
        Output("page-stage", "data"),
        Output("run-trigger", "disabled"),
        Output("run-trigger", "n_intervals"),
        Input("run-simulation-btn", "n_clicks"),
        prevent_initial_call = True,
    )
    def start_run(n_clicks):
        return "loading", False, 0

    @app.callback(
        Output("page-stage", "data", allow_duplicate = True),
        Output("results-container", "children"),
        Output("run-trigger", "disabled", allow_duplicate = True),
        Input("run-trigger", "n_intervals"),
        State("setting-start-year", "value"),
        State("setting-start-month", "value"),
        State("setting-start-day", "value"),
        State("setting-simulation-days", "value"),
        State("setting-work-day-start", "value"),
        State("setting-work-day-end", "value"),
        State("setting-employee-count", "value"),
        State("setting-transaction-window", "value"),
        State("setting-timeout-min", "value"),
        State("setting-timeout-max", "value"),
        State("setting-session-min", "value"),
        State("setting-session-max", "value"),
        State("setting-work-break", "value"),
        State("setting-clarify-min", "value"),
        State("setting-clarify-max", "value"),
        State("prob-select-unassigned", "value"),
        State("prob-select-new", "value"),
        State("prob-fav-outcome", "value"),
        State("prob-sla-multiplier", "value"),
        State("prob-potential-fraud", "value"),
        State("prob-high-priority-threshold", "value"),
        State("prob-hand-over", "value"),
        State("prob-base-clarification", "value"),
        State("prob-resolution-sessions-weight", "value"),
        State({"type": "prob-provider-weight", "index": ALL}, "value"),
        State({"type": "prob-provider-weight", "index": ALL}, "id"),
        State({"type": "prob-priority-weight", "index": ALL}, "value"),
        State({"type": "prob-priority-weight", "index": ALL}, "id"),
        State({"type": "prob-reception-weight", "index": ALL}, "value"),
        State({"type": "prob-reception-weight", "index": ALL}, "id"),
        State({"type": "prob-missing-fields-weight", "index": ALL}, "value"),
        State({"type": "prob-missing-fields-weight", "index": ALL}, "id"),
        State({"type": "prob-clarification-reasons-weight", "index": ALL}, "value"),
        State({"type": "prob-clarification-reasons-weight", "index": ALL}, "id"),
        State({"type": "incident-type-weight", "index": ALL}, "value"),
        State({"type": "incident-type-weight", "index": ALL}, "id"),
        prevent_initial_call = True
    )
    def run_and_render(
        _n_intervals,
        start_year, start_month, start_day,
        simulation_days_value,
        work_day_start_value, work_day_end_value,
        employee_count_value,
        transaction_window_value,
        timeout_min, timeout_max,
        session_min, session_max,
        work_break_value,
        clarify_min, clarify_max,
        select_unassigned, select_new, fav_outcome,
        sla_multiplier_value, potential_fraud,
        high_priority_threshold_value, hand_over,
        base_clarification, resolution_sessions_weight,
        provider_weights, provider_ids,
        priority_weights, priority_ids,
        reception_weights, reception_ids,
        missing_fields_weights, missing_fields_ids,
        clarification_reasons_weights, clarification_reasons_ids,
        incident_type_weights, incident_type_ids
    ):
        
        if _n_intervals != 1 or simulation_state.get("running"):
            raise PreventUpdate

        simulation_state["running"] = True

        try:
            settings = {
                "start_date": {"year": start_year, "month": start_month, "day": start_day},
                "simulation_days": simulation_days_value,
                "work_day": {"start": work_day_start_value, "end": work_day_end_value},
                "employee_count": employee_count_value,
                "transaction_date_window": transaction_window_value,
                "employee_timeout": {"minimum": timeout_min, "maximum": timeout_max},
                "employee_work_session": {"minimum": session_min, "maximum": session_max},
                "employee_work_break": work_break_value,
                "employee_clarification_wait": {"minimum": clarify_min, "maximum": clarify_max},
            }

            probabilities = {
                "select_unassigned_incident_chance": select_unassigned,
                "select_new_incident_chance": select_new,
                "favourable_outcome_chance": fav_outcome,
                "sla_multiplier": sla_multiplier_value,
                "potential_fraud_chance": potential_fraud,
                "incident_high_priority_threshold": high_priority_threshold_value,
                "hand_over_chance": hand_over,
                "base_clarification_chance": base_clarification,
                "incident_resolution_sessions_weight": resolution_sessions_weight,
                "incorrect_field_chance" : 0.05 # placeholder
            }

            providers = {item["index"]: weight for item, weight in zip(provider_ids, provider_weights)}
            priorities = {item["index"]: weight for item, weight in zip(priority_ids, priority_weights)}
            receptions = {item["index"]: weight for item, weight in zip(reception_ids, reception_weights)}
            missing_fields = {item["index"]: weight for item, weight in zip(missing_fields_ids, missing_fields_weights)}
            clarification_reasons = {item["index"]: weight for item, weight in zip(clarification_reasons_ids, clarification_reasons_weights)}
            incident_weights = {item["index"]: weight for item, weight in zip(incident_type_ids, incident_type_weights)}

            weights = {
                "providers": providers,
                "priorities": priorities,
                "reception_channels": receptions,
                "missing_fields": missing_fields,
                "root_causes": config.load_preferences()[2]["root_causes"], # placeholder
                "clarification_reasons": clarification_reasons
            }

            simulation_days, employee_count = config.apply_preferences(settings, probabilities, weights)
            config.apply_incidents(incident_weights)

            df = run_simulation(employee_count, logging.getLogger("werkzeug"))
            max_hour = simulation_days * 24

            simulation_state["df"] = prepare_dataframe(df)
            simulation_state["intervals_df"] = compute_assignment_intervals(simulation_state["df"], max_hour)
            simulation_state["employees"] = sorted(simulation_state["df"]["username"].dropna().unique().tolist())
            simulation_state["max_hour"] = max_hour

        finally:
            simulation_state["running"] = False

        return "results", build_results_view(), True

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
        max_hour = simulation_state["max_hour"]

        if ctx.triggered_id == "time-slider":
            if slider_value == current_hour:
                raise PreventUpdate

            return slider_value, no_update, True

        new_hour = min(current_hour + (speed or 1), max_hour)
        return new_hour, new_hour, no_update

    @app.callback(
        Output("timestamp-display", "children"),
        Output("employee-grid", "children"),
        Input("current-hour-store", "data"),
    )
    def render_frame(hour):
        intervals_df = simulation_state["intervals_df"]
        employees = simulation_state["employees"]

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

        df = simulation_state["df"]
        intervals_df = simulation_state["intervals_df"]

        summary = incident_summary_text(df, incident_itemno)
        journey = render_incident_journey(df, intervals_df, incident_itemno)

        return summary, journey
    
    @app.callback(
        Output("page-stage", "data", allow_duplicate = True),
        Input("back-to-setup-btn", "n_clicks"),
        prevent_initial_call = True,
    )
    def back_to_setup(n_clicks):
        return "setup"

    return app

def launch_dashboard():
    app = build_app()
    app.run(debug = False, threaded = False)