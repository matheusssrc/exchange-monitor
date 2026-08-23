-- Q1: variação percentual diária por par (maior movimento primeiro).
SELECT pair, day, open, close, round(variation_pct, 4) AS variation_pct
FROM read_parquet('DAILY_PARQUET')
ORDER BY abs(variation_pct) DESC;
