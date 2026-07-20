import OEC_config as config
from OEC_classes import Employee

import simpy, random, string, pandas as pd
from faker import Faker

# TODO:
# Dashboard to edit yaml
# Incident view incorrect times

# Incident Creation: customer type, cif, account type, account status, amount claimed, fees, charge fees, fraud, priority rows

# Product Type column

# Incident End: Fraud resolution, customer satisfaction, reimbursement, root cause rows

fake = Faker('en_CA')

def generate_employees(count: int):
    for _ in range(count):
        Employee(env, f"{fake.first_name()} {fake.last_name()}")

def generate_transits():
    for city in ["Toronto", "Kingston", "Montreal", "Ottawa", "Vancouver", "Calgary", "Edmonton", "Quebec City", "Winnipeg", "Halifax", "Moncton"]:
        transit_number = "".join(random.choices(string.digits, k = 5))
        config.transits.append(f"{transit_number} {city}")

if __name__ == "__main__":
    simulation_days, employee_count = config.load_settings()
    config.load_incidents()

    env = simpy.Environment()
    
    generate_employees(employee_count)
    generate_transits()
    
    print("Running Simulation...")
    env.run(until = simulation_days * 24)
    print("Simulation Complete\n")

    print("Saving simulation results...")
    df = pd.DataFrame(config.event_logs)
    df = df.sort_values(by = ["incident_itemno", "timestamp"])
 
    csv_df = df[df["action"] != "Handoff"]
    csv_df.to_csv("OEC_simulation_results.csv", index = False)
    print("Simulation results saved\n")
    
    print("Loading Dashboard...")
    from OEC_dashboard import launch_dashboard
    launch_dashboard(df)