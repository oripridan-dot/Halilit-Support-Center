#!/usr/bin/env bash
# Double-click this file on Mac to start the app and open it in your browser.
# (Same as start.sh but runs in Terminal from the project folder.)

cd "$(dirname "$0")"
chmod +x start.sh 2>/dev/null || true
exec ./start.sh
