import sys
import pandas as pd
from .io import load_all_csvs, validate_all
from .calendar import expand_month
from .availability import build_allowed
from .export import write_schedule_csv
from .config import C
from .solver import solve

def main():
    if len(sys.argv) < 3:
        print("Usage: python -m src.main <year> <month>")
        sys.exit(1)
    year = int(sys.argv[1]); month = int(sys.argv[2])

    data_dir = "data"
    employees, shifts_df, recurring, exceptions, constraints = load_all_csvs(data_dir)
    validate_all(employees, shifts_df, recurring, exceptions, constraints)

    month_days = expand_month(year, month)
    shifts = list(shifts_df['shift_id'])

    allowed, prefer, force = build_allowed(employees, month_days, shifts_df, recurring, exceptions)

    coverage = {}
    for d, day in enumerate(month_days):
        target = int(constraints['target_coverage_weekend'] if day['is_weekend']
                     else constraints['target_coverage_weekday'])
        for si,_ in enumerate(shifts):
            coverage[(d,si)] = target

    min_month = {}; max_month = {}; weekend_limit = {}
    max_weekend_days = int(constraints['max_weekend_days_per_month'])
    for _, row in employees.iterrows():
        e = row[C.EMPLOYEE_ID]
        min_month[e] = int(row.get('min_shifts', 0)) if 'min_shifts' in row else 0
        max_month[e] = int(row.get('max_shifts', 1000)) if 'max_shifts' in row else 1000
        weekend_limit[e] = max_weekend_days

    assignments, meta = solve(
        month_days, shifts, list(employees[C.EMPLOYEE_ID]),
        allowed, coverage, min_month, max_month, weekend_limit,
        prefer, force
    )

    if not assignments:
        print("Keine Lösung:", meta); sys.exit(2)

    out = pd.DataFrame(assignments).merge(
        employees[[C.EMPLOYEE_ID,'name']], on=C.EMPLOYEE_ID, how='left'
    )
    path = write_schedule_csv(out, data_dir, year, month)
    print(f"Plan gespeichert: {path}\nMeta: {meta}")

if __name__ == '__main__':
    main()
