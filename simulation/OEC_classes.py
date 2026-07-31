import OEC_config as config

import string, simpy, random, datetime, itertools
from faker import Faker

starting_fields = [
    "incidenttype", "bnscustomer", "customertype", "customername", "customerlastname", "customerbusinessname", "cif", "gender", 
    "citizenship", "resident", "customerlegalrep", "customeraddress", "customercity", "customeremail", "customerbphoneno", "customerhphoneno", 
    "customercphoneno", "receptionchannel",
]

additional_fields = {
    "Claims" : ["acc_transit", "category", "subcategory", "description", "account_no", "account_type", "account_status", "provider", "amountclaimed", "fees", "chargefees", "potentialfraudfo", "transactiondate", "producttype"],
    "Requests" : ["acc_transit", "category", "subcategory", "description", "account_no", "account_type", "account_status", "provider"],
    "Complaints" : ["vttransitnames", "transit", "complainttype", "prodchannel", "priority"]
}

field_description_map = {
    "incidenttype" : "INCIDENT TYPE",
    "bnscustomer" : "BNS CUSTOMER",
    "customertype" : "CUSTOMER TYPE",
    "customername" : "FIRST NAME",
    "customerlastname" : "LAST NAME",
    "customerbusinessname" : "BUSINESS NAME",
    "cif" : "CIF",
    "gender" : "GENDER",
    "citizenship" : "CITIZENSHIP",
    "resident" : "RESIDENT",
    "customerlegalrep" : "LEGAL REPRESENTATION",
    "customeraddress" : "ADDRESS",
    "customercity" : "CITY",
    "customeremail" : "EMAIL",
    "customerbphoneno" : "BUSINESS PHONE NUMBER",
    "customerhphoneno" : "HOME PHONE NUMBER",
    "customercphoneno" : "CELL PHONE NUMBER",
    "receptionchannel" : "RECEPTION CHANNEL",
    "description" : "DESCRIPTION",

    "acc_transit" : "TRANSIT",
    "category" : "CATEGORY",
    "subcategory" : "SUB CATEGORY",
    "account_no" : "ACCOUNT #",
    "account_type" : "TYPE",
    "account_status" : "STATUS",
    "provider" : "PROVIDER",
    "amountclaimed" : "AMOUNT CLAIMED",
    "fees" : "FEES",
    "chargefees" : "CHARGE FEES TO ACCOUNT",
    "potentialfraudfo" : "FRAUD",
    "transactiondate" : "TRANSACTION DATE",
    "producttype" : "PRODUCT TYPE",

    "vttransitnames" : "VISIBLE TO",
    "transit" : "IMPACTED TRANSIT",
    "complainttype" : "COMPLAINT TYPE",
    "prodchannel" : "PROD / CHANNEL",
    "priority" : "PRIORITY"
}

incident_numbers = set()
unassigned_queue = []

fake = Faker('en_CA')

def reset():
    incident_numbers.clear()
    unassigned_queue.clear()

def simulation_datetime(env_hour: float) -> datetime.datetime:
    return config.start_datetime + datetime.timedelta(hours = env_hour)

def next_business_day(current: datetime.datetime) -> datetime.datetime:
    work_start = current.replace(hour = config.work_day_start, minute = 0, second = 0, microsecond = 0)
    work_end = current.replace(hour = config.work_day_end, minute = 0, second = 0, microsecond = 0)

    if current.weekday() >= 5:
        days_ahead = 7 - current.weekday()

        return (current + datetime.timedelta(days = days_ahead)).replace(
            hour = config.work_day_start, minute = 0, second = 0, microsecond = 0
        )

    if current < work_start:
        return work_start
    
    if current < work_end:
        return current

    next_day = current + datetime.timedelta(days = 1)
    while next_day.weekday() >= 5:
        next_day += datetime.timedelta(days = 1)

    return next_day.replace(hour = config.work_day_start, minute = 0, second = 0, microsecond = 0)

def hours_until_work(env_hour: float) -> float:
    current = simulation_datetime(env_hour)
    business_time = next_business_day(current)

    return max(0.0, (business_time - current).total_seconds() / 3600)

def business_hours_timeout(env: simpy.Environment, duration: float):
    remaining = duration

    while remaining > 1e-9:
        wait = hours_until_work(env.now)
        
        if wait > 0:
            yield env.timeout(wait)
            continue

        current = simulation_datetime(env.now)
        work_end = current.replace(hour = config.work_day_end, minute = 0, second = 0, microsecond = 0)
        available = (work_end - current).total_seconds() / 3600

        if available <= 0:
            continue

        chunk = min(remaining, available)
        yield env.timeout(chunk)
        remaining -= chunk

class Employee(object):
    incident_variants = None

    def __init__(self, env: simpy.Environment):
        self.env = env
        self.username = f"{fake.first_name()} {fake.last_name()}"
        self.current_incident = None

        self.env.process(self.run())

    def run(self):
        while True:
            wait = hours_until_work(self.env.now)
            if wait:
                yield self.env.timeout(wait)

            yield self.env.timeout(random.uniform(config.employee_timeout["minimum"], config.employee_timeout["maximum"]))

            if hours_until_work(self.env.now) > 0:
                continue

            if self.current_incident is not None:
                continue

            incident = self.get_next_incident()

            if incident is None:
                continue

            self.current_incident = incident
            yield self.env.process(self.handle_incident(incident))

    def get_next_incident(self):
        high_priority = [inc for inc in unassigned_queue if inc.is_high_priority()]

        if high_priority:
            high_priority.sort(key = lambda inc: inc.time_remaining_hours())

            incident = high_priority[0]
            unassigned_queue.remove(incident)
            incident.current_employee = self
            incident.access_incident()

            return incident

        if unassigned_queue and random.random() < config.select_unassigned_incident_chance:
            unassigned_queue.sort(key = lambda inc: inc.time_remaining_hours())

            incident = unassigned_queue[0]
            unassigned_queue.remove(incident)
            incident.current_employee = self
            incident.access_incident()

            return incident

        incident = self.create_incident()

        if incident is None:
            return None

        if random.random() < config.select_new_incident_chance:
            return incident

        unassigned_queue.append(incident)
        return None
    
    def create_incident(self):
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

        if selected_type in ["Claims", "Requests"]:
            incident = Incident(
                env = self.env,
                incident_type = selected_type,
                category = variant["category"],
                subcategory = variant["subcategory"],
                description_two = variant["description_two"],
                service_level_agreement = variant["service_level_agreement"],
                employee = self
            )

        elif selected_type == "Complaints":
            incident = Incident(
                env = self.env,
                incident_type = "Complaints",
                complaint_type = variant["complaint_type"],
                complaint_description = variant["complaint_description"],
                prod_channel = variant["prod_channel"],
                service_level_agreement = variant["service_level_agreement"],
                employee = self
            )

        if config.simulation_days * 24 - self.env.now <= 0:
            return None

        return incident

    def handle_incident(self, incident: Incident):
        while True:
            yield self.env.process(self.work_session(incident))

            if len(incident.incorrect_fields) > 0 and random.random() < 0.5:
                yield self.env.process(self.fix_incorrect_field(incident))
                incident.access_incident()
                continue

            if self.maybe_request_clarification(incident):
                yield self.env.process(self.clarify(incident))
                incident.access_incident()
                continue

            if self.is_incident_resolved(incident):
                break

            if incident.time_remaining_hours() > 0.1:
                break_duration = yield self.env.process(self.work_break(incident))

                if self.should_handoff(incident, break_duration):
                    self.handoff_incident(incident)
                    return

                incident.access_incident()

        yield self.env.process(incident.close_incident())

    def work_session(self, incident: Incident):
        duration = random.uniform(
            config.employee_work_session["minimum"],
            config.employee_work_session["maximum"]
        )
        duration = min(duration, max(incident.time_remaining_hours(), 0.05))
        incident.work_sessions += 1

        yield from business_hours_timeout(self.env, duration)

    def work_break(self, incident: Incident):
        remaining = incident.time_remaining_hours()

        if remaining <= 0:
            return 0

        max_break = min(remaining * 0.5, config.employee_work_break)
        if max_break <= 0:
            return 0

        break_duration = random.uniform(0, max_break)
        yield from business_hours_timeout(self.env, break_duration)

        return break_duration
    
    def should_handoff(self, incident: Incident, break_duration: float, required_buffer: float = 1.0) -> bool:
        if incident.time_remaining_hours() <= required_buffer:
            return False

        handoff_chance = min(break_duration / 8, config.hand_over_chance)
        return random.random() < handoff_chance

    def handoff_incident(self, incident: Incident):
        incident.log_action("Handoff")
        self.current_incident = None
        unassigned_queue.append(incident)

    def fix_incorrect_field(self, incident: Incident):
        random.shuffle(incident.incorrect_fields)
        field_info = incident.incorrect_fields[0]

        yield self.env.process(self.clarify(incident, reason = "Missing Information"))
        incident.edit_field(
            field_info["description"],
            field_info["field"],
            field_info["correct_val"],
            field_info["curval"]
        )

        incident.incorrect_fields.pop(0)

    def maybe_request_clarification(self, incident: Incident) -> bool:
        base_odds = config.base_clarify_chance
        odds = max(base_odds * (0.4 ** incident.clarification_count), 0.01)

        return random.random() < odds

    def clarify(self, incident: Incident, reason: str = None):
        incident.clarification_count += 1
        yield self.env.process(incident.clarify_incident(reason))

        wait_time = random.uniform(
            config.employee_clarify_wait["minimum"], 
            config.employee_clarify_wait["maximum"]
        )
        wait_time = min(wait_time, max(incident.time_remaining_hours(), 0.1))

        yield from business_hours_timeout(self.env, wait_time)

    def is_incident_resolved(self, incident: Incident) -> bool:
        completion_chance = min(0.2 + incident.work_sessions * config.incident_resolution_sessions_weight, 0.9)

        return random.random() < completion_chance

class Incident(object):
    
    def __init__(
        self, 
        env, 
        incident_type: str,
        service_level_agreement : int,
        employee: Employee,
        category: str = None,
        subcategory: str = None,
        description_two: str = None,
        product_type: str = None,
        complaint_type: str = None,
        prod_channel: str = None,
        complaint_description: str = None
    ):
        self.env = env
        self.incident_itemno = self.generate_incident_number()
        self.incident_type = incident_type
        self.current_employee = employee
        self.service_level_agreement = service_level_agreement * config.sla_multiplier

        self.category = category
        self.subcategory = subcategory
        self.description_two = description_two
        self.product_type = product_type
        self.complaint_type = complaint_type
        self.prod_channel = prod_channel
        self.complaint_description = complaint_description

        self.created_at = self.env.now
        self.event_sequence = itertools.count()
        self.work_sessions = 0
        self.clarification_count = 0
        self.incorrect_fields = []
        self.potential_fraud = None

        config.incidents.append(self)
        self.env.process(self.create_incident())

    def generate_incident_number(self):
        while True:
            incident_number =  "INC-" + "".join(random.choices(string.digits, k = 8))

            if incident_number not in incident_numbers:
                incident_numbers.add(incident_number)
                return incident_number

    def create_incident(self):
        self.log_action("Pending")
        yield self.env.timeout(0.5 / 3600)
        
        gender = random.choice(["Male", "Female"])
        gender_name_map = {
            "Male" : [fake.first_name_male(), fake.last_name_male()],
            "Female" : [fake.first_name_female(), fake.last_name_female()]
        }

        reception_channels = list(config.reception_channels.keys())
        reception_channel_weights = [
            config.reception_channels[reception_channel]
            for reception_channel in reception_channels
        ]

        provider_types = list(config.providers.keys())
        provider_weights = [
            config.providers[provider_type]
            for provider_type in provider_types
        ]

        priority_types = list(config.priorities.keys())
        priority_weights = [
            config.priorities[priority_type]
            for priority_type in priority_types
        ]

        if self.incident_type == "Claims":
            fraud_score = (0.025
                + int(self.category == "Credit Card" and self.subcategory == "International POS") * 0.9
                + int(self.category == "Debit Card" and self.subcategory == "International POS") * 0.8
                + int(self.category == "Credit Card" and self.subcategory == "Local POS") * 0.2
                + int(self.category == "Debit Card" and self.subcategory == "Local POS") * 0.075
            )
            
            self.potential_fraud = "Yes" if random.random() < fraud_score else "No"

        field_value_map = {
            "incidenttype" : lambda: self.incident_type,
            "bnscustomer" : lambda: "Yes",
            "receptionchannel" : lambda: random.choices(reception_channels, weights = reception_channel_weights, k = 1)[0], 
            "customertype" : lambda: None, 
            "customername" : lambda: gender_name_map[gender][0], 
            "customerlastname" : lambda: gender_name_map[gender][1], 
            "customerbusinessname" : lambda: None,   
            "cif" : lambda:  None, 
            "gender" : lambda: gender, 
            "citizenship" : lambda: "CA", 
            "resident" : lambda: "CA", 
            "customerlegalrep" : lambda: random.choices([None, "Yes"], weights = [0.99, 0.01], k = 1)[0], 
            "customeraddress" : lambda: fake.street_address(), 
            "customercity" : lambda: fake.city(), 
            "customeremail" : lambda: fake.email(), 
            "customerbphoneno" : lambda: f"{fake.msisdn()[:3]}-{fake.msisdn()[3:6]}-{fake.msisdn()[6:10]}", 
            "customerhphoneno" : lambda: f"{fake.msisdn()[:3]}-{fake.msisdn()[3:6]}-{fake.msisdn()[6:10]}", 
            "customercphoneno" : lambda: f"{fake.msisdn()[:3]}-{fake.msisdn()[3:6]}-{fake.msisdn()[6:10]}",
            "acc_transit" : lambda: random.choice(config.transits),
            "category" : lambda: self.category,
            "account_no" : lambda: fake.bban()[4:],
            "account_type" : lambda: None,
            "subcategory" : lambda: self.subcategory,
            "description" : lambda: self.description_two,
            "provider" : lambda: random.choices(provider_types, weights = provider_weights, k = 1)[0],
            "vttransitnames" : lambda: None,
            "account_status" : lambda: None,
            "fees" : lambda: "Waive",
            "amountclaimed" : lambda: None,
            "transit" : lambda: None,
            "chargefees" : lambda: 0,
            "potentialfraudfo" : lambda: self.potential_fraud,
            "prodchannel" : lambda: self.prod_channel,
            "transactiondate" : lambda: (config.start_datetime - datetime.timedelta(days = random.randint(0, config.transaction_window))).date(),
            "producttype" : lambda: self.product_type,
            "complainttype" : lambda: self.complaint_type,
            "priority" : lambda: random.choices(priority_types, weights = priority_weights, k = 1)[0]
        }

        for field in starting_fields + additional_fields[self.incident_type]:
            newval = field_value_map[field]()
            description = field_description_map[field]

            if field in config.missing_fields.keys():
                if random.random() < config.incorrect_field_chance * config.missing_fields[field]:
                    is_missing = random.random() < 0.5
                    while True:
                        correct_val = field_value_map[field]()

                        if newval != correct_val:
                            break

                    self.incorrect_fields.append({
                        "description" : description,
                        "field" : field,
                        "curval" : None if is_missing else newval,
                        "correct_val" : correct_val
                    })

                    if is_missing:
                        continue

            self.edit_field(description, field, newval, None)

    def edit_field(self, description: str, field: str, newval: str, prevval: str):
        self.log_action("Field Edited", description, field, newval, prevval)

    def access_incident(self):
        self.log_action("Access Control")

    def clarify_incident(self, reason: str = None):
        if reason is None:
            clarification_reasons = list(config.clarification_reasons.keys())
            clarification_reason_weights = list(config.clarification_reasons.values())

            reason = random.choices(clarification_reasons, weights = clarification_reason_weights, k = 1)[0]

        self.log_action("Clarification")
        yield self.env.timeout(0.5 / 3600)
        self.log_action(
            "Field Edited", 
            "CLARIFICATION REASON", 
            "clarification_reason", 
            reason
        )

    def close_incident(self):
        yield from business_hours_timeout(self.env, 0.5 / 3600)

        root_cause_map = config.root_causes[self.incident_type].copy()
        if self.potential_fraud == "Yes" and "Fraud" in root_cause_map:
            root_cause_map["Fraud"] += 0.75

        root_causes = list(root_cause_map.keys())
        root_cause_weights = list(root_cause_map.values())

        root_cause = random.choices(root_causes, weights = root_cause_weights, k = 1)[0]

        session_factor = config.factor_decays["Sessions"] ** self.work_sessions
        clarification_factor = config.factor_decays["Clarifications"] ** self.clarification_count

        response_score = session_factor * 0.4 + clarification_factor * 0.4 + int(root_cause != "Fraud") * 0.2
        response_type = "Favorable" if random.random() < response_score else "Unfavorable"

        wait_ratio = max((self.env.now - self.created_at) / (self.service_level_agreement * 24), 0)
        satisfaction_score = (1 - wait_ratio) * 0.4 + int(response_type == "Favorable") * 0.6
        customer_satisfaction = "Satisfied" if random.random() < satisfaction_score else "Not Satisfied"

        self.log_action("Field Edited", "RESPONSE TYPE", "responsetype", response_type)
        self.log_action("Field Edited", "RESPONSE TO CUSTOMER", "customerreponse")
        self.log_action("Field Edited", "CUSTOMER SATISFACTION", "customersatisfaction", customer_satisfaction)
        self.log_action("Field Edited", "ROOT CAUSE", "rootcause", root_cause)
        self.log_action("Closed")

        self.current_employee.current_incident = None

    def time_remaining_hours(self) -> float:
        sla_total_hours = self.service_level_agreement * 24
        elapsed = self.env.now - self.created_at

        return sla_total_hours - elapsed

    def is_high_priority(self, threshold: float = None) -> bool:
        if threshold is None:
            threshold = config.high_priority_threshold

        sla_total_hours = self.service_level_agreement * 24

        if sla_total_hours <= 0:
            return True
        
        return self.time_remaining_hours() <= sla_total_hours * threshold

    def log_action(self, action_type: str, description = None, field = None, newval = None, prevval = None):
        config.event_logs.append({
            "incident_itemno" : self.incident_itemno,
            "action" : action_type,
            "description" : description,
            "field" : field,
            "newval" : newval,
            "prevval" : prevval,
            "timestamp" : self.get_timestamp(),
            "username" : self.current_employee.username,
            "sequence" : next(self.event_sequence),
            "incidenttype" : self.incident_type,
            "producttype" : self.product_type,
            "category" : self.category,
            "subcategory" : self.subcategory,
            "description2" : self.description_two,
            "complainttype" : self.complaint_type,
            "prodchannel" : self.prod_channel,
            "complaintdescrip" : self.complaint_description,
            "sla" : self.service_level_agreement
        })

    def get_timestamp(self):
        current_time = config.start_datetime + datetime.timedelta(hours = self.env.now)

        return current_time.strftime("%Y-%m-%d %H:%M:%S.%f")