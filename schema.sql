CREATE TABLE ticker_feed (
  timestamp TIMESTAMP DEFAULT NOW(),
  ask NUMERIC,
  bid NUMERIC,
  last NUMERIC,
  low NUMERIC,
  high NUMERIC,
  open NUMERIC,
  volume NUMERIC,
  volume_quote NUMERIC
);

CREATE TABLE order_feed (
  timestamp TIMESTAMP DEFAULT NOW(),
  quantity NUMERIC,
  side VARCHAR(10),
  status VARCHAR(10),
  uuid TEXT,
  usd_balance NUMERIC,
  btc_balance NUMERIC,
  current_price NUMERIC
);

CREATE TABLE prediction_feed (
  timestamp TIMESTAMP DEFAULT NOW(),
  prediction_timestamp NUMERIC,
  prediction_weight NUMERIC,
  prediction_history TEXT[],
  status VARCHAR(10),
  uuid TEXT,
  prediction_percent NUMERIC
);