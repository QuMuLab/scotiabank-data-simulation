import OEC_config as config
import OEC_classes as classes

import simpy, random, string, argparse, tqdm, pandas as pd

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

def run_simulation(employee_count: int) -> pd.DataFrame:
    config.reset()
    classes.reset()

    env = simpy.Environment()

    generate_employees(env, employee_count)
    generate_transits()

    total_hours = config.simulation_days * 24

    with tqdm.tqdm(total = config.simulation_days, desc = "Running simulation", unit = "days") as progress:

        while env.now < total_hours:
            next_time = min(env.now + 24, total_hours)

            env.run(until = next_time)
            progress.update(1)

    df = pd.DataFrame(config.event_logs)
    df = df.sort_values(by = ["incident_itemno", "timestamp"])
    df.to_csv("OEC_simulation_results.csv", index = False)

    generate_join_table(df)
    print("Simulation results saved to OEC_simulation_results.csv")

    return df

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--dashboard", action = "store_true")
    args = parser.parse_args()

    config.load_incidents()

    if args.dashboard:
        from OEC_dashboard import launch_dashboard

        config.load_incidents()
        launch_dashboard()

    else:   
        settings, probabilities, weights = config.load_preferences()
        simulation_days, employee_count = config.apply_preferences(settings, probabilities, weights)

        run_simulation(employee_count)