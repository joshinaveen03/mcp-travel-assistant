#!/bin/bash
set -e

STREAMLIT_PORT="${PORT:-8501}"

echo "Starting FastAPI backend on port 8000..."
python -m uvicorn backend:app --host 0.0.0.0 --port 8000 &

echo "Waiting for FastAPI backend to be ready..."
for i in $(seq 1 30); do
  if curl -s http://127.0.0.1:8000/health > /dev/null 2>&1; then
    echo "FastAPI backend is ready!"
    break
  fi
  sleep 1
done

echo "Starting Streamlit frontend on port ${STREAMLIT_PORT}..."
exec streamlit run app.py \
  --server.port="${STREAMLIT_PORT}" \
  --server.address=0.0.0.0 \
  --server.enableCORS=false \
  --server.enableXsrfProtection=false \
  --server.headless=true
