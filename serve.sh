#!/usr/bin/env bash
# Start the Book Tracker API as a persistent background server on port 8000.
cd "$(dirname "$0")"

# Free the port if a stale server is still bound to it.
fuser -k 8000/tcp 2>/dev/null
sleep 1

setsid ./venv/bin/uvicorn main:app --host 0.0.0.0 --port 8000 \
  > /tmp/uvicorn.log 2>&1 < /dev/null &

# Wait until it accepts connections.
for _ in $(seq 1 20); do
  curl -s -o /dev/null http://127.0.0.1:8000/health && break
  sleep 0.5
done
echo "server up on :8000 (pid $(pgrep -f 'uvicorn main:app' | head -1))"
