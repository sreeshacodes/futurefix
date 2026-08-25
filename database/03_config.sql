INSERT INTO app_config (config_key, config_value)
VALUES
(
  'machine_order',
  '["M1","M2","M3"]'
),
(
  'oee_thresholds',
  '{"green":0.85,"amber":0.70}'
),
(
  'default_days',
  '7'
),
(
  'refresh_seconds',
  '30'
)
ON CONFLICT (config_key) DO NOTHING;