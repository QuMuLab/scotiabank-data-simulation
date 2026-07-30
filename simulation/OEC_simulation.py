import OEC_config as config
import OEC_classes as classes

import simpy, logging, random, string, pandas as pd

""""
Expose root_cause weights, transit wieghts, incorrect_field_chance, session and clarification decay start to dashboard

Remove favorable outcome from dashboard and yaml

Fraud chance formula + fraud chance effects: fraud root cause

Clarifications: Field Edited investigate
Starting Fraud Chance investigate

Join Table: Additional tables

More actions / branches (Access Control (More variation), Clarification, Field Edits throughout incident lifecycle), Reassign, Cancelled

More outliers (incidents) and noise (weights)

===

Incident view incorrect times

Clean up the HTML

README

===

Variant Weights

Product Type, Account type

Incident Creation: customer type, cif, account type, account status, amount claimed, fees, charge fees, priority rows

Incident End: Fraud resolution, reimbursement rows
"""

def generate_employees(env: simpy.Environment, count: int):
    for _ in range(count):
        classes.Employee(env)

def generate_transits():
    for city in ["Toronto", "Kingston", "Montreal", "Ottawa", "Vancouver", "Calgary", "Edmonton", "Quebec City", "Winnipeg", "Halifax", "Moncton"]:
        transit_number = "".join(random.choices(string.digits, k = 5))
        config.transits.append(f"{transit_number} {city}")

def generate_join_table(df: pd.DataFrame):
    df = df[["incident_itemno", "action", "field", "newval", "timestamp"]]
    field_activity_map = {
        "incidenttype" : "INCIDENT TYPE",
        "clarification_reason" : "CLARIFICATION",
        "responsetype" : "RESPONSE TYPE"
    }
    case_ids = {}
    join_table = []

    for row in df.itertuples():
        if row.action in ["Pending", "Access Control", "Closed"]:
            activity = row.action.upper()

        elif row.action == "Field Edited" and row.field in ["incidenttype", "clarification_reason", "responsetype"]:
            activity = f"{field_activity_map[row.field]} {row.newval}"

        else:
            continue

        if row.incident_itemno not in case_ids:
            case_ids[row.incident_itemno] = len(case_ids)

        join_table.append({
            "activity" : activity,
            "case_id" : case_ids[row.incident_itemno],
            "timestamp" : row.timestamp
        })

    df = pd.DataFrame(join_table)
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