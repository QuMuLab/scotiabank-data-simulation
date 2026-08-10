import OEC_config as config
import OEC_classes as classes

import simpy, logging, random, string, pandas as pd

""""
Favorable rate by which fields are included / not included

 - Product channel and other optional fields influencing end results

More *Access Controls* & Field Edits throughout incident lifecycle

Reassigned and cancelled incident conclusions

More outliers (incidents)
"""

def generate_employees(env: simpy.Environment, count: int):
    for _ in range(count):
        classes.Employee(env)

def generate_transits():
    for city in ["Toronto", "Kingston", "Montreal", "Ottawa", "Vancouver", "Calgary", "Edmonton", "Quebec City", "Winnipeg", "Halifax", "Moncton"]:
        transit_number = "".join(random.choices(string.digits, k = 5))
        config.transits.append(f"{transit_number} {city}")

def generate_join_table(df: pd.DataFrame):
    df = df[["activity", "case_id", "timestamp"]]
    df = df[df["activity"].notna()]
    df = df.sort_values(by = ["case_id", "timestamp"])

    df.to_csv("OEC_simulation_join_table.csv", index = False)

def run_simulation(employee_count: int, logger: logging.Logger) -> pd.DataFrame:
    logger.info("Running Simulation...")
 
    config.reset()
    classes.reset()

    env = simpy.Environment()

    generate_employees(env, employee_count)
    generate_transits()

    env.run(until = config.simulation_days * 24)

    df = pd.DataFrame(config.event_logs)
    df = df.sort_values(by = ["incident_itemno", "timestamp"])
    df.to_csv("OEC_simulation_results.csv", index = False)

    generate_join_table(df)
    logger.info("Simulation Complete")

    return df

if __name__ == "__main__":
    from OEC_dashboard import launch_dashboard

    config.load_incidents()
    launch_dashboard()