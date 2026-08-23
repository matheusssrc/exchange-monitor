-- Q2: ranking de pares mais voláteis (desvio-padrão do mid).
SELECT pair, round(avg(volatility), 6) AS avg_volatility, sum(tick_count) AS ticks
FROM read_parquet('DAILY_PARQUET')
GROUP BY pair
ORDER BY avg_volatility DESC;
