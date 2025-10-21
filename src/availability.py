from collections import defaultdict
from .config import C

def _parse_allowed(s):
    if not isinstance(s, str) or not s.strip():
        return set()
    return set([x.strip() for x in s.split(",") if x.strip()])

def build_allowed(employees_df, month_days, shifts_df, recurring_df, exceptions_df):
    employees = list(employees_df[C.EMPLOYEE_ID])
    shifts = list(shifts_df['shift_id'])

    allowed = {e: [[False for _ in shifts] for _ in month_days] for e in employees}
    prefer = {e: [[False for _ in shifts] for _ in month_days] for e in employees}
    force  = {e: [[False for _ in shifts] for _ in month_days] for e in employees}

    rec_map = defaultdict(dict)
    for _, r in recurring_df.iterrows():
        rec_map[r[C.EMPLOYEE_ID]][r['weekday']] = _parse_allowed(r['allowed_shifts'])

    for e in employees:
        for d, day in enumerate(month_days):
            base = rec_map.get(e, {}).get(day["weekday"], set())
            for si, s in enumerate(shifts):
                allowed[e][d][si] = (s in base)

    exc_group = defaultdict(list)
    for _, r in exceptions_df.iterrows():
        exc_group[(r[C.EMPLOYEE_ID], str(r['date']))].append(r)

    for e in employees:
        for d, day in enumerate(month_days):
            key = (e, day["date"].isoformat())
            if key not in exc_group:
                continue
            if any(r['type']=="block" for r in exc_group[key]):
                for si in range(len(shifts)):
                    allowed[e][d][si] = False
                continue
            force_rows = [r for r in exc_group[key] if r['type']=="force"]
            if force_rows:
                forced = set()
                for r in force_rows:
                    forced |= _parse_allowed(r['allowed_shifts'])
                for si, s in enumerate(shifts):
                    val = s in forced
                    allowed[e][d][si] = val
                    force[e][d][si] = val
            prefer_rows = [r for r in exc_group[key] if r['type']=="prefer"]
            if prefer_rows:
                prefs = set()
                for r in prefer_rows:
                    prefs |= _parse_allowed(r['allowed_shifts'])
                for si, s in enumerate(shifts):
                    if s in prefs and allowed[e][d][si]:
                        prefer[e][d][si] = True

    return allowed, prefer, force
