# Entrega 1 — Definição do Problema

## Tema

Monitoramento contínuo de cotações de câmbio (pares BRL/USD/EUR e demais moedas), com
consolidação do histórico em camadas tratadas para análise.

## Problema

Cotações chegam como eventos crus, de alta frequência e com ruído (ticks repetidos, campos em
formato textual, fusos distintos). É preciso ingerir esse fluxo de forma automática, limpá-lo
e agregá-lo em uma camada pronta para consulta, de modo que indicadores históricos
(volatilidade, variação diária, spread) possam ser produzidos sem reprocessar o dado bruto a
cada consulta.

## Público interessado

- Analistas financeiros e times de risco que precisam de séries históricas confiáveis.
- Traders de varejo interessados na variação e volatilidade diária por par.
- Times de dados/BI que consomem indicadores agregados (camada Gold) para relatórios.

## Fonte de dados

- **Origem:** API pública **AwesomeAPI** — endpoint `economia.awesomeapi.com.br/last/<par>`.
- **Formato:** JSON. Cada par retorna um objeto com `bid`, `ask`, `timestamp` (Unix), `code`,
  `codein`, entre outros campos. Os valores numéricos vêm como **string**.
- **Volume:** ~8 pares monitorados, 1 coleta a cada 30s → ≈ 16 ticks/min → **≈ 23 mil
  registros/dia**. O histórico cresce de forma contínua e cumulativa.
- **Frequência de geração:** contínua; coleta agendada a cada 30s (configurável via
  `EXCHANGE_POLLING_INTERVAL_SECONDS`).
- **Problemas de qualidade tratados no pipeline:**
  - ticks duplicados do mesmo instante (dedup por `pair + fetched_at + provider_name`);
  - valores numéricos como texto (cast para `DECIMAL(18,8)`);
  - `timestamp` em Unix e fuso implícito (normalização para UTC);
  - eventuais valores inconsistentes (`bid`/`ask` ≤ 0 ou `ask < bid`) descartados na camada
    Silver, com medição do **percentual de registros inválidos**.

## Indicadores produzidos

A partir da camada Gold (agregação por par/dia e por par/hora):

- **Spread médio** (`ask − bid`);
- **Volatilidade diária** (desvio-padrão do `mid`);
- **Variação percentual diária** (`(close − open) / open`);
- **Mínimo/máximo do `mid`** e a faixa do dia (`high − low`);
- **OHLC** (abertura, fechamento, máxima, mínima) por par/dia;
- **Eventos por hora** (contagem de coletas por par/hora);
- **Percentual de registros inválidos** (qualidade dos dados).

## Proposta inicial de arquitetura

Pipeline batch/micro-batch local em arquitetura Medallion:

```
AwesomeAPI (fonte)
   → Ingestão automática (Airflow, DAG collect_rates, 30s)
   → Bronze (tabela exchange_rates + JSONL cru em data/bronze/)
   → Silver (DuckDB → Parquet limpo, tipado, validado)
   → Gold (DuckDB → Parquet com indicadores por par/dia e por par/hora)
   → Consulta (queries DuckDB/SQL) + Dashboard React (candlestick OHLC)
   → Monitoramento (Prometheus /metrics)
```

A orquestração da construção das camadas é feita por uma segunda DAG (`build_medallion`) com
tarefas dependentes (Silver → Gold → validação). Detalhe completo do fluxo na Entrega 2.
