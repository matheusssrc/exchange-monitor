# Trillia Exchange Monitor — Backend

API e domínio do monitor de câmbio. Implementado em **Python 3.12** com **FastAPI** e
**Clean Architecture**: o domínio não conhece framework nem banco; a persistência fica
atrás da porta `RateRepository` e o provedor de cotações atrás de `RateProvider`.

## Camadas

```
src/trillia_monitor/
├── domain/           # CurrencyPair, ExchangeRate, invariantes e erros tipados
├── application/      # Casos de uso + portas (RateRepository, RateProvider)
└── infrastructure/
    ├── api/          # App FastAPI, routers, middleware, handlers
    ├── persistence/  # SQLAlchemy (modelos, mappers, repositório), sessão async
    ├── providers/    # Cliente + provider AwesomeAPI (httpx + tenacity)
    ├── scheduler/    # collect_pair() usado pelo Airflow
    ├── migrations/   # Alembic
    └── observability/# structlog + métricas Prometheus
```

## Stack

Python 3.12 · FastAPI · SQLAlchemy 2 (async) + asyncpg · Alembic · Pydantic v2 +
pydantic-settings · httpx + tenacity · structlog · prometheus-client.

## Rodando

A forma recomendada é via Docker Compose na raiz do repositório (`docker compose up -d --build`).
Para desenvolvimento local:

```bash
cd backend
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -e ".[dev]"

# Suba um Postgres e exporte TRILLIA_DATABASE_URL apontando para ele.
python -m trillia_monitor migrate                    # aplica as migrations (alembic upgrade head)
python -m trillia_monitor api --host 0.0.0.0 --port 8000
```

### CLI (`trillia-monitor`)

| Comando | Descrição |
|---|---|
| `api [--host --port]` | Sobe a API FastAPI (uvicorn). |
| `migrate` | Aplica as migrations Alembic (`upgrade head`). |
| `collect <PAR>` | Coleta e persiste uma cotação para o par (usado pelo Airflow). |
| `worker` | Worker APScheduler (alternativa local ao Airflow). |

```bash
python -m trillia_monitor collect BRL-USD
```

## API

| Método | Rota | Descrição |
|---|---|---|
| GET | `/rates/latest?pair=BRL-USD` | Cotação mais recente (404 se não houver) |
| GET | `/rates/history?pair=&start_date=&end_date=&limit=&offset=` | Histórico paginado |
| GET | `/pairs` | Pares monitorados |
| GET | `/health` · `/ready` | Liveness / readiness |
| GET | `/metrics` | Exposição Prometheus |

Documentação interativa (Swagger) em `http://localhost:8000/docs`.

## Persistência idempotente

Cada cotação é gravada com `ON CONFLICT DO NOTHING` sobre uma constraint única
`(pair, fetched_at, provider_name)`, de modo que coletas repetidas não geram lixo e o
histórico cresce de forma consistente.

## Testes e qualidade

```bash
pytest                 # unit + integração (testcontainers sobe Postgres efêmero)
ruff check .           # lint
mypy .                 # tipagem estrita
```

`pytest-asyncio` em modo `auto`; integração de repositório usa `testcontainers[postgres]`.

## Configuração

Via variáveis de ambiente com prefixo `TRILLIA_` (ver [`.env.example`](../.env.example)):
`TRILLIA_DATABASE_URL`, `TRILLIA_MONITORED_PAIRS`, `TRILLIA_POLLING_INTERVAL_SECONDS`,
`TRILLIA_AWESOMEAPI_BASE_URL`, `TRILLIA_PROVIDER_TIMEOUT_SECONDS`,
`TRILLIA_PROVIDER_RETRY_ATTEMPTS`, `TRILLIA_LOG_LEVEL`, `TRILLIA_LOG_JSON`.

---

Licença MIT · Matheus Rossi Carvalho.
