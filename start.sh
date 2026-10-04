#!/bin/bash
# Double-click to run (macOS). Serves the chart at http://localhost:8765 and opens it.
cd "$(dirname "$0")"
PORT=8765
( sleep 1; open "http://localhost:$PORT" ) &
echo "Serving Hoff Aran chart at http://localhost:$PORT  (close this window or press Ctrl+C to stop)"
python3 -m http.server $PORT --bind 127.0.0.1
