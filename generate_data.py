"""
generate_data.py
-----------------
Generates a synthetic medical equipment utilization & maintenance-risk
dataset that mirrors the structure of the VitalAsset capstone data
(Kenya Health Facility Census-style facility/location fields combined
with C-MAPSS-style degradation/sensor fields).

Run this once to (re)create data/equipment_risk_data.csv.
Swap this file's output for your real dataset later without changing
any other code — rag_utils.py only cares about the column names below.
"""

import csv
import random
from datetime import datetime, timedelta
from pathlib import Path

random.seed(42)

COUNTIES = ["Nairobi", "Mombasa", "Kisumu", "Nakuru", "Uasin Gishu", "Kiambu",
            "Machakos", "Kakamega", "Meru", "Bungoma"]

HOSPITALS = {
    "Nairobi": ["Kenyatta National Hospital", "Mbagathi Hospital"],
    "Mombasa": ["Coast General Teaching & Referral Hospital"],
    "Kisumu": ["Jaramogi Oginga Odinga Teaching & Referral Hospital"],
    "Nakuru": ["Nakuru Level 5 Hospital"],
    "Uasin Gishu": ["Moi Teaching & Referral Hospital"],
    "Kiambu": ["Kiambu Level 5 Hospital"],
    "Machakos": ["Machakos Level 5 Hospital"],
    "Kakamega": ["Kakamega County General Hospital"],
    "Meru": ["Meru Level 5 Hospital"],
    "Bungoma": ["Bungoma County Referral Hospital"],
}

EQUIPMENT_TYPES = {
    "Dialysis Machine": {"life_cycles": 9000, "unit": "treatment cycles"},
    "Ventilator": {"life_cycles": 15000, "unit": "operating hours"},
    "Anesthesia Machine": {"life_cycles": 12000, "unit": "operating hours"},
    "Patient Monitor": {"life_cycles": 20000, "unit": "operating hours"},
    "Infusion Pump": {"life_cycles": 25000, "unit": "operating hours"},
    "X-Ray Machine": {"life_cycles": 8000, "unit": "exposures"},
    "Ultrasound Machine": {"life_cycles": 18000, "unit": "operating hours"},
    "Autoclave/Sterilizer": {"life_cycles": 10000, "unit": "sterilization cycles"},
    "Defibrillator": {"life_cycles": 6000, "unit": "discharge cycles"},
    "Oxygen Concentrator": {"life_cycles": 22000, "unit": "operating hours"},
}

MAINTENANCE_NOTES = [
    "Routine preventive maintenance completed, no faults found.",
    "Technician flagged unusual vibration during last inspection.",
    "Replacement filter/consumable overdue by more than 30 days.",
    "Calibration passed within tolerance.",
    "Recurring error code logged by onboard diagnostics.",
    "No maintenance record on file for over 6 months.",
    "Spare parts requested from supplier, pending delivery.",
    "Unit temporarily decommissioned pending inspection.",
    "Minor repair completed, unit returned to service.",
    "Biomedical engineer recommends replacement within 90 days.",
]


def risk_level_from_score(score):
    if score >= 75:
        return "Critical"
    if score >= 50:
        return "High"
    if score >= 25:
        return "Medium"
    return "Low"


def make_row(i):
    eq_type = random.choice(list(EQUIPMENT_TYPES.keys()))
    county = random.choice(COUNTIES)
    hospital = random.choice(HOSPITALS[county])

    life_cycles = EQUIPMENT_TYPES[eq_type]["life_cycles"]
    unit = EQUIPMENT_TYPES[eq_type]["unit"]

    install_date = datetime(2018, 1, 1) + timedelta(days=random.randint(0, 2500))
    age_days = (datetime(2026, 9, 1) - install_date).days

    cycles_used = int(min(life_cycles, max(0, random.gauss(life_cycles * 0.45, life_cycles * 0.25))))
    utilization_pct = round(min(100, (cycles_used / life_cycles) * 100), 1)

    days_since_maintenance = random.randint(1, 400)
    last_maintenance = datetime(2026, 9, 1) - timedelta(days=days_since_maintenance)

    sensor_temp_c = round(random.gauss(38, 4), 1)
    sensor_vibration_mm_s = round(max(0, random.gauss(2.5, 1.5)), 2)

    # Composite risk score: weighted mix of utilization, overdue maintenance,
    # sensor drift, and age -- mirrors the kind of feature blend the ML
    # teammate is using for the capstone's risk model.
    score = (
        utilization_pct * 0.4
        + min(days_since_maintenance / 3, 100) * 0.3
        + min(sensor_vibration_mm_s * 8, 100) * 0.2
        + min(age_days / 30, 100) * 0.1
    )
    score = round(min(100, max(0, score)), 1)
    predicted_failure_days = int(max(3, (100 - score) * random.uniform(2.5, 4.5)))

    return {
        "equipment_id": f"EQ-{i:04d}",
        "equipment_type": eq_type,
        "hospital_name": hospital,
        "county": county,
        "install_date": install_date.strftime("%Y-%m-%d"),
        "last_maintenance_date": last_maintenance.strftime("%Y-%m-%d"),
        "days_since_maintenance": days_since_maintenance,
        "utilization_pct_of_rated_life": utilization_pct,
        "usage_unit": unit,
        "sensor_temp_c": sensor_temp_c,
        "sensor_vibration_mm_s": sensor_vibration_mm_s,
        "risk_score": score,
        "risk_level": risk_level_from_score(score),
        "predicted_days_to_failure": predicted_failure_days,
        "maintenance_notes": random.choice(MAINTENANCE_NOTES),
    }


def main(n=250):
    out_path = Path(__file__).parent / "data" / "equipment_risk_data.csv"
    out_path.parent.mkdir(exist_ok=True)
    rows = [make_row(i) for i in range(1, n + 1)]
    with open(out_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)
    print(f"Wrote {len(rows)} rows to {out_path}")


if __name__ == "__main__":
    main()
