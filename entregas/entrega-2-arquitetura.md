# Entrega 2 — Diagrama de Arquitetura

O diagrama abaixo mostra o fluxo completo dos dados: fonte, ingestão, armazenamento em
camadas (Bronze/Silver/Gold), processamento, orquestração, consulta, visualização e
monitoramento. As setas indicam o sentido do fluxo dos dados.

```mermaid
flowchart TD
  EXT["AwesomeAPI<br/>(fonte de dados — JSON)"]

  subgraph ING["Ingestão — Airflow"]
    DAG1["DAG collect_rates<br/>(30s, 1 task por par)"]
    DAG2["DAG build_medallion<br/>(silver → gold → validate)"]
  end

  BR["Bronze<br/>tabela exchange_rates<br/>+ data/bronze/*.jsonl (cru)"]
  SI["Silver<br/>data/silver/silver.parquet<br/>(limpo · tipado · UTC · validado)"]
  GO["Gold<br/>data/gold/gold_daily.parquet<br/>gold_hourly.parquet (indicadores)"]

  Q["Consultas analíticas<br/>queries/*.sql (DuckDB)"]
  DASH["Dashboard React<br/>candlestick OHLC (:8080)"]
  API["API FastAPI (:8000)"]
  MON["Monitoramento<br/>Prometheus /metrics"]

  EXT -->|coleta| DAG1
  DAG1 -->|grava tick| BR
  DAG1 -->|payload cru| BR
  BR -->|DuckDB build_silver| SI
  SI -->|DuckDB build_gold| GO
  DAG2 -.orquestra.-> SI
  DAG2 -.orquestra.-> GO
  GO --> Q
  BR --> API
  API --> DASH
  MON -.observa.-> API
  MON -.observa.-> ING
```

## Legenda do fluxo

1. **Fonte:** AwesomeAPI fornece cotações em JSON por par.
2. **Ingestão:** a DAG `collect_rates` coleta a cada 30s (uma task por par) e grava o tick no
   Postgres, além de registrar o payload cru em `data/bronze/`.
3. **Bronze:** dado original, sem transformação (tabela `exchange_rates` + JSONL).
4. **Silver:** DuckDB limpa, tipa, normaliza para UTC, calcula `mid`/`spread`, valida e grava
   Parquet.
5. **Gold:** DuckDB agrega por par/dia e por par/hora, produzindo os indicadores em Parquet.
6. **Orquestração:** a DAG `build_medallion` encadeia Silver → Gold → validação, garantindo
   que uma etapa dependente não execute antes da conclusão da anterior.
7. **Consulta e visualização:** as queries em `queries/` leem a camada Gold; o dashboard React
   consome a API e exibe candlesticks OHLC.
8. **Monitoramento:** o Prometheus coleta métricas (`/metrics`) da API e do pipeline.
