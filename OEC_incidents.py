from OEC_classes import Employee, Incident
import simpy, random

def create_claim(env: simpy.Environment, employee: Employee):
    category = random.choice([
        "Credit Card", "Debit Card", "BSC - Corporate", "Debit Deposit Accounts", "Disputes below USD50", "Electronic Transactions", "Personal Loan", "Regulatory"
    ])

    if category == "Credit Card":
        subcategory = random.choice(["International POS", "Local POS", "Fraud"])

        if subcategory == "International POS":
            description_two = random.choice([
                "Customer doesn't recognize transaction", 
                "Customer claims amount charged is incorrect", 
                "Investigation for credit not processed by Merchant",
                "Investigaton for Product not recieved"
            ])
            sla = 120

        elif subcategory == "Local POS":
            description_two = random.choice([
                "Customer doesn't recognize transaction",
                "Customer claims transaction was duplicated by the merchant",
                "Customer claims amount charged is incorrect", 
            ])
            sla = 120

        elif subcategory == "Fraud":
            description_two = "Customer suspects transaction is fraudulent"
            sla = 120

    elif category == "Debit Card":
        subcategory = random.choice(["International POS", "Local BNS ATM", "Local Non BNS ATM", "Local Offsite ABM", "Local Onsite ABM Deposit", "Local POS"])

        if subcategory == "International POS":
            description_two = random.choice([
                "Customer claims amount charged is incorrect",
                "Customer claims transaction was duplicated by the merchant",
                "Customer doesn't recognize transaction",
                "Investigation for credit not processed by Merchant",
                "Investigaton for Product not recieved"
            ])
            sla = 120

        elif subcategory == "Local BNS ATM":
            description_two = random.choice([
                "ATM Cash Not dispensed",
                "Customer tried to withdraw but the money wasn't delivered",
                "Customer withdrawal, ABM didn't deliver the total amount requested"
            ])

            if description_two == "ATM Cash Not dispensed":
                sla = 10

            elif description_two == "Customer tried to withdraw but the money wasn't delivered":
                sla = random.choice([15, 30])

            elif description_two == "Customer withdrawal, ABM didn't deliver the total amount requested":
                sla = random.choice([10, 30, 60])

        elif subcategory == "Local Non BNS ATM":
            description_two = "Customer tried to withdraw but the money wasn't delivered"
            sla = 15

        elif subcategory == "Local Offsite ABM":
            description_two = random.choice(["Deposit Error - Missing deposit", "Deposit Error - Partial deposit"])
            sla = 5

        elif subcategory == "Local Onsite ABM Deposit":
            description_two = random.choice(["Deposit Error - Missing deposit", "Deposit Error - Partial deposit"])
            sla = 5

        elif subcategory == "Local POS":
            description_two = random.choice([
                "Customer claims transaction was duplicated by the merchant",
                "Customer doesn't recognize transaction",
            ])

            sla = random.choice([15, 120, 95])

    elif category == "BSC - Corporate":
        subcategory = random.choice(["Checking Accounts", "Saving Accounts"])
        sla = 30

        if subcategory == "Checking Accounts":
            description_two = random.choice(["Debit / Credit Inquiry", "Identify Debit/Credit", "Reversal / Correction", "Reversal/Correction Tax 0.15", "Wire Investigation", "WIRE/RTGS Investigation"])

        elif subcategory == "Saving Accounts":
            description_two = random.choice(["Cheque Inquiry", "Identify Debit/Credit", "Reversal / Correction", "RTGS Recall", "Wire Investigation", "Wire Recall", "WIRE/RTGS Investigation"])

    elif category == "Debit Deposit Accounts":
        subcategory = "Unrecognized Debit/Credit"
        description_two = random.choice([
            "Customer claims has not yet recieved expected credit",
            "Customer does not recognize debit or credit",
            "Customer doesn't recognize credit on their account",
            "Customer doesn't recognize debit on their account"
        ])
        sla = 30

    elif category == "Disputes below USD50":
        subcategory = random.choice(["International POS", "Local POS"])
        sla = 5

        if subcategory == "International POS":
            description_two = "Customer doesn't recognize transaction"

        elif subcategory == "Local POS":
            description_two = random.choice([
                "Customer claims transaction was duplicated by the merchant",
                "Customer doesn't recognize transaction",
                "Investigation for credit not processed by Merchant",
                "Investigaton paid by other means",
                "Transaction cancelled by Merchant"
            ])

    elif category == "Electronic Transactions":
        subcategory =  random.choice(["Bill Payments", "INTL Wire Transfers", "Local Wire Transfers", "Third Party Transfers"])

        if subcategory == "Bill Payments":
            description_two = random.choice([
                "Bill payment remains unapplied",
                "Customer made a electronic transfer to pay a bill but was not recieved by company",
                "Customer selected the wrong vendor and wishes to recall the funds",
                "Customer transferred to an incorrect account, claims correction"
            ])
            sla = 30

        elif subcategory == "INTL Wire Transfers":
            description_two = random.choice([
                "Beneficiary claims non reciept of the funds, customer claims credit confirmation",
                "Customer requesting detail of charges",
                "Customer wishes to recall the funds",
                "Incoming OFAC confirmation"
            ])
            sla = 5

        elif subcategory == "Local Wire Transfers":
            description_two = random.choice([
                "Beneficiary claims non reciept of the funds, customer claims credit confirmation",
                "Customer requesting detail of charges",
                "Customer wishes to recall the funds",
                "Incoming OFAC confirmation"
            ])
            sla = 30

        elif subcategory == "Third Party Transfers":
            description_two = random.choice([
                "Customer made a electronic transfer to pay a bill but was not recieved by company",
                "Customer selected the wrong beneficiary and wishes to recall the funds",
                "Customer transferred to an incorrect account, claims correction",
                "Third Party Transfers remains unapplied"
            ])
            sla = 30

    elif category == "Personal Loan":
        subcategory = "LOAN ISSUES"
        description_two = random.choice(["Customer requests a loan review", "Payment applied/credited erroneously"])
        sla = 30

    elif category == "Regulatory":
        subcategory = "CBD Request"
        description_two = "Contract open s/b clsoed - Credit Card"
        sla = 12

    incident = Incident(
        env = env,
        incident_type = "Claims",
        product_type = None,
        category = category,
        subcategory = subcategory,
        description_two = description_two,
        service_level_agreement = sla,
        employee = employee
    )

    return incident

def create_complaint(env: simpy.Environment, employee: Employee):
    complaint_type = random.choice(["Insurance", "Product", "Service Issues"])

    if complaint_type == "Insurance":
        prod_channel = random.choice(["Chequing / Savings Account", "Credit Card"])
        
        if prod_channel == "Chequing / Savings Account":
            complaint_desc = "Transaction not recognized - Scotia Vida"
            sla = 5

        elif prod_channel == "Credit Card":
            complaint_desc = "Duplicate Transaction - Card and Account Protection (Fraud)"
            sla = 7

    elif complaint_type == "Product":
        prod_channel = "Chequing / Savings Account"
        complaint_desc = "Other"
        sla = 14

    elif complaint_type == "Service Issues":
        prod_channel = random.choice(["Contact Centre", "CRCU", "Retail Banking", "Small Business Banking"])
        
        if prod_channel == "Contact Centre":
            complaint_desc = "Customer information incorrect"
            sla = 21

        elif prod_channel == "CRCU":
            complaint_desc = random.choice([
                "Commitments not kept",
                "Processing delays resulting in financial losses to the customer"
            ])
            sla = 14

        elif prod_channel == "Retail Banking":
            complaint_desc = random.choice([
                "Charges misapplied / duplicated",
                "Processing delays resulting in financial losses to the customer"
            ])

            if complaint_desc == "Charges misapplied / duplicated":
                sla = 21

            elif complaint_desc == "Processing delays resulting in financial losses to the customer":
                sla = 14

        elif prod_channel == "Small Business Banking":
            complaint_desc = "Poor advice / Lack of knowledge"
            sla = 21

    incident = Incident(
        env = env,
        incident_type = "Complaints",
        complaint_type = complaint_type,
        complaint_description = complaint_desc,
        prod_channel = prod_channel,
        service_level_agreement = sla,
        employee = employee
    )

    return incident

def create_request(env: simpy.Environment, employee: Employee):
    category = random.choice([
        "Credit Card", "Insurance", "Merchant Services", "ACH Recalls", "Advice & Counsel", "Authorization Request", 
        "CFM Request", "Collections - CRCU", "Debit Deposit Accounts", "Digital letters - Contact Center only",
        "Electronics transactions", "Lending Service Unit (LSU)", "Letters", "Loan", "Maintenance & Amendment",
        "Maintenance Loans", "Manual Name Screening", "Processing Deposits", "Processing Loans",
        "Regulatory", "USD Draft", "Wires"
    ])
    description_two = None

    if category == "Credit Card":
        subcategory = random.choice(["Chargebacks", "Contact Center Request", "Non Monetary Maintenance", "Operations"])

        if subcategory == "Chargebacks":
            description_two = random.choice([
                "Client requests transaction investigation for duplicity", 
                "Client requests transcation investigation for fraud", 
                "Client requests transaction investigation for not recognizing", 
                "Client requests transaction investigation for service not dispensed",
                "Customer is requesting interest calculation",
                "Investigation for credit not processed by Merchant"
            ])
            sla = 120

        elif subcategory == "Contact Center Request":
            description_two = "CC / Statement Request"
            sla = 2

        elif subcategory == "Non Monetary Maintenance":
            description_two = random.choice([
                "Mant. CC / Additional", "Mant. CC / Bill Address", 
                "Mant. CC / Close (NA-Charge Off)", "Mant. CC / Credit Card Status Change",
                "Mant. CC / Credit Limit Distribution", "Mant. CC / Credit Limit Unification",
                "Mant. CC / General Maintenance", "Mant. CC / Insurance cancellation",
                "Mant. CC / Product Change / Upgrade", "Mant. CC / Replacement (General reasons)"
            ])

            if description_two == "Mant. CC / Additional" or description_two == "Mant. CC / Credit Limit Unification":
                sla = 5

            else:
                sla = 3

        elif subcategory == "Operations":
            description_two = random.choice([
                "Cards Movement", "Client requests clear balance (for closure)",
                "Client requests", "Client requests Payment application", 
                "Client requests points/cash back", "Client requests Reverse of Internal Charges",
                "Collection - Fixed Payment Plan Requests", "CUOTAS cash advance campaigns",
                "Customer is requesting Correction or Transfer of Payments",
                "Customer is requesting overpay reimbursement", "Installments - Acceleration",
                "Installments All Requests", "Write off Records request"
            ])
            sla = 3

    elif category == "Insurance":
        subcategory = "Insurance Cancellation"

        description_two = random.choice([
            "Checking Accounts/Card and Account Protection (Fraud)",
            "Credit Card/Card and Account Protection (Fraud)",
            "Credit Card/Fire Coverage (Individual)"
        ])
        sla = 5

    elif category == "Merchant Services":
        subcategory = random.choice(["Agency", "Credits", "Gift Cards", "Merchant Inquiries", "Merchant Maintenance", "Merchant Reports"])

        if subcategory == "Agency":
            description_two = random.choice(["Air Tickets", "Concert Tickets", "Cruise Ships", "Hotels", "Insurance", "Rent a Car", "Tourist Package"])
            sla = 10

        elif subcategory == "Credits":
            description_two = random.choice(["CC renovation retained customer", "Credit Card Credit", "Savings Account Credit"])
            sla = 3

        elif subcategory == "Gift Cards":
            description_two = random.choice(["Amazon Gift Card", "International", "Local", "Movie Tickets"])
            sla = 4

        elif subcategory == "Merchant Inquiries":
            description_two = random.choice(["Batch Payment", "Refund"])
            sla = 2

        elif subcategory == "Merchant Maintenance":
            description_two = random.choice(["Regular Data Modification", "Profile Data Modification"])

            if description_two == "Regular Data Modification":
                sla = 60

            elif description_two == "Profile Data Modification":
                sla = 3

        elif subcategory == "Merchant Reports":
            description_two = "Merchant Statement"
            sla = 2

    elif category == "ACH Recalls":
        subcategory = "ACH Recalls from Other Banks"
        description_two = "Online Banking Transfer"
        sla = 90

    elif category == "Advice & Counsel":
        subcategory = random.choice(["A&C-Advice & Counsel", "ABM Differences", "CH-Over Limit Reporting", "Monthly GL Certification", "MOS - Special Requests", "Teller Differences"])
        sla = 3

        if subcategory == "A&C-Advice & Counsel":
            description_two = "For guidance on policy, procedure and general information"

        elif subcategory == "ABM Differences":
            description_two = "Notify ABM Differences"

        elif subcategory == "CH-Over Limit Reporting":
            description_two = "Notify cash holding overlimit situation"

        elif subcategory == "Monthly GL Certification":
            description_two = "Submit Monthly GL Certification"

        elif subcategory == "MOS - Special Requests":
            description_two = "MOS special requests"
            sla = 5

        elif subcategory == "Teller Differences":
            description_two = "Notify Teller Differences"

    elif category == "Authorization Request":
        subcategory = random.choice(["CL-Write-Off", "Draft Replacement"])

        if subcategory == "CL-Write-Off":
            description_two = "Request authorization to write off cashlosses > USD$2,500.00"
            sla = 7

        elif subcategory == "Draft Replacement":
            description_two = "Replace draft replacement authorization"
            sla = 5

    elif category == "CFM Request":
        subcategory = random.choice(["CC - Card Unblock", "CC - Fraud", "CC - Fraud Declines", "CC Fraud Declines", "CC Suspect Compromise", "General Request"])
        sla = 3

        if subcategory == "CC - Card Unblock":
            description_two = "Unblock Card - Confirmed legitimate suspicious tx"

        elif subcategory == "CC - Fraud":
            description_two = "Report Fraud on Card"

        elif subcategory == "CC - Fraud Declines":
            description_two = "Apply Maintenance Due to Declines on Card"

        elif subcategory == "CC Fraud Declines":
            description_two = random.choice(["Advice messages not an approval decline", "ASSOC RTD Decline", "Do Not Honor Decline", "Falcon Decline", "MNP Decline", "Security Violation Decline"])
            sla = 1

        elif subcategory == "CC Suspect Compromise":
            description_two = "Remove block, customer confirms legitimate transaction"
            sla = 1

        elif subcategory == "General Request":
            description_two = "General Request"

    elif category == "Collections - CRCU":
        subcategory = random.choice(["Credit Bureau", "Letters", "Mitigation Tools (LMT)", "Opposition Lifting / Vehicle and Mortage"])

        if subcategory == "Credit Bureau":
            description_two = "Credit Bureau Update according to our system"
            sla = 30

        elif subcategory == "Letters":
            description_two = random.choice(["Certification of debt letter", "Credit Card balance letter", "Loan payout letter"])
            sla = 30

        elif subcategory == "Mitigation Tools (LMT)":
            description_two = random.choice(["ADP", "Debt Consolidation"])

            if description_two == "ADP":
                sla = 2

            elif description_two == "Debt Consolidation":
                sla = 15

        elif subcategory == "Opposition Lifting / Vehicle and Mortage":
            description_two = "Review credit bureau and update system"
            sla = random.choice([1, 2, 4])

    elif category == "Debit Deposit Accounts":
        subcategory = random.choice(["Account Closure", "Contact Center Request", "Taxes", "Unrecognized Debit/Credit"])

        if subcategory == "Account Closure":
            description_two = "Account Closure"
            sla = 3

        elif subcategory == "Contact Center Request":
            description_two = random.choice(["Add permanent order", "DDA / Statement Request", "Eliminate permanent order", "Request to unify Cifkey"])
            sla = 2

        elif subcategory == "Taxes":
            description_two = random.choice(["Request Tax Receipts", "Reverse tax 0.15% per transfer"])
            sla = 2
        
        elif subcategory == "Unrecognized Debit/Credit":
            description_two = "Customer does not recognize debit or credit"
            sla = 5

    elif category == "Digital letters - Contact Center only":
        subcategory = random.choice(["Consular or reference letter", "Credit Card pay-out letter", "Loan pay-out letter"])
        description_two = "Letter in spanish"
        sla = 2

    elif category == "Electronics transactions":
        subcategory = random.choice(["INTL Wire Transfers", "Local Wire Transfers"])
        sla = 5
        
        if subcategory == "INTL Wire Transfers":
            description_two = random.choice([
                "Incoming Wire Credit Confirmation required. Customer expecting funds and claims non-receipt",
                "Incoming Wire-Customer requests details of charges",
                "Outgoing Wire-Customer requests copy of one/various SWIFT Acknowledgements",
                "Outgoing Wire-Request for confirmation of release/status, Benificiary claims non receipt"
            ])

        elif subcategory == "Local Wire Transfers":
            description_two = random.choice([
                "Incoming Wire Credit Confirmation required. Customer expecting funds and claims non-receipt",
                "Incoming Wire-Customer requests details of charges",
                "Outgoing Wire-Request for confirmation of release/status, Benificiary claims non receipt"
            ])

    elif category == "Lending Service Unit (LSU)":
        subcategory = "Letters"
        description_two = "Customer Requests a Mortage Radiation"
        sla = 2

    elif category == "Letters":
        subcategory = "Letters"
        description_two = "Reference Letter"
        sla = 2

    elif category == "Loan":
        subcategory = "Request"
        description_two = random.choice(["Amortization Table", "Loan History", "Request Tax Receipts"])
        sla = 5

    elif category == "Maintenance & Amendment":
        subcategory = random.choice(["Loan Amendment", "SPL Maintenance"])

        if subcategory == "Loan Amendment":
            description_two = random.choice(["Principal Payment", "Rate Change"])
            sla = 15

        elif subcategory == "SPL Maintenance":
            description_two = "Payment Date Change"
            sla = 3

    elif category == "Maintenance Loans":
        subcategory = "Loan Maintenance"
        description_two = "Loan status changes"
        sla = 5

    elif category == "Manual Name Screening":
        subcategory = "World Check Validation"
        description_two = random.choice(["Individual", "Business"])

        if description_two == "Individual":
            sla = 1

        elif description_two == "Business":
            sla = 8

    elif category == "Processing Deposits":
        subcategory = random.choice(["Customer reimbursement", "IBA", "MICR processing"])
        sla = 5

        if subcategory == "Customer reimbursement":
            description_two = "Customer claims reimbursement"

        elif subcategory == "IBA":
            description_two = "Inter branch remittance"

        elif subcategory == "MICR processing":
            description_two = "Bulk processing of entries"

    elif category == "Processing Loans":
        subcategory = random.choice(["Loan Amendment", "Loan Payments", "Loan Entries", "POS Virtual"])
        sla = 5

        if subcategory == "Loan Amendment":
            description_two = "Loan Amendment"

        elif subcategory == "Loan Payments":
            description_two = "Loan payments and reversals"

        elif subcategory == "Loan Entries":
            description_two = "Loans monetary entries"

        elif subcategory == "POS Virtual":
            description_two = "CRCU customer payments via POS"

    elif category == "Regulatory":
        subcategory = "Regulatory"
        description_two = random.choice(["PRO Usuario - Data Certification", "SIB - Information Requirements"])
        sla = 30

    elif category == "USD Draft":
        subcategory = "Validate"
        description_two = "Single Payee"
        sla = 1

    elif category == "Wires":
        subcategory = "Processing"
        description_two = "Process Payment/Message as per instruction"
        sla = 5

    incident = Incident(
        env = env,
        incident_type = "Requests",
        category = category,
        subcategory = subcategory,
        description_two = description_two,
        service_level_agreement = sla,
        employee = employee
    )

    return incident