#!/bin/bash

# Запуск бэкенда
cd server/src
uv run main.py &
BACKEND_PID=$!

# Запуск фронтенда
cd ../../front
python -m http.server 7001 &
FRONTEND_PID=$!

echo "Backend running on http://localhost:7000"
echo "Frontend running on http://localhost:7001"

trap "kill $BACKEND_PID $FRONTEND_PID" EXIT
wait