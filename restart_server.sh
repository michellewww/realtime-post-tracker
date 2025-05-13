#!/bin/bash

echo "Stopping any existing server processes..."
pkill -f "uvicorn backend.main:app" || true

echo "Starting the FastAPI server..."
cd $(dirname "$0")
source env/bin/activate
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000 