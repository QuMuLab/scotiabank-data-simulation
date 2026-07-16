from OEC_config import load_config, transits, event_logs
from OEC_classes import Employee
from OEC_visualization import launch_dashboard

import simpy, random, string, pandas as pd
from faker import Faker

# TODO:
# yaml stores all customization
# verify new .yaml file

# Incident Creation: customer type, cif, account type, account status, amount claimed, fees, charge fees, fraud, priority rows

# Product Type column

# Incident End: Fraud resolution, customer satisfaction, reimbursement, root cause rows

fake = Faker('en_CA')

def generate_employees(count: int):
    for _ in range(count):
        Employee(env, f"{fake.first_name()} {fake.last_name()}")

def generate_transits(cities: list[str]):
    for city in cities:
        transit_number = "".join(random.choices(string.digits, k = 5))
        transits.append(f"{transit_number} {city}")

if __name__ == "__main__":
    simulation_days, employee_count, transit_cities = load_config()

    env = simpy.Environment()
    
    generate_employees(employee_count)
    generate_transits(transit_cities)
    
    print("Running Simulation...")
    env.run(until = simulation_days * 24)
    print("Simulation Complete\n")
 
    df = pd.DataFrame(event_logs)
    df = df.sort_values(by = ["incident_itemno", "timestamp"])
 
    csv_df = df[df["action"] != "Handoff"]
    csv_df.to_csv("OEC_simulation_results.csv", index = False)

    launch_dashboard(df)