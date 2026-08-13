import psycopg2, psycopg2.extras

def get_conn():
    return psycopg2.connect(host="localhost", dbname="futurefix", user="futurefix",
        password="futurefix", cursor_factory=psycopg2.extras.RealDictCursor)

def test_oee_bounds():
    with get_conn() as c, c.cursor() as cur:
        cur.execute("SELECT * FROM v_oee_by_shift")
        rows = cur.fetchall()
        assert len(rows) > 0
        for r in rows:
            for f in ("availability","performance","quality","oee"):
                assert r[f] is None or r[f] >= 0

def test_availability_matches_raw():
    with get_conn() as c, c.cursor() as cur:
        cur.execute("SELECT shift_id, machine_id, availability FROM v_oee_by_shift LIMIT 1")
        r = cur.fetchone()
        cur.execute("SELECT planned_start,planned_end,planned_break_min FROM shifts WHERE shift_id=%s",(r["shift_id"],))
        s = cur.fetchone()
        cur.execute("""SELECT COALESCE(SUM(duration_s),0) run FROM machine_states
            WHERE machine_id=%s AND state='RUNNING' AND state_start>=%s AND state_start<%s""",
            (r["machine_id"], s["planned_start"], s["planned_end"]))
        run = cur.fetchone()["run"]
        planned = (s["planned_end"]-s["planned_start"]).total_seconds() - s["planned_break_min"]*60
        assert abs(float(r["availability"]) - run/planned) < 0.001