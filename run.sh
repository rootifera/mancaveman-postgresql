#!/bin/bash

# Check the MODE environment variable
if [ "$MODE" = "multi" ]; then
    # Start in multithreaded mode
    echo "Starting in multithreaded mode with Gunicorn..."
    gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker --threads 2 -b 0.0.0.0:8080
else
    # Start in single-threaded mode
    echo "Starting in single-threaded mode with Uvicorn..."
    uvicorn main:app --host 0.0.0.0 --port 8080
fi
