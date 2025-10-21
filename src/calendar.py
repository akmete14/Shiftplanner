from datetime import date, timedelta
from .config import WEEKDAYS

def expand_month(year:int, month:int):
    if month == 12:
        end_year, end_month = year+1, 1
    else:
        end_year, end_month = year, month+1

    d = date(year, month, 1)
    end = date(end_year, end_month, 1)
    days = []
    while d < end:
        wd_idx = (d.weekday() + 1) % 7
        weekday = WEEKDAYS[wd_idx] if wd_idx < len(WEEKDAYS) else WEEKDAYS[0]
        is_weekend = weekday in ("SA","SO")
        days.append({"date": d, "weekday": weekday, "is_weekend": is_weekend})
        d += timedelta(days=1)
    return days
