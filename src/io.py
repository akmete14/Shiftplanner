import os
import pandas as pd
from .config import WEEKDAYS, SHIFT_IDS, C

def _read_csv(path):
    if not os.path.exists(path):
        raise FileNotFoundError(f"CSV fehlt: {path}")
    return pd.read_csv(path)

def load_all_csvs(data_dir:str):
    employees = _read_csv(os.path.join(data_dir, "employees.csv"))
    shifts = _read_csv(os.path.join(data_dir, "shifts.csv"))
    recurring = _read_csv(os.path.join(data_dir, "availability_recurring.csv"))
    exceptions = _read_csv(os.path.join(data_dir, "availability_exceptions.csv"))
    constraints = _read_csv(os.path.join(data_dir, "constraints.csv"))
    constraints = {k: v for k, v in zip(constraints['key'], constraints['value'])}
    return employees, shifts, recurring, exceptions, constraints

def validate_all(employees, shifts, recurring, exceptions, constraints):
    if employees[C.EMPLOYEE_ID].duplicated().any():
        dup = employees[employees[C.EMPLOYEE_ID].duplicated()][C.EMPLOYEE_ID].tolist()
        raise ValueError(f"Doppelte employee_id: {dup}")

    if not set(shifts['shift_id']).issubset(set(SHIFT_IDS)):
        missing = set(shifts['shift_id']) - set(SHIFT_IDS)
        raise ValueError(f"Unbekannte shift_id(s): {missing}")

    if not set(recurring['weekday']).issubset(set(WEEKDAYS)):
        bad = set(recurring['weekday']) - set(WEEKDAYS)
        raise ValueError(f"Ungültige Wochentage in recurring: {bad}")

    if 'type' in exceptions.columns:
        valid_types = {'block','prefer','force'}
        bad = set(exceptions['type'].dropna()) - valid_types
        if bad:
            raise ValueError(f"Ungültige exception type(s): {bad}")

    required = ['target_coverage_weekday','target_coverage_weekend','max_weekend_days_per_month']
    for r in required:
        if r not in constraints:
            raise ValueError(f"Constraint fehlt: {r}")
    return True
