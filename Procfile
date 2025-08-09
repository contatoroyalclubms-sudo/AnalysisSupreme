web: gunicorn --bind 0.0.0.0:$PORT --workers 4 --worker-class uvicorn.workers.UvicornWorker --timeout 120 src.api.main:app
worker: python src/workers/background_worker.py
release: python scripts/migrate.py
