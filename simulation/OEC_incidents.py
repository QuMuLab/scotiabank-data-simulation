from OEC_classes import Employee, Incident
import OEC_config as config
import simpy, random

import sys

def create_incident(env: simpy.Environment, employee: Employee):
    incident_types = list(config.incident_variants.keys())

    incident_weights = [
        config.incident_variants[incident_type]["weight"]
        for incident_type in incident_types
    ]

    selected_type = random.choices(
        population = incident_types,
        weights = incident_weights,
        k = 1,
    )[0]

    available_variants = config.incident_variants[selected_type]["variants"]
    variant = random.choice(available_variants)

    if selected_type == "Claims" or selected_type == "Requests":
        incident = Incident(
            env = env,
            incident_type = selected_type,
            category = variant["category"],
            subcategory = variant["subcategory"],
            description_two = variant["description_two"],
            service_level_agreement = variant["service_level_agreement"],
            employee = employee
        )

    elif selected_type == "Complaints":
        incident = Incident(
            env = env,
            incident_type = "Complaints",
            complaint_type = variant["complaint_type"],
            complaint_description = variant["complaint_description"],
            prod_channel = variant["prod_channel"],
            service_level_agreement = variant["service_level_agreement"],
            employee = employee
        )

    return incident