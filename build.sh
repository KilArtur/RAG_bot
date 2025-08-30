#!/bin/bash

cd server/src
uv run main.py &
BACKEND_PID=$!

cd ../../front
python -m http.server 8001 &
FRONTEND_PID=$!

echo "Backend running on http://localhost:8000"
echo "Frontend running on http://localhost:8001"

trap "kill $BACKEND_PID $FRONTEND_PID" EXIT
wait