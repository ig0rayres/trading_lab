FROM python:3.12-slim
RUN apt-get update && apt-get install -y --no-install-recommends git ca-certificates && rm -rf /var/lib/apt/lists/*
WORKDIR /app
COPY src /app/src
COPY tests /app/tests
COPY data /app/data
COPY config /app/config
COPY migrations /app/migrations
COPY scripts /app/scripts
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt
ARG UPSTREAM_COMMIT=3d0f4ef6986f4984b7c6bd46f7ff4f87744c3abd
ENV UPSTREAM_DIR=/app/vendor/day-trader-skill
ENV UPSTREAM_COMMIT=${UPSTREAM_COMMIT}
RUN mkdir -p /app/vendor \
    && git clone --depth 1 https://github.com/Jakeschincariol/day-trader-skill /app/vendor/day-trader-skill \
    && cd /app/vendor/day-trader-skill \
    && git fetch --depth 1 origin ${UPSTREAM_COMMIT} \
    && git checkout ${UPSTREAM_COMMIT} \
    && test "$(git rev-parse HEAD)" = "${UPSTREAM_COMMIT}"
RUN chmod +x /app/scripts/*.sh
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 LIVE_TRADING_ENABLED=false
ENTRYPOINT ["/app/scripts/run.sh"]
CMD ["v4-scheduler", "--universe", "/app/config/universe.json", "--output-dir", "/app/reports/v4", "--interval-seconds", "900", "--timeout-seconds", "180"]
