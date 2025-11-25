web: gunicorn final_backend_postgresql:application --config gunicorn.conf.py
# Optional: Uncomment to enable Celery worker for background tasks
# worker: celery -A final_backend.celery worker --loglevel=info
# Optional: Uncomment to enable Flower for Celery monitoring
# flower: celery -A final_backend.celery flower --port=5555
