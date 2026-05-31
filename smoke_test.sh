#!/usr/bin/env bash
# Smoke test for the Book Tracker CRUD API.
# Starts the server, exercises every endpoint, then shuts it down.
set -u
cd "$(dirname "$0")"

# Free port 8000 in case a stale server is still bound to it.
fuser -k 8000/tcp 2>/dev/null
sleep 1

./venv/bin/uvicorn main:app --host 127.0.0.1 --port 8000 > /tmp/uvicorn.log 2>&1 &
SRV=$!
trap 'kill "$SRV" 2>/dev/null' EXIT

B=http://127.0.0.1:8000
# Wait for the server to accept connections.
for _ in $(seq 1 20); do
  curl -s -o /dev/null "$B/health" && break
  sleep 0.5
done

json='-H Content-Type:application/json'

echo "== POST #1 (Dune, reading) =="
curl -s -X POST "$B/books" $json -d '{"title":"Dune","author":"Herbert","status":"reading"}'; echo
echo "== POST #2 (1984, read, rating 5) =="
curl -s -X POST "$B/books" $json -d '{"title":"1984","author":"Orwell","status":"read","rating":5}'; echo
echo "== POST #3 (Sapiens, default status) =="
curl -s -X POST "$B/books" $json -d '{"title":"Sapiens","author":"Harari"}'; echo

echo "== GET /books (all) =="
curl -s "$B/books"; echo
echo "== GET /books?status=reading =="
curl -s "$B/books?status=reading"; echo
echo "== GET /books/2 =="
curl -s "$B/books/2"; echo
echo "== GET /books/99 (expect 404) =="
curl -s -w "  <- [%{http_code}]" "$B/books/99"; echo

echo "== PUT /books/1 (mark read, rating 4) =="
curl -s -X PUT "$B/books/1" $json -d '{"status":"read","rating":4}'; echo
echo "== PUT /books/99 (expect 404) =="
curl -s -w "  <- [%{http_code}]" -X PUT "$B/books/99" $json -d '{"status":"read"}'; echo

echo "== DELETE /books/2 (expect 200 + message) =="
curl -s -w "  <- [%{http_code}]" -X DELETE "$B/books/2"; echo
echo "== DELETE /books/2 again (expect 404) =="
curl -s -w "  <- [%{http_code}]" -X DELETE "$B/books/2"; echo

echo "== GET /books (after delete) =="
curl -s "$B/books"; echo
echo "== POST invalid, missing author (expect 422) =="
curl -s -o /dev/null -w "[%{http_code}]" -X POST "$B/books" $json -d '{"title":"x"}'; echo
echo "== GET /books/stats (route-order check: must NOT 404 as id=stats) =="
curl -s -w "  <- [%{http_code}]" "$B/books/stats"; echo
