from OEC_classes import Employee, transits, event_logs, simulation_days
from OEC_visualization import launch_dashboard

import simpy, random, string, pandas as pd
from faker import Faker

# TODO:
# Incident End: Fraud resolution, customer satisfaction, reimbursement, root cause
# Visualization

# Incident Creation: customer type, cif, account type, account status, amount claimed, fees, charge fees, fraud, priority
# Product Type
# Incident type percentages

fake = Faker('en_CA')

def generate_employees():
    for _ in range(25):
        Employee(env, f"{fake.first_name()} {fake.last_name()}")

def generate_transits():
    for city in ["Toronto", "Kingston", "Montreal", "Ottawa", "Vancouver", "Calgary", "Edmonton", "Quebec City", "Winnipeg", "Halifax", "Moncton"]:
        transit_number = "".join(random.choices(string.digits, k = 5))
        transits.append(f"{transit_number} {city}")

if __name__ == "__main__":
    env = simpy.Environment()
 
    generate_transits()
    generate_employees()
    
    print("Running Simulation...")
    env.run(until = simulation_days * 24)
    print("Simulation Complete\n")
 
    df = pd.DataFrame(event_logs)
    df = df.sort_values(by = ["incident_itemno", "timestamp"])
 
    csv_df = df[df["action"] != "Handoff"]
    csv_df.to_csv("OEC_simulation_results.csv", index = False)

    launch_dashboard(df)