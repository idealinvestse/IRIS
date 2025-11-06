# IRIS v6.0 Dockerfile
# Multi-stage build för optimal storlek och säkerhet

# =============================================================================
# Base Image - Python 3.12 med svenska locale
# =============================================================================
FROM python:3.12-slim as base

# Metadata
LABEL maintainer="IRIS Team"
LABEL version="6.0.0"
LABEL description="Förenklad och Robust Intelligensrapportering för Svenska Användare"

# Systemvariabler
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    DEBIAN_FRONTEND=noninteractive

# Installera systempaket
RUN apt-get update && apt-get install -y \
    # Grundläggande verktyg
    curl \
    wget \
    git \
    build-essential \
    # Språkstöd
    locales \
    # Databas-drivrutiner
    libpq-dev \
    # För spaCy svenska modeller
    python3-dev \
    # Rensning
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Konfigurera svenska locale
RUN sed -i '/sv_SE.UTF-8/s/^# //g' /etc/locale.gen && \
    locale-gen && \
    update-locale LANG=sv_SE.UTF-8

ENV LANG=sv_SE.UTF-8 \
    LANGUAGE=sv_SE:sv \
    LC_ALL=sv_SE.UTF-8 \
    TZ=Europe/Stockholm

# Skapa applikationsanvändare (säkerhet)
RUN groupadd -r iris && useradd -r -g iris iris

# Skapa applikationsmappar
RUN mkdir -p /app/data /app/logs /app/config && \
    chown -R iris:iris /app

WORKDIR /app

# =============================================================================
# Dependencies Stage - Installera Python-beroenden
# =============================================================================
FROM base as dependencies

# Kopiera requirements
COPY requirements.txt ./

# Installera Python-beroenden
RUN pip install --upgrade pip setuptools wheel && \
    pip install -r requirements.txt

# Installera spaCy svenska modell
RUN python -m spacy download sv_core_news_sm

# =============================================================================
# Development Stage - För utveckling med hot reload
# =============================================================================
FROM dependencies as development

# Installera utvecklingsverktyg
RUN pip install \
    pytest \
    pytest-asyncio \
    black \
    isort \
    mypy \
    ipython \
    jupyter

# Kopiera applikationskod
COPY --chown=iris:iris . .

# Växla till iris-användare
USER iris

# Exponera portar
EXPOSE 8000 8001

# Utvecklingskommando
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload", "--log-level", "debug"]

# =============================================================================
# Production Stage - Optimerad för produktion
# =============================================================================
FROM dependencies as production

# Kopiera endast nödvändiga filer
COPY --chown=iris:iris src/ ./src/
COPY --chown=iris:iris config/ ./config/
COPY --chown=iris:iris alembic.ini ./
COPY --chown=iris:iris migrations/ ./migrations/

# Skapa tom .env för säkerhet
RUN touch .env && chown iris:iris .env

# Växla till iris-användare
USER iris

# Exponera port
EXPOSE 8000

# Hälsokontroll
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:8000/hälsa || exit 1

# Produktionskommando med Gunicorn
CMD ["gunicorn", "src.main:app", \
     "--worker-class", "uvicorn.workers.UvicornWorker", \
     "--workers", "4", \
     "--bind", "0.0.0.0:8000", \
     "--timeout", "120", \
     "--keep-alive", "5", \
     "--max-requests", "1000", \
     "--max-requests-jitter", "100", \
     "--preload", \
     "--log-level", "info", \
     "--access-logfile", "-", \
     "--error-logfile", "-"]

# =============================================================================
# Test Stage - För CI/CD testning
# =============================================================================
FROM production as test

# Installera testberoenden
USER root
RUN pip install pytest pytest-asyncio pytest-cov httpx

# Kopiera tester
COPY --chown=iris:iris tests/ ./tests/

USER iris

# Testkommando
CMD ["python", "-m", "pytest", "tests/", "-v", "--cov=src", "--cov-report=html"]

# =============================================================================
# Builder för statisk analys (valfri)
# =============================================================================
FROM dependencies as lint

USER root
RUN pip install black isort mypy flake8 bandit safety

COPY --chown=iris:iris . .
USER iris

# Linting-kommandon
RUN black --check src/ && \
    isort --check-only src/ && \
    mypy src/ --ignore-missing-imports && \
    flake8 src/ && \
    bandit -r src/ && \
    safety check