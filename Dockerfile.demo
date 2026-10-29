FROM python:3.12-slim
RUN apt-get update && apt-get install -y --no-install-recommends git ca-certificates && rm -rf /var/lib/apt/lists/*
WORKDIR /app
COPY src /app/src
COPY tests /app/tests
COPY data /app/data
COPY config /app/config
COPY scripts /app/scripts
RUN chmod +x /app/scripts/*.sh
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 LIVE_TRADING_ENABLED=false
ENTRYPOINT ["/app/scripts/run.sh"]
CMD ["v4-scheduler", "--universe", "/app/config/universe.json", "--output-dir", "/app/reports/v4", "--interval-seconds", "900", "--timeout-seconds", "180"]
