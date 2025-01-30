#!/bin/bash

if [ "$1" == "prod" ]; then
    echo "🚀 Running in production mode..."
    uvicorn app.main:create_app --host 0.0.0.0 --port 80
else
    echo "🛠️ Running in development mode..."
    uvicorn app.main:create_app --host 0.0.0.0 --port 8000 --reload
fi
