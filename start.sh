#!/bin/bash
# Railway startup script: Run migrations before starting the server

echo "🔧 Running database migrations..."
python add_missing_user_columns.py

if [ $? -eq 0 ]; then
    echo "✅ Migrations completed successfully"
else
    echo "⚠️ Warning: Migration script had errors, but continuing..."
fi

echo "🚀 Starting gunicorn server..."
# Using final_backend_postgresql module which supports both PostgreSQL and SQLite
# This module properly handles database initialization and persistence
exec gunicorn final_backend_postgresql:application --bind 0.0.0.0:8080 --workers 4 --timeout 120 --access-logfile - --error-logfile -
