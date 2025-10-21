import os
def write_schedule_csv(df, data_dir, year, month):
    out_path = os.path.join(data_dir, f"schedule_{year}_{month:02d}.csv")
    df.to_csv(out_path, index=False)
    return out_path
