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

    df.to_csv("OEC_event_table.csv", index = False)

def parse_number(value: str):
    try:
        return int(value)
    
    except ValueError:
        return float(value)

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
    df.to_csv("OEC_information_table.csv", index = False)

    generate_join_table(df)
    print("Simulation results saved to OEC_information_table.csv")

    return df

if __name__ == "__main__":
    config.load_incidents()
    settings, probabilities, weights = config.load_preferences()
 
    parser = argparse.ArgumentParser(usage = "%(prog)s [--dashboard] [--param_name value ...]")
    parser.add_argument("--dashboard", action = "store_true")
 
    flags = []
 
    for key in probabilities:
        flags.append((key, probabilities, key))
 
    for key, value in settings.items():
        if isinstance(value, dict):
            for subkey in value:
                flags.append((f"{key}_{subkey}", value, subkey))

        else:
            flags.append((key, settings, key))
 
    for flag_name, _, _ in flags:
        parser.add_argument(f"--{flag_name}", type = parse_number, default = None)
 
    args = parser.parse_args()
 
    passed_flags = [flag_name for flag_name, _, _ in flags if getattr(args, flag_name) is not None]
 
    if args.dashboard and passed_flags:
        print(f"error: --dashboard cannot be combined with other flags, got: {passed_flags}")
        raise SystemExit(1)
 
    if args.dashboard:
        from OEC_dashboard import launch_dashboard
 
        launch_dashboard()
 
    else:
        for flag_name, target_dict, key in flags:
            value = getattr(args, flag_name)

            if value is not None:
                target_dict[key] = value
 
        simulation_days, employee_count = config.apply_preferences(settings, probabilities, weights)
 
        run_simulation(employee_count)