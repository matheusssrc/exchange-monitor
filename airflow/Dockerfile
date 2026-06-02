FROM apache/airflow:2.10.4-python3.12

USER root
RUN apt-get update \
    && apt-get install -y --no-install-recommends build-essential libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install the Trillia backend into an ISOLATED virtualenv. Airflow 2.10 pins
# SQLAlchemy <2.0; the backend needs SQLAlchemy 2.0. Keeping it in its own venv
# avoids breaking Airflow's metadata ORM. The DAG invokes this venv's CLI.
COPY backend/pyproject.toml /opt/trillia/backend/pyproject.toml
COPY backend/src /opt/trillia/backend/src
RUN python3 -m venv /opt/trillia/venv \
    && /opt/trillia/venv/bin/pip install --no-cache-dir --upgrade pip \
    && /opt/trillia/venv/bin/pip install --no-cache-dir /opt/trillia/backend
# Root owns /opt/trillia; files are world-readable/executable, so the unprivileged
# airflow user can run /opt/trillia/venv/bin/python without an explicit chown.

USER airflow

# Bake the DAGs into the image (reproducible; no host mount needed).
COPY --chown=airflow:airflow airflow/dags /opt/airflow/dags
