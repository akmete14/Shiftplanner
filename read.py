''' from pathlib import Path
import pandas as pd
from dateutil.relativedelta import relativedelta

path_to_file = "03_Sperrdatenplan Länggasse März + Erste Woche April 2025.xlsx"
sheet_name = "März"   # anpassen


# 1) alles roh ohne Header laden
raw = pd.read_excel(path_to_file, sheet_name=sheet_name, header=None)
#print(raw)

# 2) Zeile mit Spaltenüberschrift "Name" finden
name_row_idx = raw.index[raw.iloc[:,0].astype(str).str.strip().eq("Name")][0]
#print(name_row_idx)

# 3) Ab der Zeile NACH "Name" alle Einträge in der 1. Spalte holen
names_col = raw.iloc[name_row_idx+1:, 0]

# 4) Stoppen, sobald erste NaN (oder leere Zelle) kommt
names = []
for val in names_col:
    if pd.isna(val) or str(val).strip() == "":
        break
    names.append(str(val).strip())

# 5) Als DataFrame speichern
employees_df = pd.DataFrame(names, columns=["Employee"])
print(employees_df)

# 6) Suche Pensum-Index
pensum_row_index = raw.index[raw.iloc[:,1].astype(str).str.strip().eq("März")][0]
#print(pensum_row_index)

# pensum column
pensum_col = raw.iloc[pensum_row_index+1:, 1]

# stoppen sobald nan oder leere zelle
pensum = []
for val in pensum_col:
    if pd.isna(val) or str(val).strip() == "":
        break
    pensum.append(str(val).strip())

# als dataframe speichern
pensum_df = pd.DataFrame(pensum, columns=["Pensum"])
print(pensum_df)

# make sure indices start at 0..n-1 so rows align
employees_df = employees_df.reset_index(drop=True)
pensum_df    = pensum_df.reset_index(drop=True)

df = pd.concat([employees_df, pensum_df], axis=1)
print(df)'''
'''
import pandas as pd
from pathlib import Path

path_to_file = "03_Sperrdatenplan Länggasse März + Erste Woche April 2025.xlsx"
sheet_name = "März"

# 1) Load raw sheet
raw = pd.read_excel(path_to_file, sheet_name=sheet_name, header=None)

# 2) Find "Name" row
name_row_idx = raw.index[raw.iloc[:, 0].astype(str).str.strip().eq("Name")][0]

# 3) Extract employee names (below "Name" until empty)
names_col = raw.iloc[name_row_idx + 1 :, 0]
names = []
for val in names_col:
    if pd.isna(val) or str(val).strip() == "":
        break
    names.append(str(val).strip())

# 4) Find pensum values (same rows as names)
pensum_min_col = raw.iloc[name_row_idx + 1 : name_row_idx + 1 + len(names), 1]
pensum_max_col = raw.iloc[name_row_idx + 1: name_row_idx + 1 + len(names), 2]
pensum_min = [str(v).strip() if not pd.isna(v) else "" for v in pensum_min_col]
pensum_max = [str(v).strip() if not pd.isna(v) else "" for v in pensum_max_col]

# 5) Combine into one base DataFrame
df = pd.DataFrame({"Employee": names, "min Pensum": pensum_min, "max Pensum": pensum_max})

# 6) Availability columns start after column 1 (i.e. from column 2 onwards)
availability_cols = raw.columns[3:]

# Get corresponding rows for each employee
availability_rows = raw.iloc[name_row_idx + 1 : name_row_idx + 1 + len(names), 3:]

# Build availability DataFrame
availability_df = availability_rows.copy()
availability_df.index = df["Employee"]  # align by employee names
availability_df.columns = raw.iloc[name_row_idx, 3:]  # use date headers if available

# 7) Merge availability info into main df
# You can either:
#   - store the whole row as a list in one column, or
#   - flatten to long format (tidy)

# Option A: Store availability as list of values per employee
#df["Availability"] = availability_df.values.tolist()

print(df.head(3))'''
import pandas as pd
from pathlib import Path

path_to_file = "03_Sperrdatenplan Länggasse März + Erste Woche April 2025.xlsx"
sheet_name = "März"

# 1) Load raw sheet
raw = pd.read_excel(path_to_file, sheet_name=sheet_name, header=None)

# 2) Find "Name" row
name_row_idx = raw.index[raw.iloc[:, 0].astype(str).str.strip().eq("Name")][0]

# 3) Extract employee names (below "Name" until empty)
names_col = raw.iloc[name_row_idx + 1 :, 0]
names = []
for val in names_col:
    if pd.isna(val) or str(val).strip() == "":
        break
    names.append(str(val).strip())

# 4) Find pensum values (same rows as names)
pensum_min_col = raw.iloc[name_row_idx + 1 : name_row_idx + 1 + len(names), 1]
pensum_max_col = raw.iloc[name_row_idx + 1: name_row_idx + 1 + len(names), 2]
pensum_min = [str(v).strip() if not pd.isna(v) else "" for v in pensum_min_col]
pensum_max = [str(v).strip() if not pd.isna(v) else "" for v in pensum_max_col]

# 5) Combine into one base DataFrame
df = pd.DataFrame({"Employee": names, "min Pensum": pensum_min, "max Pensum": pensum_max})

# 6) Availability columns start after column 1 (i.e. from column 2 onwards)
availability_cols = raw.columns[3:]

# Get corresponding rows for each employee
availability_rows = raw.iloc[name_row_idx + 1 : name_row_idx + 1 + len(names), 3:]

# --- 🔽 NEW SECTION: Build clean availability matrix 🔽 ---

# Find the "slots" (a/b/c) row just above "Name"
slots_row_idx = name_row_idx
slots_raw = raw.iloc[slots_row_idx, 3:].astype(str).str.strip().str.lower()

# Find a "dates" row above slots (by checking for parsable dates)
def is_mostly_dates(series, dayfirst=True, thresh=0.6):
    s = series.dropna().astype(str).str.strip()
    parsed = pd.to_datetime(s, dayfirst=dayfirst, errors="coerce")
    return (parsed.notna().mean() >= thresh)

date_row_idx = None
for r in range(slots_row_idx - 1, max(-1, slots_row_idx - 10), -1):
    cand = raw.iloc[r, 3:]
    if is_mostly_dates(cand, dayfirst=True, thresh=0.5):
        date_row_idx = r
        break

if date_row_idx is None:
    raise ValueError("Could not find a date header row above the slots row.")

dates_raw = raw.iloc[date_row_idx, 3:]
dates_parsed = pd.to_datetime(dates_raw, dayfirst=True, errors="coerce").dt.date
slots = slots_raw.replace({"": None}).where(slots_raw.ne("nan"))
dates_parsed = dates_parsed.ffill()

col_tuples = []
for d, s in zip(dates_parsed, slots):
    slot = (s if s in ("a", "b", "c") else "")
    col_tuples.append((d, slot))

availability_matrix = availability_rows.copy()
availability_matrix.index = df["Employee"]
availability_matrix.columns = pd.MultiIndex.from_tuples(col_tuples, names=["Date", "Slot"])

# Ensure values are numeric 0/1 (you said you already replaced x→0 and empty→1)
availability_matrix = (
    availability_matrix
    .applymap(lambda v: 1 if (pd.isna(v) or str(v).strip()=="") else int(float(v)))
    .clip(lower=0, upper=1)
)

availability_matrix = availability_matrix.sort_index(axis=1)

# Also build a tidy/long version (useful for scheduling)
availability_long = (
    availability_matrix
    .stack(level=0)              # Date
    .stack(level=0)              # Slot
    .rename("Available")
    .reset_index()
    .rename(columns={"level_1": "Date", "level_2": "Slot"})
)

# --- 🔼 END NEW SECTION 🔼 ---

#print("=== Employee Table (no availability inside) ===")
print(df.head(3))

#print("\n=== Availability Matrix ===")
print(availability_matrix.head())

#print("\n=== Tidy (Long) Availability ===")
#print(availability_long.head())
#print(availability_matrix.iat[4,0])


### Given availability matrix and min/max pensum, we can try to schedule using optimization technique
from ortools.sat.python import cp_model
import numpy as np

# Inputs you already have:
# df: columns ["Employee", "min Pensum", "max Pensum"] (strings -> will parse)
# availability_matrix: index=Employee, columns=MultiIndex (Date, Slot), values in {0,1}

# --- Prepare indices ---
employees = list(df["Employee"])
slots_cols = list(availability_matrix.columns)   # list of (date, slot)
dates = sorted(set(c[0] for c in slots_cols))
#print(dates)