from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import psycopg2, psycopg2.extras, json

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

def db():
    return psycopg2.connect(host="localhost", dbname="futurefix", user="futurefix",
        password="futurefix", cursor_factory=psycopg2.extras.RealDictCursor)

@app.get("/api/machines")
def machines():
    with db() as c, c.cursor() as cur:
        cur.execute("SELECT * FROM machines")
        return cur.fetchall()

@app.get("/api/oee")
def oee(machine_id: str = None):
    with db() as c, c.cursor() as cur:
        cur.execute("""SELECT machine_id, AVG(availability) availability, AVG(performance) performance,
            AVG(quality) quality, AVG(oee) oee FROM v_oee_by_shift
            WHERE %(m)s IS NULL OR machine_id=%(m)s GROUP BY machine_id""", {"m": machine_id})
        return cur.fetchall()

@app.get("/api/downtime-pareto")
def downtime_pareto(machine_id: str):
    with db() as c, c.cursor() as cur:
        cur.execute("""SELECT dr.description, SUM(ms.duration_s) secs FROM machine_states ms
            JOIN downtime_reasons dr ON dr.reason_code = ms.reason_code
            WHERE ms.machine_id=%s AND ms.state='DOWN' GROUP BY dr.description ORDER BY secs DESC""", (machine_id,))
        return cur.fetchall()

@app.get("/api/reject-pareto")
def reject_pareto(machine_id: str):
    with db() as c, c.cursor() as cur:
        cur.execute("""SELECT rr.description, COUNT(*) n FROM production_events pe
            JOIN reject_reasons rr ON rr.reject_reason_code = pe.reject_reason_code
            WHERE pe.machine_id=%s AND pe.quality_status='SCRAP' GROUP BY rr.description ORDER BY n DESC""", (machine_id,))
        return cur.fetchall()

@app.get("/api/telemetry")
def telemetry(machine_id: str, from_ts: str, to_ts: str):
    with db() as c, c.cursor() as cur:
        cur.execute("""SELECT date_trunc('minute', ts) t, AVG(spindle_load_pct) load,
            AVG(motor_temp_c) temp, AVG(vibration_mm_s) vib FROM telemetry
            WHERE machine_id=%s AND ts BETWEEN %s AND %s GROUP BY t ORDER BY t""",
            (machine_id, from_ts, to_ts))
        return cur.fetchall()

@app.get("/api/config")
def get_config():
    with db() as c, c.cursor() as cur:
        cur.execute("SELECT config_key, config_value FROM app_config")
        return {r["config_key"]: r["config_value"] for r in cur.fetchall()}

@app.put("/api/config/{key}")
def set_config(key: str, value: dict):
    with db() as c, c.cursor() as cur:
        cur.execute("""INSERT INTO app_config VALUES (%s,%s)
            ON CONFLICT (config_key) DO UPDATE SET config_value=%s""",
            (key, json.dumps(value), json.dumps(value)))
        c.commit()
    return {"ok": True}