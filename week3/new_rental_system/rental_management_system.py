"""
=============================================================
  NAIJA PROPERTY MANAGER
  Nigerian Property Rental Management System
  Week 4 Project — Decorators, Generator, Context Manager
=============================================================
"""

from enum import Enum
from datetime import date, datetime
import functools, os, sys


# ── Colours ──────────────────────────────────────────────────
class C:
    RESET  = "\033[0m";  BOLD  = "\033[1m"
    GREEN  = "\033[92m"; RED   = "\033[91m"
    YELLOW = "\033[93m"; CYAN  = "\033[96m"
    BLUE   = "\033[94m"; GREY  = "\033[90m"
    WHITE  = "\033[97m"

# ── Display helpers ───────────────────────────────────────────
def clr():      os.system("cls" if os.name == "nt" else "clear")
def pause():    input(f"\n  {C.GREY}Press Enter to continue...{C.RESET}")
def success(m): print(f"  {C.GREEN}✓  {m}{C.RESET}")
def error(m):   print(f"  {C.RED}✗  {m}{C.RESET}")
def warn(m):    print(f"  {C.YELLOW}⚠  {m}{C.RESET}")
def info(m):    print(f"  {C.GREY}ℹ  {m}{C.RESET}")
def divider():  print(f"  {C.GREY}{'─' * 54}{C.RESET}")

def banner(title, subtitle=""):
    print(f"\n{C.CYAN}{'═' * 58}{C.RESET}")
    print(f"{C.BOLD}{C.WHITE}  {title}{C.RESET}")
    if subtitle: print(f"{C.GREY}  {subtitle}{C.RESET}")
    print(f"{C.CYAN}{'═' * 58}{C.RESET}\n")

def section(title):
    print(f"\n{C.BLUE}  ── {title} {'─' * (48 - len(title))}{C.RESET}")


# ── Input helpers ─────────────────────────────────────────────
def get_input(prompt, required=True):
    while True:
        val = input(f"  {C.CYAN}▶ {prompt}: {C.RESET}").strip()
        if val: return val
        if not required: return ""
        error("This field cannot be empty.")

def get_text_only(prompt, required=True):
    while True:
        val = input(f"  {C.CYAN}▶ {prompt}: {C.RESET}").strip()
            
        # Handle empty inputs based on the 'required' flag
        if not val:
            if not required: 
                return ""
            error("This field cannot be empty.")
            continue

        # Reject if it contains any numbers
        if any(char.isdigit() for char in val):
            error("Numbers are not allowed. Please enter text only.")
            continue
            
        # Ensure it actually contains letters (prevents inputs like "-' ")
        if not any(char.isalpha() for char in val):
            error("Input must contain valid letters.")
            continue
            
        return val

def get_int(prompt, min_val=None, max_val=None):
    while True:
        raw = input(f"  {C.CYAN}▶ {prompt}: {C.RESET}").strip()
        try:
            val = int(raw)
            if min_val is not None and val < min_val:
                error(f"Enter at least {min_val}."); continue
            if max_val is not None and val > max_val:
                error(f"Enter no more than {max_val}."); continue
            return val
        except ValueError:
            error(f"'{raw}' is not a valid number.")

def get_float(prompt, min_val=0.01):
    while True:
        raw = input(f"  {C.CYAN}▶ {prompt}: {C.RESET}").strip().replace(",", "")
        try:
            val = float(raw)
            if val < min_val: error(f"Must be at least ₦{min_val:,.2f}."); continue
            return val
        except ValueError:
            error(f"'{raw}' is not a valid amount.")

def get_date(prompt, allow_future=True, allow_past=True):
    while True:
        raw = input(f"  {C.CYAN}▶ {prompt} (YYYY-MM-DD): {C.RESET}").strip()
        try:
            d = datetime.strptime(raw, "%Y-%m-%d").date()
            if not allow_future and d > date.today(): error("Date cannot be in the future."); continue
            if not allow_past  and d < date.today(): error("Date cannot be in the past.");   continue
            return d
        except ValueError:
            error(f"Use format YYYY-MM-DD  e.g. 2024-01-15")

def get_bool(prompt):
    while True:
        raw = input(f"  {C.CYAN}▶ {prompt} (y/n): {C.RESET}").strip().lower()
        if raw in ("y", "yes"): return True
        if raw in ("n", "no"):  return False
        error("Type 'y' or 'n'.")

def get_choice(options, prompt="Enter your choice"):
    for i, opt in enumerate(options, 1):
        print(f"    {C.YELLOW}[{i}]{C.RESET}  {opt}")
    return options[get_int(prompt, min_val=1, max_val=len(options)) - 1]

def pick_from(label, items, display_fn=str):
    if not items: warn(f"No {label} found."); return None
    section(f"Select {label}")
    options = [display_fn(i) for i in items] + ["Cancel"]
    chosen  = get_choice(options)
    if chosen == "Cancel": return None
    return items[options.index(chosen)]

def get_exact_digits(prompt, exact_length):
    """Ensures input is entirely numeric and matches a specific length."""
    while True:
        val = input(f"  {C.CYAN}▶ {prompt} ({exact_length} digits): {C.RESET}").strip()
        
        if not val.isdigit():
            error("This field must contain ONLY numbers (no letters or spaces).")
            continue
            
        if len(val) != exact_length:
            error(f"Must be exactly {exact_length} digits. You entered {len(val)}.")
            continue
            
        return val


# ── Enums ──────────────────────────────────────────────────────
class Priority(Enum):
    LOW = 1; MEDIUM = 2; HIGH = 3

class PropertyStatus(Enum):
    AVAILABLE = "available"; PENDING = "pending"
    OCCUPIED  = "occupied";  SUSPENDED = "suspended"

class LeaseStatus(Enum):
    ACTIVE = "active"; EXPIRED = "expired"; TERMINATED = "terminated"

class PaymentStatus(Enum):
    ON_TIME = "on_time"; LATE = "late"; DEFAULTED = "defaulted"


# =============================================================
# WEEK 4 REQUIREMENT 1 — @validate_positive decorator
# Blocks any payment method if amount is zero or negative.
# =============================================================
def validate_positive(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        # args[0]=self, args[1]=amount for methods
        amount = kwargs.get("amount", args[1] if len(args) > 1 and not isinstance(args[0], (int, float)) else args[0] if args else None)
        if not isinstance(amount, (int, float)):
            raise TypeError("Amount must be a number.")
        if amount <= 0:
            raise ValueError(f"Amount must be positive. Got ₦{amount:,.2f}.")
        return func(*args, **kwargs)
    return wrapper


# =============================================================
# WEEK 4 REQUIREMENT 2 — @requires_role decorator (with args)
# Restricts methods to specific user roles (Landlord / Agent).
# =============================================================
def requires_role(*allowed_roles):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(self, caller, *args, **kwargs):
            if type(caller).__name__ not in allowed_roles:
                raise PermissionError(
                    f"Only {' or '.join(allowed_roles)} can do this. "
                    f"You are a {type(caller).__name__}."
                )
            return func(self, caller, *args, **kwargs)
        return wrapper
    return decorator


# ── Penalty Calculator ────────────────────────────────────────
class PenaltyCalculator:
    DUE_DAY = 1; GRACE_DAYS = 3; RATE = 0.05

    @staticmethod
    def compute(date_paid, monthly_rent):
        days_late = date_paid.day - PenaltyCalculator.DUE_DAY
        if days_late <= PenaltyCalculator.GRACE_DAYS: return 0.0
        return round(PenaltyCalculator.RATE * monthly_rent, 2)

    @staticmethod
    def classify(date_paid, due_date):
        days_late = (date_paid - due_date).days
        if days_late <= PenaltyCalculator.GRACE_DAYS: return PaymentStatus.ON_TIME
        if days_late <= 30:                           return PaymentStatus.LATE
        return PaymentStatus.DEFAULTED


# ── Person hierarchy ──────────────────────────────────────────
class Person:
    def __init__(self, name, phone, national_id):
        self.name = name; self.phone = phone; self.national_id = national_id

    def __repr__(self): return f"<{type(self).__name__}: {self.name}>"
    def display(self):  return f"{self.name}  |  {self.phone}"


class Landlord(Person):
    def __init__(self, name, phone, national_id, tax_id, bank_account):
        super().__init__(name, phone, national_id)
        self.tax_id = tax_id; self.bank_account = bank_account
        self.properties = []

    def display(self):
        n = len(self.properties)
        return f"{self.name}  |  {self.phone}  |  {n} propert{'ies' if n != 1 else 'y'}"

    # =========================================================
    # WEEK 4 REQUIREMENT 3 — Generator
    # Yields overdue payments one at a time (memory efficient).
    # =========================================================
    def overdue_payments(self):
        for prop in self.properties:
            for lease in prop.leases:
                for payment in lease.payments:
                    if payment.status in (PaymentStatus.LATE, PaymentStatus.DEFAULTED):
                        yield payment   # pauses here, resumes on next request


class Tenant(Person):
    def __init__(self, name, phone, national_id, occupation, guarantor=None):
        super().__init__(name, phone, national_id)
        self.occupation = occupation; self.guarantor = guarantor

    def display(self): return f"{self.name}  |  {self.occupation}  |  {self.phone}"


class Agent(Person):
    def __init__(self, name, phone, national_id, agency_name, licence_no, commission_rate=0.10):
        super().__init__(name, phone, national_id)
        self.agency_name = agency_name; self.licence_no = licence_no
        self.commission_rate = commission_rate

    def display(self): return f"{self.name}  |  {self.agency_name}  |  {self.phone}"


# ── Mandate (Agent ↔ Landlord agreement) ─────────────────────
class Mandate:
    def __init__(self, landlord, agent, properties, start_date, end_date):
        self.landlord = landlord; self.agent = agent
        self.properties = properties
        self.start_date = start_date; self.end_date = end_date

    def is_active(self): return self.start_date <= date.today() <= self.end_date

    def display(self):
        status = "ACTIVE" if self.is_active() else "EXPIRED"
        return f"{self.agent.name} manages for {self.landlord.name}  |  {status}  |  {self.start_date} → {self.end_date}"


# ── Property hierarchy ────────────────────────────────────────
class Property:
    def __init__(self, address, size_sqm, monthly_rent, landlord):
        self.address = address; self.size_sqm = size_sqm
        self.monthly_rent = monthly_rent; self.landlord = landlord
        self.status = PropertyStatus.AVAILABLE
        self.leases = []; self.maintenance = []
        landlord.properties.append(self)   # auto-register under landlord

    @property
    def is_available(self):
        # Computed dynamically — never stored, never stale
        if self.status != PropertyStatus.AVAILABLE: return False
        return not any(l.is_active() for l in self.leases)

    def active_lease(self):
        return next((l for l in self.leases if l.is_active()), None)

    @requires_role("Landlord", "Agent")   # Week 4 Req 2 applied here
    def terminate_lease(self, caller, lease):
        if lease not in self.leases:          raise ValueError("Lease not found on this property.")
        if lease.status != LeaseStatus.ACTIVE: raise ValueError(f"Lease is already {lease.status.value}.")
        lease.status = LeaseStatus.TERMINATED
        self.status  = PropertyStatus.AVAILABLE
        success(f"Lease for {lease.tenant.name} terminated by {caller.name}.")

    def summary_line(self): return f"{self.address}  |  ₦{self.monthly_rent:,.0f}/mo  |  {self.status.value}"
    def display(self):
        a = f"{C.GREEN}Available{C.RESET}" if self.is_available else f"{C.RED}Not Available{C.RESET}"
        return f"{self.address}  |  ₦{self.monthly_rent:,.0f}/mo  |  {self.status.value}  |  {a}"
    def __repr__(self): return f"<{type(self).__name__}: {self.address}>"


class Flat(Property):
    def __init__(self, address, size_sqm, monthly_rent, landlord, num_bedrooms, floor_number):
        super().__init__(address, size_sqm, monthly_rent, landlord)
        self.num_bedrooms = num_bedrooms; self.floor_number = floor_number

    def summary_line(self):
        return f"[FLAT] {self.address}  |  {self.num_bedrooms} bed  |  Floor {self.floor_number}  |  ₦{self.monthly_rent:,.0f}/mo  |  {self.status.value}"


class Duplex(Property):
    def __init__(self, address, size_sqm, monthly_rent, landlord, num_floors, has_bq):
        super().__init__(address, size_sqm, monthly_rent, landlord)
        self.num_floors = num_floors; self.has_bq = has_bq

    def summary_line(self):
        bq = "with BQ" if self.has_bq else "no BQ"
        return f"[DUPLEX] {self.address}  |  {self.num_floors} floors  |  {bq}  |  ₦{self.monthly_rent:,.0f}/mo  |  {self.status.value}"


class SelfContain(Property):
    def summary_line(self):
        return f"[SELF-CONTAIN] {self.address}  |  ₦{self.monthly_rent:,.0f}/mo  |  {self.status.value}"


class Shop(Property):
    def __init__(self, address, size_sqm, monthly_rent, landlord, frontage_size, business_category):
        super().__init__(address, size_sqm, monthly_rent, landlord)
        self.frontage_size = frontage_size; self.business_category = business_category

    def summary_line(self):
        return f"[SHOP] {self.address}  |  {self.business_category}  |  ₦{self.monthly_rent:,.0f}/mo  |  {self.status.value}"


class Warehouse(Property):
    def __init__(self, address, size_sqm, monthly_rent, landlord, loading_bays, has_cold_storage=False):
        super().__init__(address, size_sqm, monthly_rent, landlord)
        self.loading_bays = loading_bays; self.has_cold_storage = has_cold_storage

    def summary_line(self):
        cold = "Cold storage" if self.has_cold_storage else "Dry storage"
        return f"[WAREHOUSE] {self.address}  |  {self.loading_bays} bays  |  {cold}  |  ₦{self.monthly_rent:,.0f}/mo  |  {self.status.value}"


# =============================================================
# WEEK 4 REQUIREMENT 4 — Context Manager (LeaseSigning)
# Locks property as PENDING during signing.
# Rolls back to AVAILABLE automatically if anything fails.
# =============================================================
class LeaseSigning:
    def __init__(self, tenant, prop):
        self.tenant = tenant; self.prop = prop; self.lease = None

    def __enter__(self):
        if not self.prop.is_available:
            raise ValueError(f"'{self.prop.address}' is {self.prop.status.value} — cannot be booked.")
        self.prop.status = PropertyStatus.PENDING
        warn(f"'{self.prop.address}' is now PENDING — signing in progress...")
        return self

    def sign(self, start_date, end_date, rent_amount):
        if start_date >= end_date: raise ValueError("Start date must be before end date.")
        if rent_amount <= 0:       raise ValueError("Rent amount must be positive.")
        self.lease = LeaseAgreement(self.tenant, self.prop, start_date, end_date, rent_amount)
        self.prop.status = PropertyStatus.OCCUPIED
        return self.lease

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            self.prop.status = PropertyStatus.AVAILABLE   # ROLLBACK
            error(f"Signing failed: {exc_val}")
            warn(f"'{self.prop.address}' rolled back to AVAILABLE.")
        return False   # do not suppress the error


# ── LeaseAgreement ────────────────────────────────────────────
class LeaseAgreement:
    def __init__(self, tenant, prop, start_date, end_date, rent_amount):
        self.tenant = tenant; self.property = prop
        self.start_date = start_date; self.end_date = end_date
        self.rent_amount = rent_amount
        self.status = LeaseStatus.ACTIVE; self.payments = []
        prop.leases.append(self)   # auto-register on property

    def is_active(self):
        return self.status == LeaseStatus.ACTIVE and self.start_date <= date.today() <= self.end_date

    @validate_positive   # Week 4 Req 1 applied here
    def record_payment(self, amount, date_paid=None):
        if date_paid is None: date_paid = date.today()
        payment = RentPayment(self, amount, date_paid)
        self.payments.append(payment)
        return payment

    def display(self):
        return f"{self.tenant.name}  →  {self.property.address}  |  {self.start_date} to {self.end_date}  |  ₦{self.rent_amount:,.0f}/mo  |  {self.status.value}"

    def __repr__(self): return f"<LeaseAgreement: {self.tenant.name} @ {self.property.address}>"


# ── RentPayment ───────────────────────────────────────────────
class RentPayment:
    def __init__(self, lease, amount, date_paid):
        self.lease = lease; self.amount = amount; self.date_paid = date_paid
        self.penalty = PenaltyCalculator.compute(date_paid, lease.rent_amount)
        self.status  = PenaltyCalculator.classify(date_paid, date_paid.replace(day=1))

    def display(self):
        col         = C.GREEN if self.status == PaymentStatus.ON_TIME else C.RED
        penalty_str = f"  Penalty: ₦{self.penalty:,.2f}" if self.penalty > 0 else ""
        return f"₦{self.amount:,.2f}  paid on {self.date_paid}  |  {col}{self.status.value}{C.RESET}{penalty_str}"

    def __repr__(self): return f"<RentPayment: ₦{self.amount:,.2f} | {self.date_paid} | {self.status.value}>"


# ── MaintenanceRequest ────────────────────────────────────────
class MaintenanceRequest:
    def __init__(self, tenant, prop, issue, priority):
        self.tenant = tenant; self.property = prop
        self.issue = issue; self.priority = priority
        self.status = "open"; self.date_logged = date.today()
        prop.maintenance.append(self)   # auto-register on property

    def resolve(self):
        self.status = "resolved"

    def display(self):
        col = {Priority.HIGH: C.RED, Priority.MEDIUM: C.YELLOW, Priority.LOW: C.GREEN}.get(self.priority, C.GREY)
        st  = f"{C.GREEN}Resolved{C.RESET}" if self.status == "resolved" else f"{C.YELLOW}Open{C.RESET}"
        return f"{col}[{self.priority.name}]{C.RESET}  {self.issue}  |  {self.tenant.name}  |  {self.date_logged}  |  {st}"


# ── AppState (session memory) ─────────────────────────────────
class AppState:
    def __init__(self):
        self.landlords = []; self.tenants = []; self.agents = []
        self.properties = []; self.leases = []; self.mandates = []
        self.current_user = None

state = AppState()


# =============================================================
# SCREEN FUNCTIONS
# =============================================================

def screen_welcome():
    clr()
    print(f"""
{C.CYAN}╔══════════════════════════════════════════════════════╗
║                                                      ║
║   {C.BOLD}{C.WHITE}🏠  NAIJA PROPERTY MANAGER{C.CYAN}                       ║
║                                                      ║
║   {C.GREY}Nigerian Property Rental Management System{C.CYAN}          ║
║   {C.GREY}Lagos · Abuja · Port Harcourt · Benin · Ibadan{C.CYAN}     ║
║                                                      ║
╠══════════════════════════════════════════════════════╣
║                                                      ║
║  {C.GREEN}✓{C.CYAN}  Manage property listings                          ║
║  {C.GREEN}✓{C.CYAN}  Track tenant lease agreements                      ║
║  {C.GREEN}✓{C.CYAN}  Record rent payments & late penalties               ║
║  {C.GREEN}✓{C.CYAN}  Handle maintenance complaints                       ║
║  {C.GREEN}✓{C.CYAN}  Generate financial reports                          ║
║                                                      ║
╚══════════════════════════════════════════════════════╝{C.RESET}
""")
    input(f"  {C.GREY}Press Enter to get started...{C.RESET}")


def screen_role_select():
    clr()
    banner("Who are you?", "Select your role to continue")
    print(f"  {C.YELLOW}[1]{C.RESET}  🏛️   Landlord   — manage your properties & tenants")
    print(f"  {C.YELLOW}[2]{C.RESET}  🤝   Agent      — manage properties on behalf of a landlord")
    print(f"  {C.YELLOW}[3]{C.RESET}  🏡   Tenant     — view your lease & submit requests")
    print(f"  {C.YELLOW}[4]{C.RESET}  👤   New User   — register for the first time")
    print(f"  {C.YELLOW}[0]{C.RESET}  ❌   Exit\n")
    while True:
        choice = input(f"  {C.CYAN}▶ Enter choice: {C.RESET}").strip()
        if   choice == "1": return screen_login("Landlord")
        elif choice == "2": return screen_login("Agent")
        elif choice == "3": return screen_login("Tenant")
        elif choice == "4": return screen_register()
        elif choice == "0": screen_goodbye()
        else: error("Please enter 1, 2, 3, 4, or 0.")


def screen_login(role):
    clr(); banner(f"Login as {role}")
    pool = {"Landlord": state.landlords, "Tenant": state.tenants, "Agent": state.agents}[role]
    if not pool:
        warn(f"No {role}s registered yet.")
        return screen_register(default_role=role) if get_bool(f"Register as a {role} now?") else None
    section("Select your name")
    for i, p in enumerate(pool, 1): print(f"    {C.YELLOW}[{i}]{C.RESET}  {p.display()}")
    print(f"    {C.YELLOW}[0]{C.RESET}  Go back\n")
    choice = get_int("Enter number", min_val=0, max_val=len(pool))
    if choice == 0: return None
    state.current_user = pool[choice - 1]
    success(f"Welcome back, {state.current_user.name}!")
    pause(); return state.current_user


def screen_register(default_role=None):
    clr(); banner("New User Registration")
    role = default_role or (section("What is your role?") or get_choice(["Landlord", "Tenant", "Agent"]))
    if default_role: info(f"Registering as: {role}")
    
    section("Personal Details")
    name = get_text_only("Full name")
    
    # Applied strict digit length validations here
    phone       = get_exact_digits("Phone number", 11)
    national_id = get_exact_digits("NIN / National ID", 11)

    if role == "Landlord":
        tax_id       = get_exact_digits("Tax ID (TIN)", 13)
        bank_account = get_exact_digits("Bank account", 10)
        person = Landlord(name, phone, national_id, tax_id, bank_account)
        state.landlords.append(person)
        
    elif role == "Tenant":
        
        g = get_text_only("Guarantor name (optional)", required=False)
        person = Tenant(name, phone, national_id, get_input("Occupation"), g or None)
        state.tenants.append(person)
        
    elif role == "Agent":
        person = Agent(name, phone, national_id, get_input("Agency name"), get_input("Licence number"),
                       get_float("Commission rate (e.g. 0.10)"))
        state.agents.append(person)

    state.current_user = person
    print(); success(f"Registration successful! Welcome, {person.name}."); pause()
    return person


def screen_main_menu():
    user = state.current_user
    role = type(user).__name__
    while True:
        clr()
        banner(f"Main Menu  —  {user.name}", f"Logged in as {role}  ·  {date.today().strftime('%A, %d %B %Y')}")
        if role == "Landlord":
            options = [("1","🏠","My Properties","View, add & manage your listings"),
                       ("2","📋","Lease Agreements","Sign, view and terminate leases"),
                       ("3","💰","Rent Payments","Record payments & view history"),
                       ("4","🔧","Maintenance Requests","View and resolve complaints"),
                       ("5","📊","Financial Report","Overdue payments & summary"),
                       ("6","🤝","Agents & Mandates","Assign agents to your properties"),
                       ("7","📈","Analytics Dashboard","Export CSV & generate Pandas charts"),
                       ("0","🚪","Logout","Return to login screen")]
        elif role == "Agent":
            options = [("1","🏠","Properties I Manage","Properties under your mandates"),
                       ("2","📋","Lease Agreements","Sign and terminate leases"),
                       ("3","💰","Rent Payments","Record and view payments"),
                       ("4","🔧","Maintenance Requests","View and resolve complaints"),
                       ("0","🚪","Logout","Return to login screen")]
        else:
            options = [("1","📋","My Lease","View your current lease"),
                       ("2","💰","My Payments","View your payment history"),
                       ("3","🔧","Submit Maintenance Request","Report a problem"),
                       ("0","🚪","Logout","Return to login screen")]

        for key, icon, title, desc in options:
            print(f"  {C.YELLOW}[{key}]{C.RESET}  {icon}  {C.BOLD}{title}{C.RESET}")
            print(f"         {C.GREY}{desc}{C.RESET}\n")

        choice = input(f"  {C.CYAN}▶ Enter choice: {C.RESET}").strip()
        if role == "Landlord":
            actions = {"1": screen_properties, "2": screen_leases, "3": screen_payments,
                       "4": screen_maintenance, "5": screen_report, "6": screen_mandates,
                       "7": screen_analytics_dashboard}
        elif role == "Agent":
            actions = {"1": screen_agent_properties, "2": screen_leases,
                       "3": screen_payments, "4": screen_maintenance}
        else:
            actions = {"1": screen_tenant_lease, "2": screen_tenant_payments, "3": screen_submit_maintenance}

        if choice == "0": return
        elif choice in actions: actions[choice]()
        else: error("Invalid choice."); pause()


# ── Properties ────────────────────────────────────────────────
def screen_properties():
    user = state.current_user
    while True:
        clr(); banner("My Properties", f"{len(user.properties)} total")
        if not user.properties:
            warn("No properties added yet.")
        else:
            for i, p in enumerate(user.properties, 1):
                tag = f"{C.GREEN}[Available]{C.RESET}" if p.is_available else f"{C.RED}[Not Available]{C.RESET}"
                print(f"  {C.YELLOW}[{i}]{C.RESET}  {p.summary_line()}  {tag}")
            print()
        print(f"  {C.YELLOW}[A]{C.RESET}  ➕  Add a new property")
        print(f"  {C.YELLOW}[V]{C.RESET}  🔍  View property details")
        print(f"  {C.YELLOW}[S]{C.RESET}  ⏸️   Suspend / unsuspend a property")
        print(f"  {C.YELLOW}[0]{C.RESET}  ←   Back\n")
        choice = input(f"  {C.CYAN}▶ Enter choice: {C.RESET}").strip().upper()
        if   choice == "A": screen_add_property()
        elif choice == "V": screen_view_property()
        elif choice == "S": screen_suspend_property()
        elif choice == "0": return
        else: error("Invalid choice."); pause()


def screen_add_property():
    clr(); banner("Add New Property")
    section("Property Type")
    prop_type = get_choice(["Flat", "Duplex", "Self-Contain", "Shop", "Warehouse"])
    section("Property Details")
    address = get_input("Full property address")
    size    = get_float("Size in square metres (sqm)")
    rent    = get_float("Monthly rent amount (₦)")
    ll      = state.current_user

    if   prop_type == "Flat":        prop = Flat(address, size, rent, ll, get_int("Bedrooms", 1, 10), get_int("Floor number", 0, 50))
    elif prop_type == "Duplex":      prop = Duplex(address, size, rent, ll, get_int("Number of floors", 2, 5), get_bool("Has Boys Quarters (BQ)?"))
    elif prop_type == "Self-Contain":prop = SelfContain(address, size, rent, ll)
    elif prop_type == "Shop":        prop = Shop(address, size, rent, ll, get_float("Frontage size (metres)"), get_input("Business category"))
    elif prop_type == "Warehouse":   prop = Warehouse(address, size, rent, ll, get_int("Loading bays", 1), get_bool("Has cold storage?"))

    state.properties.append(prop)
    print(); success(f"{prop_type} added: {address}"); info(f"Rent: ₦{rent:,.2f}/mo"); pause()


def screen_view_property():
    clr(); prop = pick_from("property", state.current_user.properties, lambda p: p.summary_line())
    if not prop: pause(); return
    clr(); banner("Property Details")
    section("Basic Info")
    print(f"  Address      : {C.WHITE}{prop.address}{C.RESET}")
    print(f"  Type         : {type(prop).__name__}")
    print(f"  Size         : {prop.size_sqm} sqm")
    print(f"  Monthly Rent : {C.GREEN}₦{prop.monthly_rent:,.2f}{C.RESET}")
    print(f"  Status       : {prop.status.value.upper()}")
    print(f"  Available    : {'Yes' if prop.is_available else 'No'}")
    if isinstance(prop, Flat):
        print(f"  Bedrooms     : {prop.num_bedrooms}"); print(f"  Floor        : {prop.floor_number}")
    elif isinstance(prop, Duplex):
        print(f"  Floors       : {prop.num_floors}"); print(f"  Boys Quarters: {'Yes' if prop.has_bq else 'No'}")
    elif isinstance(prop, Shop):
        print(f"  Frontage     : {prop.frontage_size}m"); print(f"  Business     : {prop.business_category}")
    elif isinstance(prop, Warehouse):
        print(f"  Loading Bays : {prop.loading_bays}"); print(f"  Cold Storage : {'Yes' if prop.has_cold_storage else 'No'}")
    active = prop.active_lease()
    section("Current Lease")
    if active:
        print(f"  Tenant       : {C.WHITE}{active.tenant.name}{C.RESET}  ({active.tenant.phone})")
        print(f"  Period       : {active.start_date}  →  {active.end_date}")
        print(f"  Rent         : ₦{active.rent_amount:,.2f}/mo")
        days = (active.end_date - date.today()).days
        col  = C.RED if days < 30 else C.YELLOW if days < 90 else C.GREEN
        print(f"  Days Left    : {col}{days}{C.RESET}")
    else:
        info("No active lease.")
    section(f"Maintenance  ({len(prop.maintenance)} total)")
    open_m = [m for m in prop.maintenance if m.status == "open"]
    for m in open_m[:5]: print(f"  {m.display()}")
    if not open_m: info("No open maintenance requests.")
    pause()


def screen_suspend_property():
    clr(); prop = pick_from("property", state.current_user.properties, lambda p: p.summary_line())
    if not prop: pause(); return
    clr(); banner("Suspend / Unsuspend Property")
    print(f"  Property : {prop.address}\n  Status   : {prop.status.value}\n")
    if prop.status == PropertyStatus.SUSPENDED:
        if get_bool("Restore to Available?"):
            prop.status = PropertyStatus.AVAILABLE; success("Property is now Available.")
    elif prop.active_lease():
        error("Cannot suspend — property has an active lease.")
    else:
        if get_bool("Suspend this property?"):
            prop.status = PropertyStatus.SUSPENDED; warn("Property suspended.")
    pause()


# ── Leases ────────────────────────────────────────────────────
def _get_leases():
    user = state.current_user; role = type(user).__name__
    if role == "Landlord": return [l for p in user.properties for l in p.leases]
    if role == "Agent":    return [l for p in _agent_properties() for l in p.leases]
    return []

def screen_leases():
    while True:
        clr(); banner("Lease Agreements")
        all_leases = _get_leases()
        if not all_leases:
            warn("No lease agreements found.")
        else:
            for i, l in enumerate(all_leases, 1):
                tag = f"{C.GREEN}[ACTIVE]{C.RESET}" if l.is_active() else f"{C.GREY}[{l.status.value}]{C.RESET}"
                print(f"  {C.YELLOW}[{i}]{C.RESET}  {l.display()}  {tag}")
            print()
        print(f"  {C.YELLOW}[N]{C.RESET}  📝  Sign a new lease")
        print(f"  {C.YELLOW}[T]{C.RESET}  ❌  Terminate a lease")
        print(f"  {C.YELLOW}[0]{C.RESET}  ←   Back\n")
        choice = input(f"  {C.CYAN}▶ Enter choice: {C.RESET}").strip().upper()
        if   choice == "N": screen_sign_lease()
        elif choice == "T": screen_terminate_lease()
        elif choice == "0": return
        else: error("Invalid choice."); pause()


def screen_sign_lease():
    clr(); banner("Sign New Lease Agreement")
    user = state.current_user; role = type(user).__name__
    available = [p for p in (user.properties if role == "Landlord" else _agent_properties()) if p.is_available]
    if not available:
        warn("No available properties."); info("Add a property or end an existing lease first."); pause(); return
    section("Step 1 — Select Property")
    prop = pick_from("available property", available, lambda p: p.summary_line())
    if not prop: pause(); return
    section("Step 2 — Select Tenant")
    if not state.tenants:
        warn("No tenants registered yet.")
        if not get_bool("Register a tenant now?"): pause(); return
        screen_register(default_role="Tenant"); tenant = state.current_user; state.current_user = user
    else:
        tenant = pick_from("tenant", state.tenants, lambda t: t.display())
        if not tenant: pause(); return
    section("Step 3 — Lease Terms")
    start = get_date("Lease start date"); end = get_date("Lease end date"); rent = get_float("Monthly rent (₦)")
    section("Confirm")
    print(f"  Property : {prop.address}\n  Tenant   : {tenant.name}\n  Period   : {start} → {end}\n  Rent     : ₦{rent:,.2f}/mo\n")
    if not get_bool("Confirm and sign?"): warn("Cancelled."); pause(); return
    try:
        with LeaseSigning(tenant, prop) as ctx:
            lease = ctx.sign(start, end, rent)
        state.leases.append(lease)
        print(); success("Lease signed!"); success(f"{tenant.name} is now tenant of {prop.address}.")
    except ValueError as e:
        error(str(e))
    pause()


def screen_terminate_lease():
    clr(); banner("Terminate a Lease")
    user = state.current_user; role = type(user).__name__
    active = [l for l in _get_leases() if l.is_active()]
    if not active: warn("No active leases to terminate."); pause(); return
    lease = pick_from("lease to terminate", active, lambda l: l.display())
    if not lease: pause(); return
    print(); warn(f"Terminate lease for {lease.tenant.name} at {lease.property.address}?")
    if not get_bool("Are you sure?"): info("Cancelled."); pause(); return
    try:
        lease.property.terminate_lease(caller=user, lease=lease)
    except PermissionError as e:
        error(str(e))
    pause()


# ── Payments ──────────────────────────────────────────────────
def screen_payments():
    while True:
        clr(); banner("Rent Payments")
        print(f"  {C.YELLOW}[1]{C.RESET}  💰  Record a new payment")
        print(f"  {C.YELLOW}[2]{C.RESET}  📜  View payment history")
        print(f"  {C.YELLOW}[0]{C.RESET}  ←   Back\n")
        choice = input(f"  {C.CYAN}▶ Enter choice: {C.RESET}").strip()
        if   choice == "1": screen_record_payment()
        elif choice == "2": screen_payment_history()
        elif choice == "0": return
        else: error("Invalid choice."); pause()


def screen_record_payment():
    clr(); banner("Record Rent Payment")
    active = [l for l in _get_leases() if l.is_active()]
    if not active: warn("No active leases."); pause(); return
    lease = pick_from("lease", active, lambda l: l.display())
    if not lease: pause(); return
    section("Payment Details")
    print(f"  Tenant   : {lease.tenant.name}\n  Property : {lease.property.address}\n  Rent Due : ₦{lease.rent_amount:,.2f}\n")
    amount    = get_float("Amount being paid (₦)")
    date_paid = get_date("Date payment received", allow_future=False)
    penalty   = PenaltyCalculator.compute(date_paid, lease.rent_amount)
    status    = PenaltyCalculator.classify(date_paid, date_paid.replace(day=1))
    print()
    if penalty > 0: warn(f"Payment is {status.value.upper()} — Penalty: ₦{penalty:,.2f}")
    else:           success("Payment is ON TIME — no penalty.")
    if not get_bool("Confirm and record?"): info("Not recorded."); pause(); return
    try:
        p = lease.record_payment(amount=amount, date_paid=date_paid)
        print(); success(f"₦{amount:,.2f} recorded.")
        if p.penalty > 0: warn(f"Late penalty of ₦{p.penalty:,.2f} applied.")
    except ValueError as e:
        error(str(e))
    pause()


def screen_payment_history():
    clr(); banner("Payment History")
    leases = _get_leases()
    if not leases: warn("No leases found."); pause(); return
    lease = pick_from("lease", leases, lambda l: l.display())
    if not lease: pause(); return
    clr(); banner(f"Payments — {lease.tenant.name}")
    info(f"Property: {lease.property.address}")
    info(f"Lease   : {lease.start_date} → {lease.end_date}  |  ₦{lease.rent_amount:,.0f}/mo")
    divider()
    if not lease.payments:
        warn("No payments recorded.")
    else:
        total_paid = total_penalty = 0
        for i, p in enumerate(lease.payments, 1):
            print(f"  {C.YELLOW}[{i}]{C.RESET}  {p.display()}")
            total_paid += p.amount; total_penalty += p.penalty
        divider()
        print(f"  Total Paid    : {C.GREEN}₦{total_paid:,.2f}{C.RESET}")
        if total_penalty > 0: print(f"  Total Penalty : {C.RED}₦{total_penalty:,.2f}{C.RESET}")
    pause()


# ── Tenant screens ────────────────────────────────────────────
def _find_tenant_lease():
    user = state.current_user
    return next((l for p in state.properties for l in p.leases if l.tenant == user and l.is_active()), None)


def screen_tenant_lease():
    clr(); banner("My Lease")
    lease = _find_tenant_lease()
    if not lease:
        warn("You have no active lease."); info("Contact your landlord if this is an error."); pause(); return
    section("Lease Details")
    print(f"  Property   : {C.WHITE}{lease.property.address}{C.RESET}")
    print(f"  Landlord   : {lease.property.landlord.name}  ({lease.property.landlord.phone})")
    print(f"  Period     : {lease.start_date}  →  {lease.end_date}")
    print(f"  Rent       : {C.GREEN}₦{lease.rent_amount:,.2f}{C.RESET} per month")
    days = (lease.end_date - date.today()).days
    col  = C.RED if days < 30 else C.YELLOW if days < 90 else C.GREEN
    print(f"  Days Left  : {col}{days} days{C.RESET}")
    if days < 30: warn("Your lease is expiring soon. Contact your landlord to renew.")
    pause()


def screen_tenant_payments():
    clr(); banner("My Payment History")
    user = state.current_user
    payments = [p for prop in state.properties for l in prop.leases if l.tenant == user for p in l.payments]
    if not payments: warn("No payment records found."); pause(); return
    total_paid = total_penalty = 0
    for i, p in enumerate(payments, 1):
        print(f"  {C.YELLOW}[{i}]{C.RESET}  {p.display()}")
        total_paid += p.amount; total_penalty += p.penalty
    divider()
    print(f"  Total Paid     : {C.GREEN}₦{total_paid:,.2f}{C.RESET}")
    if total_penalty > 0: print(f"  Total Penalties: {C.RED}₦{total_penalty:,.2f}{C.RESET}")
    pause()


def screen_submit_maintenance():
    clr(); banner("Submit Maintenance Request")
    lease = _find_tenant_lease()
    if not lease: warn("You must have an active lease to submit a request."); pause(); return
    section("Describe the Issue")
    issue = get_text_only("Describe the problem")
    section("Priority Level")
    print(f"  {C.YELLOW}[1]{C.RESET}  {C.GREEN}LOW{C.RESET}     — Cosmetic (repainting, broken tile)")
    print(f"  {C.YELLOW}[2]{C.RESET}  {C.YELLOW}MEDIUM{C.RESET}  — Inconvenient (faulty lock, power issue)")
    print(f"  {C.YELLOW}[3]{C.RESET}  {C.RED}HIGH{C.RESET}    — Urgent (burst pipe, gas leak, no water)\n")
    priority = {1: Priority.LOW, 2: Priority.MEDIUM, 3: Priority.HIGH}[get_int("Select priority", 1, 3)]
    MaintenanceRequest(state.current_user, lease.property, issue, priority)
    print(); success("Maintenance request submitted!")
    info(f"Property : {lease.property.address}")
    info(f"Priority : {priority.name}")
    info("Your landlord has been notified.")
    pause()


# ── Maintenance (Landlord / Agent) ────────────────────────────
def screen_maintenance():
    user = state.current_user; role = type(user).__name__
    while True:
        clr(); banner("Maintenance Requests")
        all_req = [m for p in (user.properties if role == "Landlord" else _agent_properties()) for m in p.maintenance]
        open_req     = [m for m in all_req if m.status == "open"]
        resolved_req = [m for m in all_req if m.status == "resolved"]
        info(f"Open: {len(open_req)}   Resolved: {len(resolved_req)}   Total: {len(all_req)}\n")
        open_sorted = sorted(open_req, key=lambda m: m.priority.value, reverse=True)
        if open_sorted:
            section("Open Requests (highest priority first)")
            for i, m in enumerate(open_sorted, 1): print(f"  {C.YELLOW}[{i}]{C.RESET}  {m.display()}")
        else:
            success("No open maintenance requests.")
        print(f"\n  {C.YELLOW}[R]{C.RESET}  ✅  Resolve a request")
        print(f"  {C.YELLOW}[H]{C.RESET}  📜  View resolved history")
        print(f"  {C.YELLOW}[0]{C.RESET}  ←   Back\n")
        choice = input(f"  {C.CYAN}▶ Enter choice: {C.RESET}").strip().upper()
        if choice == "R":
            if not open_sorted: warn("No open requests."); pause()
            else:
                req = pick_from("request", open_sorted, lambda m: f"[{m.priority.name}] {m.issue} — {m.tenant.name}")
                if req: req.resolve(); success(f"Resolved: {req.issue}"); pause()
        elif choice == "H":
            clr(); banner("Resolved Maintenance")
            if not resolved_req: warn("No resolved requests yet.")
            else:
                for m in resolved_req: print(f"  {m.display()}")
            pause()
        elif choice == "0": return
        else: error("Invalid choice."); pause()


# ── Financial Report (Generator in action) ───────────────────
def screen_report():
    clr(); banner("Financial Report", "Overdue payments via generator")
    user = state.current_user
    total_props   = len(user.properties)
    occupied      = sum(1 for p in user.properties if not p.is_available)
    active_leases = sum(1 for p in user.properties for l in p.leases if l.is_active())
    monthly_roll  = sum(l.rent_amount for p in user.properties for l in p.leases if l.is_active())
    section("Portfolio Overview")
    print(f"  Total Properties : {total_props}")
    print(f"  Occupied         : {C.RED}{occupied}{C.RESET}")
    print(f"  Available        : {C.GREEN}{total_props - occupied}{C.RESET}")
    print(f"  Active Leases    : {active_leases}")
    print(f"  Monthly Rent Roll: {C.GREEN}₦{monthly_roll:,.2f}{C.RESET}")
    section("Overdue Payments  (generator reads one record at a time)")
    count = total_penalty = total_short = 0
    for payment in user.overdue_payments():   # ← generator yields one at a time
        count += 1
        short = max(0, payment.lease.rent_amount - payment.amount)
        print(f"\n  {C.YELLOW}[{count}]{C.RESET}  Tenant   : {C.WHITE}{payment.lease.tenant.name}{C.RESET}")
        print(f"        Property : {payment.lease.property.address}")
        print(f"        Paid     : ₦{payment.amount:,.2f}  on {payment.date_paid}")
        print(f"        Status   : {C.RED}{payment.status.value.upper()}{C.RESET}  |  Penalty: ₦{payment.penalty:,.2f}")
        if short > 0: print(f"        Shortfall: {C.RED}₦{short:,.2f}{C.RESET}")
        total_penalty += payment.penalty; total_short += short
    if count == 0:
        print(); success("No overdue payments! All tenants are current.")
    else:
        divider()
        print(f"  Overdue Records : {C.RED}{count}{C.RESET}")
        print(f"  Total Penalties : {C.RED}₦{total_penalty:,.2f}{C.RESET}")
        if total_short > 0: print(f"  Total Shortfall : {C.RED}₦{total_short:,.2f}{C.RESET}")
    pause()


# ── Mandates ──────────────────────────────────────────────────
def screen_mandates():
    user = state.current_user
    while True:
        clr(); banner("Agents & Mandates")
        my_mandates = [m for m in state.mandates if m.landlord == user]
        if my_mandates:
            for i, m in enumerate(my_mandates, 1): print(f"  {C.YELLOW}[{i}]{C.RESET}  {m.display()}")
        else:
            info("No mandates yet.")
        print(f"\n  {C.YELLOW}[N]{C.RESET}  ➕  Create a new mandate")
        print(f"  {C.YELLOW}[0]{C.RESET}  ←   Back\n")
        choice = input(f"  {C.CYAN}▶ Enter choice: {C.RESET}").strip().upper()
        if   choice == "N": screen_create_mandate()
        elif choice == "0": return
        else: error("Invalid choice."); pause()


def screen_create_mandate():
    clr(); banner("Create Agent Mandate"); user = state.current_user
    if not state.agents:
        warn("No agents registered.")
        if get_bool("Register an agent now?"): screen_register(default_role="Agent"); state.current_user = user
        else: pause(); return
    agent = pick_from("agent", state.agents, lambda a: a.display())
    if not agent: pause(); return
    if not user.properties: warn("You have no properties to assign."); pause(); return
    selected = [p for p in user.properties if get_bool(f"Include '{p.address}'?")]
    if not selected: warn("No properties selected."); pause(); return
    start = get_date("Mandate start date"); end = get_date("Mandate end date")
    state.mandates.append(Mandate(user, agent, selected, start, end))
    print(); success(f"Mandate created: {agent.name} manages {len(selected)} propert{'ies' if len(selected) != 1 else 'y'}."); pause()


# ── Agent properties ──────────────────────────────────────────
def _agent_properties():
    user = state.current_user; managed = []
    for m in state.mandates:
        if m.agent == user and m.is_active():
            managed += [p for p in m.properties if p not in managed]
    return managed

def screen_agent_properties():
    clr(); banner("Properties I Manage")
    managed = _agent_properties()
    if not managed:
        warn("No properties assigned to you."); info("Ask your landlord to create a mandate."); pause(); return
    for i, p in enumerate(managed, 1):
        tag = f"{C.GREEN}[Available]{C.RESET}" if p.is_available else f"{C.RED}[Not Available]{C.RESET}"
        print(f"  {C.YELLOW}[{i}]{C.RESET}  {p.summary_line()}  {tag}")
    pause()


# =============================================================
# ANALYTICS DASHBOARD — called from Landlord menu option [7]
# Imports financial_dashboard and runs it on live state data.
# =============================================================

def screen_analytics_dashboard():
    clr(); banner("Analytics Dashboard", "Pandas export & charts")
    user = state.current_user

    # Count how many payments exist right now
    total_payments = sum(len(l.payments) for p in user.properties for l in p.leases)

    if total_payments == 0:
        warn("No payment records found in memory.")
        info("You need to record at least one rent payment first.")
        info("Tip: Use [3] Rent Payments → Record a new payment.")
        print()
        if get_bool("Load demo data so you can see the charts now?"):
            seed_demo_data(user)
            total_payments = sum(len(l.payments) for p in user.properties for l in p.leases)
            success(f"Demo data loaded — {total_payments} payments now in memory.")
        else:
            pause(); return

    elif total_payments < 5:
        warn(f"You only have {total_payments} payment record(s).")
        info("Charts work best with 10+ payments across different months.")
        info("Tip: Record more payments, or load demo data to supplement.")
        print()
        if get_bool("Add demo data on top of your existing data?"):
            seed_demo_data(user)
            total_payments = sum(len(l.payments) for p in user.properties for l in p.leases)
            success(f"Demo data added — {total_payments} total payments now in memory.")

    print()
    info(f"Running analytics on {total_payments} payment records...")
    info("Charts will be saved to reports/ folder.")
    print()

    try:
        # Import the dashboard module and run it on current state
        import financial_dashboard as fd
        fd.run_on_state(user)
    except ImportError:
        error("financial_dashboard.py not found in the same folder.")
        info("Make sure financial_dashboard.py is in the same directory.")
    except Exception as e:
        error(f"Dashboard error: {e}")
    pause()


# =============================================================
# SEED DEMO DATA — testing shortcut (Pro-Tip from brief)
# Adds realistic Nigerian payment data to an existing landlord
# so charts have enough records to show meaningful patterns.
# Does NOT replace any data the user already typed in.
# =============================================================

def seed_demo_data(landlord):
    """
    Adds demo properties, tenants, leases and payments to the
    given landlord's account. Called only when the user chooses
    to load demo data from the Analytics Dashboard screen.
    Uses Nigerian names and Aba/Abia State addresses.
    """
    from datetime import date as dt

    # Only add demo tenants if none exist yet
    demo_tenants = [
        Tenant("Ada Nwosu",      "08061112233", "NIN-D001", "Nurse"),
        Tenant("Emeka Chukwu",   "08072223344", "NIN-D002", "Civil Servant"),
        Tenant("Fatima Aliyu",   "08083334455", "NIN-D003", "Teacher"),
        Tenant("Chidi Okonkwo",  "08094445566", "NIN-D004", "Trader"),
        Tenant("Ngozi Eze",      "08015556677", "NIN-D005", "Tailor"),
        Tenant("Bola Adeyemi",   "08026667788", "NIN-D006", "Lawyer"),
    ]
    state.tenants.extend(demo_tenants)

    # Add demo properties under this landlord
    flat1  = Flat("Flat 2B, 14 Ikot Ekpene Rd, Aba",    70, 110_000, landlord, 2, 1)
    flat2  = Flat("Flat 4A, 9 Eziama Close, Aba",        55,  85_000, landlord, 1, 2)
    duplex = Duplex("12 GRA Layout, Aba",               260, 400_000, landlord, 2, True)
    sc1    = SelfContain("Room 5, Ariaria Quarters, Aba", 18,  30_000, landlord)
    shop1  = Shop("Shop A3, Ariaria Market, Aba",         22,  60_000, landlord, 4.0, "Fashion")
    shop2  = Shop("Shop B7, Cemetery Rd Mkt, Aba",        16,  45_000, landlord, 2.5, "Electronics")
    state.properties.extend([flat1, flat2, duplex, sc1, shop1, shop2])

    # Lease + payment data: (prop, tenant, start, end, rent, [(day_paid, amount)...])
    # day > 4 = late payment; amount < rent = shortfall
    demo_leases = [
        (flat1,  demo_tenants[0], dt(2024,1,1),  dt(2024,12,31), 110_000,
            [(1,110_000),(1,110_000),(10,110_000),(1,110_000),(18,110_000),(1,110_000),(1,110_000),(5,110_000)]),
        (flat2,  demo_tenants[1], dt(2024,2,1),  dt(2025,1,31),   85_000,
            [(1,85_000),(9,85_000),(1,85_000),(1,80_000),(22,85_000),(1,85_000)]),
        (duplex, demo_tenants[2], dt(2024,1,15), dt(2025,1,14),  400_000,
            [(15,400_000),(15,400_000),(15,350_000),(15,400_000),(15,400_000)]),
        (sc1,    demo_tenants[3], dt(2024,4,1),  dt(2025,3,31),   30_000,
            [(1,30_000),(11,30_000),(1,30_000),(1,25_000),(1,30_000)]),
        (shop1,  demo_tenants[4], dt(2024,2,1),  dt(2025,1,31),   60_000,
            [(1,60_000),(1,60_000),(16,60_000),(1,60_000),(1,60_000),(1,50_000),(1,60_000)]),
        (shop2,  demo_tenants[5], dt(2024,6,1),  dt(2025,5,31),   45_000,
            [(1,45_000),(13,45_000),(1,45_000),(1,40_000)]),
    ]

    payment_id = sum(len(l.payments) for p in landlord.properties for l in p.leases) + 1

    for prop, tenant, start, end, rent, pmts in demo_leases:
        prop.status = PropertyStatus.OCCUPIED
        lease = LeaseAgreement(tenant, prop, start, end, rent)
        state.leases.append(lease)
        for i, (day, amount) in enumerate(pmts):
            month   = ((start.month - 1 + i) % 12) + 1
            year    = start.year + (start.month - 1 + i) // 12
            paid_on = dt(year, month, min(day, 28))
            p = RentPayment(lease, amount, paid_on)
            p.payment_id = payment_id
            lease.payments.append(p)
            payment_id += 1


# ── Goodbye ───────────────────────────────────────────────────
def screen_goodbye():
    clr()
    print(f"""
{C.CYAN}╔══════════════════════════════════════════════════════╗
║                                                      ║
║   {C.GREEN}Thank you for using Naija Property Manager!{C.CYAN}         ║
║                                                      ║
║   {C.GREY}Helping Nigerian landlords go digital.{C.CYAN}              ║
║                                                      ║
╚══════════════════════════════════════════════════════╝{C.RESET}
""")
    sys.exit(0)


# ── Entry point ───────────────────────────────────────────────
def main():
    screen_welcome()
    while True:
        user = screen_role_select()
        if user: screen_main_menu()
        state.current_user = None

if __name__ == "__main__":
    main()
