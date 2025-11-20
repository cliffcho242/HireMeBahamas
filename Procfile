web: gunicorn final_backend_postgresql:application --bind 0.0.0.0:${PORT:-8080} --workers 4 --timeout 120 --log-level info --access-logfile - --error-logfile -
