import datetime, yaml

event_logs = []
incidents = []
transits = []

def load_config():
    global start_datetime
    global simulation_days
    global incident_variants
    global work_day_start
    global work_day_end

    with open("config/default_config.yaml", "r") as file:
        config = yaml.safe_load(file)
    
    settings = config["settings"]
    incident_variants = config["incident_variants"]

    simulation_days = settings["simulation_days"]
    employee_count =  settings["employee_count"]
    transit_cities = settings["transit_cities"]

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

    return simulation_days, employee_count, transit_cities