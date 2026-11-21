"""Static, hand-specified reference data. Identical on every run."""

SYNTHETIC_NOTE = (
    "Synthetic, illustrative data generated for the Recovery AI prototype. "
    "Not real dealership, customer, supplier or Tekion data."
)

SUPPLIERS = [
    {"supplier_id": "SUP-OEM", "name": "OEM Parts Distribution (synthetic)", "supplier_type": "oem"},
    {"supplier_id": "SUP-A", "name": "Store A Parts Department", "supplier_type": "dealer_store"},
    {"supplier_id": "SUP-B", "name": "Store B Parts Department", "supplier_type": "dealer_store"},
    {"supplier_id": "SUP-C", "name": "Store C Regional Warehouse", "supplier_type": "dealer_store"},
]

# Store A is the home dealership. B and C are alternate sources with different transfer times.
LOCATIONS = [
    {"location_id": "LOC-A", "name": "Store A - Home Dealership", "supplier_id": "SUP-A",
     "is_home": True, "transfer_time_minutes": 0, "transfer_cost": 0.0},
    {"location_id": "LOC-B", "name": "Store B - Sister Dealership (North)", "supplier_id": "SUP-B",
     "is_home": False, "transfer_time_minutes": 45, "transfer_cost": 25.0},
    {"location_id": "LOC-C", "name": "Store C - Regional Parts Warehouse", "supplier_id": "SUP-C",
     "is_home": False, "transfer_time_minutes": 90, "transfer_cost": 40.0},
]

# (part_id, part_name, part_type, unit_cost). P-001 is the hero pump.
PARTS = [
    ("P-001", "OEM Coolant Pump Assembly", "OEM", 312.00),
    ("P-002", "Front Brake Pad Set", "OEM", 89.50),
    ("P-003", "Rear Brake Pad Set", "OEM", 74.25),
    ("P-004", "Front Brake Rotor", "OEM", 112.00),
    ("P-005", "Engine Oil Filter", "OEM", 11.75),
    ("P-006", "Synthetic Engine Oil 5W-30 (5 qt)", "aftermarket", 38.00),
    ("P-007", "Cabin Air Filter", "aftermarket", 19.50),
    ("P-008", "Engine Air Filter", "aftermarket", 23.00),
    ("P-009", "Spark Plug Set", "OEM", 64.00),
    ("P-010", "Serpentine Belt", "OEM", 48.75),
    ("P-011", "12V Battery", "OEM", 179.00),
    ("P-012", "Alternator", "OEM", 342.00),
    ("P-013", "Starter Motor", "OEM", 286.50),
    ("P-014", "A/C Compressor", "OEM", 524.00),
    ("P-015", "Refrigerant R-1234yf (1 lb)", "OEM", 42.00),
    ("P-016", "Wheel Speed Sensor", "OEM", 57.25),
    ("P-017", "Front Strut Assembly", "OEM", 231.00),
    ("P-018", "Control Arm Bushing Kit", "OEM", 66.00),
    ("P-019", "Automatic Transmission Fluid (1 qt)", "OEM", 14.50),
    ("P-020", "Transmission Filter Kit", "OEM", 71.00),
    ("P-021", "Thermostat Housing", "OEM", 93.00),
    ("P-022", "Wiper Blade Set", "aftermarket", 27.00),
    ("P-023", "TPMS Sensor", "OEM", 49.00),
    ("P-024", "Ignition Coil", "OEM", 58.50),
]

# Technicians. T03 is the hero technician: the ONLY one with cooling_system.
# T11 is absent today (see disruption D-003), so the generator never schedules T11.
TECHNICIANS = [
    {"technician_id": "T01", "name": "Marcus Reed", "skills": ["general_service", "brakes", "tires_alignment"], "shift": ("07:00", "16:00")},
    {"technician_id": "T02", "name": "Priya Nair", "skills": ["electrical", "diagnostics", "ac_hvac"], "shift": ("08:00", "17:00")},
    {"technician_id": "T03", "name": "Daniel Ortiz", "skills": ["cooling_system", "engine", "diagnostics"], "shift": ("08:00", "17:00")},
    {"technician_id": "T04", "name": "Sofia Lindqvist", "skills": ["brakes", "suspension", "tires_alignment"], "shift": ("08:00", "17:00")},
    {"technician_id": "T05", "name": "Kenji Watanabe", "skills": ["engine", "transmission", "diagnostics"], "shift": ("07:30", "16:30")},
    {"technician_id": "T06", "name": "Amara Okafor", "skills": ["general_service", "ac_hvac", "electrical"], "shift": ("09:00", "18:00")},
    {"technician_id": "T07", "name": "Luis Fernandez", "skills": ["suspension", "tires_alignment", "brakes"], "shift": ("08:00", "17:00")},
    {"technician_id": "T08", "name": "Hannah Brooks", "skills": ["transmission", "engine", "general_service"], "shift": ("09:00", "18:00")},
    {"technician_id": "T09", "name": "Ravi Chandran", "skills": ["electrical", "diagnostics", "general_service"], "shift": ("07:00", "16:00")},
    {"technician_id": "T10", "name": "Elena Petrova", "skills": ["ac_hvac", "general_service", "brakes"], "shift": ("08:00", "17:00")},
    {"technician_id": "T11", "name": "Omar Haddad", "skills": ["brakes", "suspension", "general_service"], "shift": ("08:30", "17:30"), "absent": True},
    {"technician_id": "T12", "name": "Grace Liu", "skills": ["diagnostics", "engine", "electrical"], "shift": ("08:00", "17:00")},
]

# Bays. supported_work uses the same vocabulary as technician skills.
BAYS = [
    {"bay_id": "BAY-01", "supported_work": ["general_service", "brakes", "tires_alignment", "engine", "transmission"], "hours": ("07:00", "18:00")},
    {"bay_id": "BAY-02", "supported_work": ["engine", "cooling_system", "transmission", "general_service"], "hours": ("07:00", "18:00")},
    {"bay_id": "BAY-03", "supported_work": ["engine", "cooling_system", "diagnostics", "general_service", "transmission"], "hours": ("07:00", "18:00")},
    {"bay_id": "BAY-04", "supported_work": ["brakes", "suspension", "tires_alignment"], "hours": ("07:00", "18:00")},
    {"bay_id": "BAY-05", "supported_work": ["electrical", "diagnostics", "ac_hvac"], "hours": ("07:00", "18:00")},
    {"bay_id": "BAY-06", "supported_work": ["general_service", "ac_hvac", "electrical", "diagnostics", "engine", "transmission"], "hours": ("07:00", "18:00")},
    {"bay_id": "BAY-07", "supported_work": ["suspension", "tires_alignment", "brakes", "general_service"], "hours": ("08:00", "17:00")},
]

# Planned maintenance (disruption D-011). The scheduler treats it as a busy block.
PLANNED_MAINTENANCE = {"bay_id": "BAY-05", "start": "15:00", "minutes": 90}

# Job templates for the random block. cooling_system is deliberately absent:
# only the hero pump jobs need it, which keeps T03's schedule exactly as specified.
JOB_TEMPLATES = [
    {"name": "Brake service", "skills": ["brakes"], "parts": ["P-002", "P-003", "P-004"], "min_parts": 1, "max_parts": 2, "durations": [60, 90, 120]},
    {"name": "Oil and filter service", "skills": ["general_service"], "parts": ["P-005", "P-006", "P-007", "P-008", "P-022"], "min_parts": 2, "max_parts": 3, "durations": [30, 45, 60]},
    {"name": "Engine tune-up", "skills": ["engine"], "parts": ["P-009", "P-010", "P-024"], "min_parts": 1, "max_parts": 2, "durations": [90, 120, 150]},
    {"name": "Electrical repair", "skills": ["electrical", "diagnostics"], "parts": ["P-011", "P-012", "P-013"], "min_parts": 1, "max_parts": 1, "durations": [60, 90, 120]},
    {"name": "A/C service", "skills": ["ac_hvac"], "parts": ["P-014", "P-015"], "min_parts": 1, "max_parts": 2, "durations": [60, 120]},
    {"name": "Suspension repair", "skills": ["suspension", "tires_alignment"], "parts": ["P-017", "P-018"], "min_parts": 1, "max_parts": 2, "durations": [120, 150, 180]},
    {"name": "Tire and TPMS service", "skills": ["tires_alignment"], "parts": ["P-023"], "min_parts": 1, "max_parts": 1, "durations": [30, 45, 60]},
    {"name": "Transmission service", "skills": ["transmission"], "parts": ["P-019", "P-020"], "min_parts": 2, "max_parts": 2, "durations": [90, 120]},
    {"name": "Diagnostic check", "skills": ["diagnostics"], "parts": ["P-016"], "min_parts": 0, "max_parts": 1, "durations": [30, 45, 60]},
]

FIRST_NAMES = [
    "Alex", "Blake", "Casey", "Dana", "Eli", "Farah", "Gabe", "Hana", "Ian", "Jules",
    "Kira", "Leo", "Maya", "Noor", "Owen", "Pia", "Quinn", "Rhea", "Saul", "Tara",
    "Uma", "Vik", "Wren", "Yara",
]
LAST_NAMES = [
    "Abbott", "Banerjee", "Castillo", "Dubois", "Eriksen", "Fischer", "Gupta", "Hayes",
    "Ibrahim", "Jensen", "Kovac", "Lopez", "Morgan", "Nakamura", "Osei", "Pereira",
    "Quigley", "Rossi", "Sato", "Thompson", "Usman", "Vargas", "Walsh", "Zhang",
]
FICTIONAL_MAKES = {
    "Arden": ["Sedan S", "Crossover X"],
    "Brava": ["Hatch H", "Wagon W"],
    "Calix": ["Pickup P", "Coupe C"],
    "Dorian": ["SUV V", "Minivan M"],
}
APPOINTMENT_PREFERENCES = [
    None, None, "Prefers morning drop-off", "Needs shuttle ride", "Waiting on site",
    "Prefers pickup after 17:00",
]
