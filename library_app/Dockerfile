# Usar Python 3.10
FROM python:3.10-slim

ENV POETRY_VIRTUALENVS_CREATE=false
ENV PYTHONUNBUFFERED=1
ENV PATH="/root/.local/bin:$PATH"

WORKDIR /app

RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \ 
    curl \
    && rm -rf /var/lib/apt/lists/*

RUN curl -sSL https://install.python-poetry.org | python3 -

COPY pyproject.toml poetry.lock* ./


RUN poetry install --no-interaction --no-ansi --only main

COPY . .

WORKDIR /app/src

EXPOSE 8550

CMD ["python", "app.py"]
