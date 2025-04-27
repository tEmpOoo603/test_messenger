FROM python:3.11-alpine

LABEL authors="Efim Aniskin"

RUN apk update && \
    apk add --no-cache \
    curl \
    build-base \
    gcc \
    musl-dev \
    libffi-dev \
    openssl-dev \
    postgresql-dev

RUN curl -sSL https://install.python-poetry.org | python3 -

#Путь для root
ENV PATH="/root/.local/bin:$PATH"

WORKDIR /app

# Копируем файлы, начинающиеся на poetry.lock
COPY pyproject.toml poetry.lock* /app/

RUN poetry config virtualenvs.create false \
    && poetry install --no-root --only main

COPY alembic.ini /app/alembic

COPY ./migrations /app/migrations

COPY . /app

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]