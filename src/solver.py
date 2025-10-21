from ortools.sat.python import cp_model

def solve(month_days, shifts, employees, allowed, coverage_by_dayshift,
          min_month_shifts, max_month_shifts, weekend_limit, prefer_flags, force_flags):
    model = cp_model.CpModel()
    x = {}
    for e in employees:
        for d,_ in enumerate(month_days):
            for si,_ in enumerate(shifts):
                x[(e,d,si)] = model.NewBoolVar(f"x_{e}_{d}_{si}")

    for e in employees:
        for d,_ in enumerate(month_days):
            for si,_ in enumerate(shifts):
                if not allowed[e][d][si]:
                    model.Add(x[(e,d,si)] == 0)

    for e in employees:
        for d,_ in enumerate(month_days):
            for si,_ in enumerate(shifts):
                if force_flags[e][d][si]:
                    model.Add(x[(e,d,si)] == 1)

    for e in employees:
        for d,_ in enumerate(month_days):
            model.Add(sum(x[(e,d,si)] for si,_ in enumerate(shifts)) <= 1)

    for d,_ in enumerate(month_days):
        for si,_ in enumerate(shifts):
            model.Add(sum(x[(e,d,si)] for e in employees) == coverage_by_dayshift[(d,si)])

    for e in employees:
        total_e = sum(x[(e,d,si)] for d,_ in enumerate(month_days) for si,_ in enumerate(shifts))
        if e in min_month_shifts:
            model.Add(total_e >= int(min_month_shifts[e]))
        if e in max_month_shifts:
            model.Add(total_e <= int(max_month_shifts[e]))

    for e in employees:
        weekend_assign = []
        for d, day in enumerate(month_days):
            if day['is_weekend']:
                w = model.NewBoolVar(f"wknd_{e}_{d}")
                model.Add(sum(x[(e,d,si)] for si,_ in enumerate(shifts)) >= 1).OnlyEnforceIf(w)
                model.Add(sum(x[(e,d,si)] for si,_ in enumerate(shifts)) == 0).OnlyEnforceIf(w.Not())
                weekend_assign.append(w)
        if weekend_assign and e in weekend_limit:
            model.Add(sum(weekend_assign) <= int(weekend_limit[e]))

    prefer_gain = []
    for e in employees:
        for d,_ in enumerate(month_days):
            for si,_ in enumerate(shifts):
                if prefer_flags[e][d][si]:
                    prefer_gain.append(x[(e,d,si)])

    c_counts = {}
    max_c = model.NewIntVar(0, len(month_days), "max_c")
    last = len(shifts)-1  # 'c'
    for e in employees:
        c_counts[e] = sum(x[(e,d,last)] for d,_ in enumerate(month_days))
        model.Add(c_counts[e] <= max_c)

    model.Maximize(5 * sum(prefer_gain) - 1 * max_c)

    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = 15
    solver.parameters.num_search_workers = 8
    status = solver.Solve(model)

    if status not in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        return None, {"status": status, "message": "No feasible schedule."}

    assignments = []
    for d, day in enumerate(month_days):
        for si, s in enumerate(shifts):
            for e in employees:
                if solver.Value(x[(e,d,si)]) == 1:
                    assignments.append({
                        "date": day["date"].isoformat(),
                        "weekday": day["weekday"],
                        "shift": s,
                        "employee_id": e
                    })
    return assignments, {"status": status, "objective": solver.ObjectiveValue()}
