-- Silver: limpa, tipa, deduplica e deriva colunas a partir de `bronze`.
CREATE OR REPLACE TABLE silver AS
SELECT DISTINCT
    pair,
    CAST(bid AS DECIMAL(18,8))                         AS bid,
    CAST(ask AS DECIMAL(18,8))                         AS ask,
    (CAST(bid AS DECIMAL(18,8)) + CAST(ask AS DECIMAL(18,8))) / 2 AS mid,
    CAST(ask AS DECIMAL(18,8)) - CAST(bid AS DECIMAL(18,8))       AS spread,
    CAST(fetched_at AS TIMESTAMPTZ)                    AS fetched_at,
    CAST(provider_timestamp AS TIMESTAMPTZ)           AS provider_timestamp,
    provider_name,
    CAST(fetched_at AS DATE)                           AS day,
    EXTRACT(hour FROM CAST(fetched_at AS TIMESTAMPTZ)) AS hour
FROM bronze
WHERE bid > 0 AND ask > 0 AND ask >= bid;
