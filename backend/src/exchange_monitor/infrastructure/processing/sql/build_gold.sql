-- Gold diário: indicadores por par/dia.
CREATE OR REPLACE TABLE gold_daily AS
SELECT
    pair,
    day,
    first(mid ORDER BY fetched_at)  AS open,
    last(mid ORDER BY fetched_at)   AS close,
    max(mid)                        AS high,
    min(mid)                        AS low,
    avg(mid)                        AS avg_mid,
    stddev_samp(mid)                AS volatility,
    avg(spread)                     AS avg_spread,
    (last(mid ORDER BY fetched_at) - first(mid ORDER BY fetched_at))
        / first(mid ORDER BY fetched_at) * 100 AS variation_pct,
    count(*)                        AS tick_count
FROM silver
GROUP BY pair, day;

-- Gold horário: contagem de eventos por par/hora.
CREATE OR REPLACE TABLE gold_hourly AS
SELECT pair, day, hour, count(*) AS events_count
FROM silver
GROUP BY pair, day, hour;
