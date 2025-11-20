web: gunicorn final_backend:application --bind 0.0.0.0:${PORT:-8080} --workers 4 --timeout 120 --log-level info --access-logfile - --error-logfile -
# Optional: Uncomment to enable Celery worker for background tasks
# worker: celery -A final_backend.celery worker --loglevel=info
# Optional: Uncomment to enable Flower for Celery monitoring
# flower: celery -A final_backend.celery flower --port=5555
