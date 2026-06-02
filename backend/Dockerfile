FROM python:3.12-slim AS base
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

FROM base AS deps
WORKDIR /app
RUN apt-get update && apt-get install -y --no-install-recommends \
        build-essential libpq-dev \
    && rm -rf /var/lib/apt/lists/*
COPY pyproject.toml ./
COPY src ./src
RUN pip install --upgrade pip && pip install --prefix=/install .

FROM base AS runtime
WORKDIR /app
RUN apt-get update && apt-get install -y --no-install-recommends \
        libpq5 wget \
    && rm -rf /var/lib/apt/lists/* \
    && useradd --create-home --uid 1001 trillia
COPY --from=deps /install /usr/local
COPY src ./src
COPY alembic.ini ./
USER trillia
ENV PYTHONPATH=/app/src
ENTRYPOINT ["python", "-m", "trillia_monitor"]
CMD ["api"]
