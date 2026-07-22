import OEC_config as config
import OEC_classes as classes

import simpy, logging, random, string, pandas as pd

""""
Expose incident_type and root_cause weights to dashboard

Non critical fields (missing or incorrect fields) -> clarifications

Incident view incorrect times, add years to dates

====

1. More actions (Access Control (More variation), Clarification, Field Edited)

2. Hand offs

3. Fraud chance formula + fraud chance effects fraud root cause

4. Response type formula

5. Clean up the HTML

6. More events / branches, outliers, noise

7. Product Type, Account type

8. Incident Creation: customer type, cif, account type, account status, amount claimed, fees, charge fees, fraud, priority rows

9. Incident End: Fraud resolution, customer satisfaction, reimbursement rows
"""

def generate_employees(count: int, env: simpy.Environment):
    for _ in range(count):
        classes.Employee(env)

def generate_transits():
    for city in ["Toronto", "Kingston", "Montreal", "Ottawa", "Vancouver", "Calgary", "Edmonton", "Quebec City", "Winnipeg", "Halifax", "Moncton"]:
        transit_number = "".join(random.choices(string.digits, k = 5))
        config.transits.append(f"{transit_number} {city}")

def run_simulation(employee_count: int, logger: logging.Logger) -> pd.DataFrame:
    logger.info("Running Simulation...")

    config.reset()
    classes.reset()

    env = simpy.Environment()

    generate_employees(employee_count, env)
    generate_transits()

    env.run(until = config.simulation_days * 24)

    df = pd.DataFrame(config.event_logs)
    df = df.sort_values(by = ["incident_itemno", "timestamp"])

    csv_df = df[df["action"] != "Handoff"]
    csv_df.to_csv("OEC_simulation_results.csv", index = False)

    logger.info("Simulation Complete")
    return df

if __name__ == "__main__":
    from OEC_dashboard import launch_dashboard

    config.load_incidents()
    launch_dashboard()