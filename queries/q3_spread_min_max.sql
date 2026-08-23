-- Q3: spread médio e faixa (min/max do mid) por par/dia.
SELECT pair, day, round(avg_spread, 6) AS avg_spread, low, high,
       round(high - low, 6) AS mid_range
FROM read_parquet('DAILY_PARQUET')
ORDER BY pair, day;
