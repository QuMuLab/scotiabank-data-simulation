# Scotiabank OEC Data Simulation #

## Overview ##
This repository contains code to run a discrete-event simulation that creates synthetic event logs for Scotiabanks OEC system for testing and demonstration purposes. It models how employees create and work on customer complaints, requests, and claims.

## Setup ## 
To setup the simulation on your own machine run the following commands in order.

```
git clone https://github.com/QuMuLab/scotiabank-data-simulation.git
```

```
cd scotiabank-data-simulation
```

```
pip install -r requirements.txt
```

## Usage ##
The simulation can be ran in headless mode with
```
python simulation/OEC_simulation.py
```

Or can be ran through an interactive dashboard with
```
python simulation/OEC_simulation.py --dashboard
```


## Configuration ##
In headless mode, the simulation settings will pull from the values in `config/preferences.yaml`, you can edit this file as you see fit and re-run the simulation to adjust it's output.

If you ran the simulation with `--dashboard` you can edit the settings through the dashboard, which is accesible at `http://127.0.0.1:8050`. You can easily adjust the settings without having to rerun the script by clicking "Back to Setup" after a run of the simulation.

Changes made directly to `preferences.yaml` will save between runs of the simulation, but changes made through the dashbaord will not.

Additionally, you can change what kind of incidents are created by adding, removing, or editing variants in `config/incidents.yaml`.

## Parameters ## 

A brief description of what each parameter found in `preferences.yaml` does can be found below.
#### `settings`

| Key | Description |
|---|---|
| `start_date` | Simulated calendar start date |
| `simulation_days` | Number of days the simulation runs for |
| `work_day.start` / `work_day.end` | The business hours employees will work|
| `employee_count` | Number of employees |
| `transaction_date_window` | Max number of days old an incident's transaction day can be |
| `employee_timeout.minimum` / `.maximum` | Hours an idle employee waits before checking for new work |
| `employee_work_session.minimum` / `.maximum` | Hours a single work session on an incident can be |
| `employee_work_break` | Hours max between work sessions |
| `employee_clarification_wait.minimum` / `.maximum` | Hours to wait on a customer clarification response |
| `noise_percentage` | Gaussian noise applied to the probabilities & weights each run |

#### `probabilities`

| Key | Description |
|---|---|
| `select_unassigned_incident_chance` | Chance an employee pulls from the unassigned queue instead of creating a new incident |
| `select_new_incident_chance` | Chance a newly created incident is worked on immediately rather than queued |
| `sla_multiplier` | Multiplier applied to each incident variant's base SLA | `1` |
| `incident_high_priority_threshold` | Fraction of SLA time remaining for an incident to be "high priority" |
| `hand_over_chance` | Chance an incident is handed off to another employee after a break |
| `base_clarification_chance` | Base chance of requesting a customer clarification |
| `incident_resolution_sessions_weight` | Added resolution chance per completed work session | 
| `incorrect_field_chance` | Base chance a given field is populated incorrectly |
| `fraud_clarify_multiplier` | Multiplier on clarification chance for suspected-fraud incidents |
| `clarification_retry_chance` | Chance of a repeat clarification when fixing an incorrect field |
| `clarification_retry_decay` | Decay applied to retry chance on each subsequent attempt |
| `base_reassign_chance` | Chance an incident is reassigned to a different transit |
| `base_cancel_chance` | Base chance an incident is cancelled instead of closed |
| `incident_blowup_chance` | Chance of an access-control "burst" event on an incident |

#### `weights`

| Key | Description |
|---|---|
| `providers` | Relative weights for provider values (e.g. `TSYS`, `NOT_APPLICABLE`, `FDR`) assigned to Claims/Requests incidents |
| `priorities` | Relative weights for `High` / `Medium` / `Low` incident priority |
| `reception_channels` | Relative weights for how an incident was received (Branch, Phone Call, Email, etc.) |
| `missing_fields` | Relative weight controlling how often each listed field is generated incorrectly or missing |
| `root_causes` | Per incident type (`Claims`, `Requests`, `Complaints`), relative weights over incident root causes |
| `clarification_reasons` | Relative weights over the reason given when a clarification is requested |
| `factor_decays` | Decay factors (`Sessions`, `Clarifications`) used when scoring an incident's closure response type |