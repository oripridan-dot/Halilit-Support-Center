#!/bin/bash
set -e
echo "Running Pipeline (Moog only for speed if possible, otherwise full)..."
# Just run the test pipeline which processes all brands found in data/brands
PYTHONPATH=. python3 backend/ingestion/test_real_data_pipeline.py

echo "Running Sync to Frontend..."
PYTHONPATH=. python3 backend/ingestion_to_frontend.py

echo "Done."
