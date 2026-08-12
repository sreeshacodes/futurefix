CREATE TABLE machines (
  machine_id TEXT PRIMARY KEY, machine_name TEXT, machine_type TEXT,
  cell TEXT, make TEXT, model TEXT, commissioned DATE, rated_kw NUMERIC
);
CREATE TABLE part_master (
  part_number TEXT PRIMARY KEY, description TEXT,
  ideal_cycle_time_s NUMERIC, machine_type TEXT
);
CREATE TABLE downtime_reasons (
  reason_code TEXT PRIMARY KEY, description TEXT, category TEXT, reason_group TEXT
);
CREATE TABLE reject_reasons (
  reject_reason_code TEXT PRIMARY KEY, description TEXT
);
CREATE TABLE shifts (
  shift_id TEXT PRIMARY KEY, machine_id TEXT REFERENCES machines(machine_id),
  shift_date DATE, shift_name TEXT, planned_start TIMESTAMP, planned_end TIMESTAMP,
  planned_break_min INT DEFAULT 0, operator_id TEXT
);
CREATE TABLE machine_states (
  id SERIAL PRIMARY KEY, machine_id TEXT REFERENCES machines(machine_id),
  state_start TIMESTAMP, state_end TIMESTAMP, duration_s INT, state TEXT,
  reason_code TEXT REFERENCES downtime_reasons(reason_code), note TEXT,
  UNIQUE (machine_id, state_start)
);
CREATE INDEX idx_states_machine_time ON machine_states (machine_id, state_start);

CREATE TABLE production_events (
  event_id TEXT PRIMARY KEY, machine_id TEXT REFERENCES machines(machine_id),
  shift_id TEXT REFERENCES shifts(shift_id), ts TIMESTAMP,
  part_number TEXT REFERENCES part_master(part_number),
  cycle_time_s NUMERIC, quality_status TEXT,
  reject_reason_code TEXT REFERENCES reject_reasons(reject_reason_code)
);
CREATE INDEX idx_events_machine_time ON production_events (machine_id, ts);

CREATE TABLE telemetry (
  machine_id TEXT REFERENCES machines(machine_id), ts TIMESTAMP,
  spindle_speed_rpm NUMERIC, spindle_load_pct NUMERIC, spindle_current_a NUMERIC,
  motor_temp_c NUMERIC, vibration_mm_s NUMERIC, coolant_flow_lpm NUMERIC,
  PRIMARY KEY (machine_id, ts)
);

CREATE TABLE app_config (
  config_key TEXT PRIMARY KEY, config_value JSONB NOT NULL
);