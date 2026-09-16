FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    STREAMLIT_SERVER_HEADLESS=true \
    STREAMLIT_SERVER_ENABLECORS=false \
    STREAMLIT_SERVER_ENABLEXSRSFPROTECTION=true \
    HOME=/tmp/app-home \
    FINOPS_HEALTH_HOST=0.0.0.0 \
    FINOPS_HEALTH_PORT=8080

WORKDIR /app

RUN groupadd --system app \
    && useradd --system --gid app --home-dir /tmp/app-home --shell /usr/sbin/nologin app \
    && mkdir -p /tmp/app-home /tmp/streamlit \
    && chown -R app:app /tmp/app-home /tmp/streamlit

COPY dashboard/requirements.txt /app/dashboard/requirements.txt
RUN pip install --no-cache-dir -r /app/dashboard/requirements.txt

COPY --chown=app:app . /app

USER app

EXPOSE 8501 8080

HEALTHCHECK --interval=30s --timeout=5s --start-period=20s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8080/health', timeout=3)"

CMD ["python", "-m", "deployment.entrypoint"]
