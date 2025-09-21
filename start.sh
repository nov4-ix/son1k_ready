#!/bin/bash

# Railway startup script
echo "🚀 Starting Son1k Railway app..."

# Get port from environment or use default
PORT=${PORT:-8000}

echo "📍 Using port: $PORT"
echo "🔗 App will be available at: http://0.0.0.0:$PORT"

# Start the application
exec uvicorn main-railway:app --host 0.0.0.0 --port $PORT