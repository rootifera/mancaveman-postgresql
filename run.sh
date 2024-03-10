#!/bin/bash

set -a
[ -f .env ] && . .env
set +a

ACCESS_LOG="./logs/access.log"
ERROR_LOG="./logs/error.log"

mkdir -p ./logs

chmod -R 755 /app/logs

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
