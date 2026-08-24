# Entregas — Atividade Avaliativa (Pipeline Big Data)

Índice dos entregáveis do projeto **Exchange Monitor** — pipeline Big Data em arquitetura
Medallion (Bronze / Silver / Gold) para monitoramento de cotações de câmbio.

- **Repositório:** https://github.com/matheusssrc/exchange-monitor (tag `v2.0`)
- **Como executar:** ver o [README principal](../README.md) (`docker compose up -d --build`)
- **Autor:** Matheus Rossi Carvalho

---

## Documentos das entregas

| Entrega | Documento |
|---|---|
| **E1 — Definição do problema** | [entrega-1-definicao.md](entrega-1-definicao.md) |
| **E2 — Diagrama de arquitetura** | [entrega-2-arquitetura.md](entrega-2-arquitetura.md) |
| **E3 — Repositório** | estrutura do projeto no [README principal](../README.md#estrutura-do-projeto) |
| **E4 — Pipeline funcional** | código + instruções no [README principal](../README.md#pipeline-medallion) |
| **E5 — README** | [README principal](../README.md) |
| **E6 — Evidências de execução** | [entrega-6-evidencias.md](entrega-6-evidencias.md) + imagens abaixo |

---

## Evidências de execução (E6)

Capturas do stack real em funcionamento (coleta ao vivo pela AwesomeAPI).

| # | Evidência | Arquivo |
|---|-----------|---------|
| 1 | Ingestão — DAG `collect_rates` (25 execuções, todas com sucesso, a cada 30s) | [assets/01-ingestao-airflow.png](assets/01-ingestao-airflow.png) |
| 2 | Bronze — ticks crus na tabela `exchange_rates` | [assets/02-bronze-rows.png](assets/02-bronze-rows.png) |
| 3 | Silver — camada tratada em Parquet (`mid`, `spread`) | [assets/03-silver-parquet.png](assets/03-silver-parquet.png) |
| 4 | Gold — indicadores por par/dia (OHLC, volatilidade, variação %) | [assets/04-gold-indicadores.png](assets/04-gold-indicadores.png) |
| 5 | Orquestração — DAG `build_medallion` (`build_silver → build_gold → validate_gold`) | [assets/05-dag-medallion.png](assets/05-dag-medallion.png) |
| 6 | Logs — ingestão (`rate.collect.saved`) e validação (`medallion.validate`) | [assets/06-logs.png](assets/06-logs.png) |
| 7 | Consultas analíticas sobre a camada Gold | [assets/07-queries.png](assets/07-queries.png) |
| 8 | Dashboard — candlestick OHLC em tempo quase real | [assets/08-dashboard.png](assets/08-dashboard.png) |

---

## Mapa dos requisitos mínimos (seção 4)

| Requisito | Onde é atendido |
|---|---|
| **4.1 Fonte de dados** | AwesomeAPI (JSON, ~8 pares, coleta a cada 30s). Detalhada em [E1](entrega-1-definicao.md) |
| **4.2 Ingestão** | DAG `collect_rates` (Airflow), automática, micro-batch — evidência 1 |
| **4.3 Armazenamento (Medallion)** | Bronze (`exchange_rates` + JSONL) · Silver/Gold em Parquet — evidências 2–4 |
| **4.4 Processamento/transformação** | DuckDB (dedup, tipos, UTC, `mid`/`spread`, agregações) — camadas Silver/Gold |
| **4.5 Disponibilização (3 queries + 3 indicadores + viz)** | `queries/` + indicadores Gold + dashboard — evidências 4, 7, 8 |
| **4.6 Orquestração** | DAG `build_medallion` com tarefas dependentes — evidência 5 |

## Indicadores produzidos

Spread médio · volatilidade diária (desvio-padrão do `mid`) · variação percentual diária ·
mínimo/máximo do `mid` · OHLC por par/dia · eventos por hora · percentual de registros inválidos.

## Consultas analíticas

- [`queries/q1_variacao_diaria.sql`](../queries/q1_variacao_diaria.sql) — variação % diária por par
- [`queries/q2_ranking_volatilidade.sql`](../queries/q2_ranking_volatilidade.sql) — ranking de volatilidade
- [`queries/q3_spread_min_max.sql`](../queries/q3_spread_min_max.sql) — spread médio + min/max por par/dia
