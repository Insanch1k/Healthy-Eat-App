FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends build-essential libpq-dev curl \
    && rm -rf /var/lib/apt/lists/* \
    && addgroup --system app \
    && adduser --system --ingroup app app

COPY . /app
RUN pip install --upgrade pip \
    && pip install .
RUN mkdir -p /app/media /app/staticfiles \
    && chmod +x /app/docker/entrypoint.sh \
    && chown -R app:app /app

USER app

ENTRYPOINT ["/app/docker/entrypoint.sh"]
CMD ["gunicorn", "health.wsgi:application", "--bind", "0.0.0.0:8000"]
