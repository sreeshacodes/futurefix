import csv, glob, os, psycopg2

conn = psycopg2.connect(host="localhost", dbname="futurefix", user="futurefix", password="futurefix")
cur = conn.cursor()
DATA = os.path.join(os.path.dirname(__file__), "..", "data")

def load(path, sql, transform=None):
    n = 0
    with open(path) as f:
        for row in csv.DictReader(f):
            try:
                if transform: row = transform(row)
                cur.execute(sql, row)
            except Exception:
                conn.rollback()
                n += 1
    if n: print(f"{path}: {n} rows quarantined")

load(f"{DATA}/machines.csv", """
    INSERT INTO machines VALUES (%(machine_id)s,%(machine_name)s,%(machine_type)s,%(cell)s,
    %(make)s,%(model)s,%(commissioned)s,%(rated_kw)s) ON CONFLICT DO NOTHING""")

load(f"{DATA}/part_master.csv", """
    INSERT INTO part_master VALUES (%(part_number)s,%(description)s,
    %(ideal_cycle_time_s)s,%(machine_type)s) ON CONFLICT DO NOTHING""")

load(f"{DATA}/downtime_reasons.csv", """
    INSERT INTO downtime_reasons VALUES (%(reason_code)s,%(description)s,
    %(category)s,%(reason_group)s) ON CONFLICT DO NOTHING""")

load(f"{DATA}/reject_reasons.csv", """
    INSERT INTO reject_reasons VALUES (%(reject_reason_code)s,%(description)s) ON CONFLICT DO NOTHING""")

load(f"{DATA}/shifts.csv", """
    INSERT INTO shifts VALUES (%(shift_id)s,%(machine_id)s,%(shift_date)s,%(shift_name)s,
    %(planned_start)s,%(planned_end)s,%(planned_break_min)s,%(operator_id)s) ON CONFLICT DO NOTHING""")

def state_transform(row):
    row["reason_code"] = row["reason_code"] or None
    return row
load(f"{DATA}/machine_states.csv", """
    INSERT INTO machine_states (machine_id,state_start,state_end,duration_s,state,reason_code,note)
    VALUES (%(machine_id)s,%(state_start)s,%(state_end)s,%(duration_s)s,%(state)s,%(reason_code)s,%(note)s)
    ON CONFLICT (machine_id,state_start) DO NOTHING""", state_transform)

def event_transform(row):
    row["reject_reason_code"] = row["reject_reason_code"] or None
    return row
load(f"{DATA}/production_events.csv", """
    INSERT INTO production_events VALUES (%(event_id)s,%(machine_id)s,%(shift_id)s,%(ts)s,
    %(part_number)s,%(cycle_time_s)s,%(quality_status)s,%(reject_reason_code)s) ON CONFLICT DO NOTHING""", event_transform)

def telemetry_transform(row):
    if row["spindle_current_a"] in ("-999.0", "-999"):
        row["spindle_current_a"] = None
    for col in ("spindle_speed_rpm","spindle_load_pct","spindle_current_a",
                "motor_temp_c","vibration_mm_s","coolant_flow_lpm"):
        if row[col] == "":
            row[col] = None
    return row
for path in glob.glob(f"{DATA}/telemetry_*.csv"):
    load(path, """
        INSERT INTO telemetry VALUES (%(machine_id)s,%(ts)s,%(spindle_speed_rpm)s,%(spindle_load_pct)s,
        %(spindle_current_a)s,%(motor_temp_c)s,%(vibration_mm_s)s,%(coolant_flow_lpm)s)
        ON CONFLICT (machine_id,ts) DO NOTHING""", telemetry_transform)

cur.execute("""INSERT INTO app_config VALUES
    ('machine_order', '["HOB-01","HOB-02","SHV-01"]'),
    ('oee_thresholds', '{"green":0.75,"amber":0.5}'),
    ('default_window_days', '7')
    ON CONFLICT DO NOTHING""")

conn.commit()
print("done")