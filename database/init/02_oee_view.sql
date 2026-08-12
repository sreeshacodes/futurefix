CREATE VIEW v_oee_by_shift AS
WITH avail AS (
  SELECT s.shift_id, s.machine_id,
    EXTRACT(EPOCH FROM (s.planned_end - s.planned_start)) - s.planned_break_min*60 AS planned_s,
    COALESCE(SUM(ms.duration_s) FILTER (WHERE ms.state='RUNNING'),0) AS run_s
  FROM shifts s
  LEFT JOIN machine_states ms ON ms.machine_id = s.machine_id
    AND ms.state_start >= s.planned_start AND ms.state_start < s.planned_end
  GROUP BY s.shift_id, s.machine_id, s.planned_start, s.planned_end, s.planned_break_min
),
perf AS (
  SELECT pe.shift_id, pe.machine_id, SUM(pm.ideal_cycle_time_s) AS ideal_time_s
  FROM production_events pe JOIN part_master pm USING (part_number)
  GROUP BY pe.shift_id, pe.machine_id
),
qual AS (
  SELECT shift_id, machine_id,
    COUNT(*) FILTER (WHERE quality_status='GOOD') AS good_count, COUNT(*) AS total_count
  FROM production_events GROUP BY shift_id, machine_id
)
SELECT a.shift_id, a.machine_id,
  a.run_s / NULLIF(a.planned_s,0) AS availability,
  perf.ideal_time_s / NULLIF(a.run_s,0) AS performance,
  qual.good_count::NUMERIC / NULLIF(qual.total_count,0) AS quality,
  (a.run_s/NULLIF(a.planned_s,0)) * (perf.ideal_time_s/NULLIF(a.run_s,0)) * (qual.good_count::NUMERIC/NULLIF(qual.total_count,0)) AS oee
FROM avail a JOIN perf USING (shift_id, machine_id) JOIN qual USING (shift_id, machine_id);