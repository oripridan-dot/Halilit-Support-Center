#!/usr/bin/env bash
# Double-click this file on Mac to start the app (Operator Console).
# Runs factory_reset.sh from the project folder. See docs/QUICK_START.md.

cd "$(dirname "$0")"
chmod +x factory_reset.sh start_console.sh 2>/dev/null || true
exec ./factory_reset.sh
