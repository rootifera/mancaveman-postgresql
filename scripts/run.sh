#!/bin/bash

cd "$(dirname "$0")"
# shellcheck disable=SC2103
cd ..

set -a
[ -f .env ] && . .env
set +a

LOGS_DIR="./logs"
ACCESS_LOG="$LOGS_DIR/access.log"
ERROR_LOG="$LOGS_DIR/error.log"

mkdir -p $LOGS_DIR

chmod -R 755 ./logs

echo "Applying database migrations..."
alembic upgrade head
if [ $? -ne 0 ]; then
    echo "Failed to apply migrations."
    exit 1
fi
echo "Database migrations applied successfully."

MAX_CORES=4

CPU_CORES=$(lscpu -p=CORE,SOCKET | grep -v '^#' | sort -u | wc -l)

if [ -z "$CPU_CORES" ] || [ "$CPU_CORES" -eq 0 ]; then
    CPU_CORES=1
fi

if [ "$CORE_LIMIT" = "True" ]; then
    WORKERS=$(($MAX_CORES<$CPU_CORES?$MAX_CORES:$CPU_CORES))
else
    WORKERS=$CPU_CORES
fi

if [ "$WORKERS" -lt 1 ]; then
    WORKERS=1
fi

if [ "$MODE" = "multi" ]; then
    echo "Number of workers: $WORKERS"
    echo "Starting in multithreaded mode with Gunicorn..."
    gunicorn main:app -w $WORKERS -k uvicorn.workers.UvicornWorker --threads 2 -b 0.0.0.0:8080 --access-logfile $ACCESS_LOG --error-logfile $ERROR_LOG
else
    echo "Starting in single-threaded mode with Uvicorn..."
    uvicorn main:app --host 0.0.0.0 --port 8080 --proxy-headers --forwarded-allow-ips '*'
fi
