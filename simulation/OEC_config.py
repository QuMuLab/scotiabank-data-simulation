import datetime, yaml

event_logs = []
incidents = []
transits = []

def reset():
    event_logs.clear()
    incidents.clear()
    transits.clear()

def load_incidents():
    global incident_variants

    with open("config/incidents.yaml", "r") as file:
        config = yaml.safe_load(file)

    incident_variants = config["incident_variants"]

def load_preferences():
    with open("config/preferences.yaml", "r") as file:
        config = yaml.safe_load(file)

    return config["settings"], config["probabilities"], config["weights"]

def apply_preferences(settings, probabilities, weights):
    global start_datetime, simulation_days, work_day_start, work_day_end, transaction_window, employee_timeout, employee_work_session, employee_work_break, employee_clarify_wait, incident_resolution_sessions_weight
    global select_unassigned_incident_chance, select_new_incident_chance, fav_outcome_chance, sla_multiplier, potential_fraud_chance, high_priority_threshold, hand_over_chance, base_clarify_chance
    global providers, priorities, reception_channels, root_causes

    start_date = settings["start_date"]
    start_datetime = datetime.datetime(
        start_date["year"], 
        start_date["month"], 
        start_date["day"], 
        0, 
        0
    )
    simulation_days = settings["simulation_days"]
    work_day_start = settings["work_day"]["start"]
    work_day_end = settings["work_day"]["end"]
    employee_count = settings["employee_count"]
    transaction_window = settings["transaction_date_window"]
    employee_timeout = settings["employee_timeout"]
    employee_work_session = settings["employee_work_session"]
    employee_work_break = settings["employee_work_break"]
    employee_clarify_wait = settings["employee_clarification_wait"]

    select_unassigned_incident_chance = probabilities["select_unassigned_incident_chance"]
    select_new_incident_chance = probabilities["select_new_incident_chance"]
    fav_outcome_chance = probabilities["favourable_outcome_chance"]
    sla_multiplier = probabilities["sla_multiplier"]
    potential_fraud_chance = probabilities["potential_fraud_chance"]
    high_priority_threshold = probabilities["incident_high_priority_threshold"]
    hand_over_chance = probabilities["hand_over_chance"]
    base_clarify_chance = probabilities["base_clarification_chance"]
    incident_resolution_sessions_weight = probabilities["incident_resolution_sessions_weight"]

    providers = weights["providers"]
    priorities = weights["priorities"]
    reception_channels = weights["reception_channels"]
    root_causes = weights["root_causes"]

    return simulation_days, employee_count

def load_and_apply_preferences():
    settings, probabilities, weights = load_preferences()

    return apply_preferences(settings, probabilities, weights)