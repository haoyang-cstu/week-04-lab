#!/usr/bin/env bash
# Part 6 manual-test sequence, run against the already-running server on :8000.
set -u
B=http://127.0.0.1:8000
json='-H Content-Type:application/json'

echo "1) GET /books (expect empty list)"
curl -s "$B/books"; echo; echo

echo "2) POST Dune (read, rating 5)"
curl -s -X POST "$B/books" $json -d '{"title":"Dune","author":"Frank Herbert","status":"read","rating":5}'; echo; echo
echo "3) POST 1984 (reading)"
curl -s -X POST "$B/books" $json -d '{"title":"1984","author":"George Orwell","status":"reading"}'; echo; echo
echo "4) POST Clean Code (want_to_read)"
curl -s -X POST "$B/books" $json -d '{"title":"Clean Code","author":"Robert Martin","status":"want_to_read"}'; echo; echo

echo "5) GET /books (expect all 3)"
curl -s "$B/books"; echo; echo
echo "6) GET /books?status=reading (expect only 1984)"
curl -s "$B/books?status=reading"; echo; echo
echo "7) GET /books/1 (expect Dune)"
curl -s "$B/books/1"; echo; echo
echo "8) PUT /books/2 (1984 -> read, rating 4)"
curl -s -X PUT "$B/books/2" $json -d '{"status":"read","rating":4}'; echo; echo
echo "9) GET /books/stats"
curl -s "$B/books/stats"; echo; echo
echo "10) DELETE /books/3 (Clean Code)"
curl -s -X DELETE "$B/books/3"; echo; echo
echo "11) GET /books (expect 2 books)"
curl -s "$B/books"; echo; echo
