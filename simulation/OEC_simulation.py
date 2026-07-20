import OEC_config as config
from OEC_classes import Employee, reset_classes

import simpy, random, string, pandas as pd
from faker import Faker

# TODO:
# Dashboard to edit yaml
# Incident view incorrect times, add years to dates

# Incident Creation: customer type, cif, account type, account status, amount claimed, fees, charge fees, fraud, priority rows

# Product Type column

# Incident End: Fraud resolution, customer satisfaction, reimbursement, root cause rows

fake = Faker('en_CA')

def generate_employees(count: int, env: simpy.Environment):
    for _ in range(count):
        Employee(env, f"{fake.first_name()} {fake.last_name()}")

def generate_transits():
    for city in ["Toronto", "Kingston", "Montreal", "Ottawa", "Vancouver", "Calgary", "Edmonton", "Quebec City", "Winnipeg", "Halifax", "Moncton"]:
        transit_number = "".join(random.choices(string.digits, k = 5))
        config.transits.append(f"{transit_number} {city}")

def run_simulation(employee_count: int) -> pd.DataFrame:
    config.reset()
    reset_classes()

    env = simpy.Environment()

    generate_employees(employee_count, env)
    generate_transits()

    env.run(until = config.simulation_days * 24)

    df = pd.DataFrame(config.event_logs)
    df = df.sort_values(by = ["incident_itemno", "timestamp"])

    csv_df = df[df["action"] != "Handoff"]
    csv_df.to_csv("OEC_simulation_results.csv", index = False)

    return df

if __name__ == "__main__":
    from OEC_dashboard import launch_dashboard

    config.load_incidents()
    launch_dashboard()