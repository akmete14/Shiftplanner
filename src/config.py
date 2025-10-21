from dataclasses import dataclass

WEEKDAYS = ["MO","DI","MI","DO","FR","SA","SO"]
SHIFT_IDS = ["a","b","c"]  # Früh, Mittel, Spät

@dataclass(frozen=True)
class Columns:
    EMPLOYEE_ID: str = "employee_id"
    NAME: str = "name"
    SHIFT_ID: str = "shift_id"
    WEEKDAY: str = "weekday"
    DATE: str = "date"
    TYPE: str = "type"
    ALLOWED_SHIFTS: str = "allowed_shifts"

C = Columns()
