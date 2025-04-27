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

WORKDIR /base

# Копируем файлы, начинающиеся на poetry.lock
COPY pyproject.toml poetry.lock* /base/

RUN poetry config virtualenvs.create false \
    && poetry install --no-root --only main

COPY app /base/app
COPY mango_test /base/mango_test
COPY alembic.ini /base/
COPY wait_for_db.sh /base/wait_for_db.sh

