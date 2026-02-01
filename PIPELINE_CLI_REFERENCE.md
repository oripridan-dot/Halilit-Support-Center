# Pipeline CLI Reference

## Quick Start

```bash
cd /workspaces/Halilit-Support-Center

# Set Python path and run full pipeline
PYTHONPATH=. python -m backend.pipeline run
```

---

## Commands

### `run` - Full Pipeline Execution

Executes all stages: Ingest → Normalize → Enrich → Optimize → Deploy

```bash
# All brands
PYTHONPATH=. python -m backend.pipeline run

# Specific brands
PYTHONPATH=. python -m backend.pipeline run --brands adam-audio neumann focal

# Skip ingest, use cached data
PYTHONPATH=. python -m backend.pipeline run --skip-ingest

# Skip processing layers
PYTHONPATH=. python -m backend.pipeline run --skip-process

# Skip frontend deployment
PYTHONPATH=. python -m backend.pipeline run --skip-deploy

# Verbose logging
PYTHONPATH=. python -m backend.pipeline run --log-level DEBUG

# Combination example
PYTHONPATH=. python -m backend.pipeline run \
  --brands adam-audio \
  --skip-process \
  --log-level DEBUG
```

**Output**:

- `backend/data/5_golden/{brand}.json` - Production catalogs
- `frontend/public/data/` - Deployed data
- `backend/data/reports/pipeline-*.json` - Execution report
- `frontend/src/types/generated.ts` - TypeScript types

**Typical Duration**: 1-3 minutes per brand

---

### `ingest` - Data Harvesting Only

Harvests data from 3 sources without processing

```bash
# All brands
PYTHONPATH=. python -m backend.pipeline ingest

# Specific brands
PYTHONPATH=. python -m backend.pipeline ingest --brands adam-audio

# With logging
PYTHONPATH=. python -m backend.pipeline ingest --log-level DEBUG
```

**Output**:

- `backend/data/1_official/{brand}.json`
- `backend/data/2_commercial/{brand}.json`
- `backend/data/3_contextual/{brand}.json`

**Typical Duration**: 1-2 minutes per brand

---

### `process` - Layer Processing Only

Runs normalization, enrichment, and optimization layers

```bash
# All brands
PYTHONPATH=. python -m backend.pipeline process

# Specific brands
PYTHONPATH=. python -m backend.pipeline process --brands adam-audio

# Use cached ingestion data
PYTHONPATH=. python -m backend.pipeline process --use-cache
```

**Requirements**: Must have completed `ingest` first

**Output**:

- `backend/data/4_validated/{brand}-normalized.json`
- `backend/data/4_validated/{brand}-enriched.json`
- `backend/data/5_golden/{brand}.json`

**Typical Duration**: 10 seconds per brand

---

### `deploy` - Frontend Deployment Only

Deploys processed data to frontend and generates types

```bash
# Deploy all brands
PYTHONPATH=. python -m backend.pipeline deploy

# Deploy specific brands
PYTHONPATH=. python -m backend.pipeline deploy --brands adam-audio

# Generate TypeScript types
PYTHONPATH=. python -m backend.pipeline types
```

**Output**:

- `frontend/public/data/index.json`
- `frontend/public/data/{brand}.json`
- `frontend/public/data/search_index.json`
- `frontend/src/types/generated.ts`

**Typical Duration**: 5 seconds

---

### `status` - Pipeline Status

Shows current pipeline status and last execution report

```bash
PYTHONPATH=. python -m backend.pipeline status
```

**Output**:

```
Pipeline Status v5.0

Last Run: 2026-01-31 22:21:03 UTC
Duration: 14.3 seconds
Status: ✅ Complete

Brands Processed: 6
Products Total: 6

Errors: 0
Warnings: 2
```

---

### `types` - TypeScript Type Generation

Generates TypeScript types from Pydantic models

```bash
PYTHONPATH=. python -m backend.pipeline types
```

**Output**: `frontend/src/types/generated.ts`

**Includes**:

- Product interfaces
- Brand interfaces
- Catalog interfaces
- Enums (StockStatus, TierLevel, etc.)

---

### `validate` - Data Validation

Validates all data files against schemas

```bash
# Validate all data
PYTHONPATH=. python -m backend.pipeline validate

# Validate specific stage
PYTHONPATH=. python -m backend.pipeline validate --stage 5_golden

# Validate specific brand
PYTHONPATH=. python -m backend.pipeline validate --brands adam-audio

# Show detailed errors
PYTHONPATH=. python -m backend.pipeline validate --verbose
```

**Stages**:

- `1_official` - Official harvester output
- `2_commercial` - Commercial harvester output
- `3_contextual` - Contextual harvester output
- `4_validated` - Normalized & enriched data
- `5_golden` - Final production data

**Output**:

```
Validation Report

Stage 5_golden: ✅ PASS
  - adam-audio.json: ✅ 1 product
  - neumann.json: ✅ 1 product
  - focal.json: ✅ 1 product

Total: 3 brands, 3 products validated
```

---

### `report` - View Execution Report

Shows detailed statistics from last run

```bash
# Latest report
PYTHONPATH=. python -m backend.pipeline report

# Specific report by timestamp
PYTHONPATH=. python -m backend.pipeline report --date 2026-01-31

# Export to CSV
PYTHONPATH=. python -m backend.pipeline report --format csv > report.csv

# Pretty print JSON
PYTHONPATH=. python -m backend.pipeline report --format json | jq .
```

**Report Contents**:

- Execution timestamps
- Processing duration
- Brands processed
- Products per brand
- Errors and warnings
- Quality metrics
- Confidence scores

---

### `clean` - Clean Up Pipeline Data

Removes generated data files

```bash
# Remove all processed data (keep official/commercial/contextual)
PYTHONPATH=. python -m backend.pipeline clean --stage validated golden

# Remove specific brand data
PYTHONPATH=. python -m backend.pipeline clean --brands adam-audio

# Remove everything (dangerous!)
PYTHONPATH=. python -m backend.pipeline clean --all

# Dry run (show what would be deleted)
PYTHONPATH=. python -m backend.pipeline clean --dry-run
```

---

## Options

### Global Options

```
--help, -h              Show help message
--version, -v           Show pipeline version
--log-level LEVEL       Set log level: DEBUG, INFO, WARNING, ERROR
                        Default: INFO
--quiet, -q             Suppress logging output
--json                  Output as JSON (for scripts)
```

### Common Options

```
--brands BRAND1 BRAND2  Process specific brands only
                        Default: all brands

--skip-ingest           Skip data harvesting
--skip-process          Skip layer processing
--skip-deploy           Skip frontend deployment

--use-cache             Use cached ingestion data (don't re-harvest)

--timeout SECONDS       Override timeout (default: 30)
--retries COUNT         Override retry count (default: 3)
--concurrent NUM        Override concurrent operations (default: 3)
```

### Validation Options

```
--stage STAGE           Validate specific stage
                        Options: 1_official, 2_commercial, 3_contextual,
                                 4_validated, 5_golden

--verbose, -v           Show detailed validation errors
--fix                   Attempt to fix validation errors
--strict                Fail on any warning
```

---

## Environment Variables

```bash
# API Keys
export SERP_API_KEY=your_key
export OPENAI_API_KEY=your_key
export GEMINI_API_KEY=your_key

# Scraper
export SCRAPER_HEADLESS=true
export SCRAPER_TIMEOUT_MS=30000
export SCRAPER_RETRIES=3

# Logging
export LOG_LEVEL=INFO

# Then run:
PYTHONPATH=. python -m backend.pipeline run
```

---

## Examples

### Example 1: Initial Setup with Test Brand

```bash
# Test with one brand
PYTHONPATH=. python -m backend.pipeline run \
  --brands test-brand \
  --log-level DEBUG

# Check results
PYTHONPATH=. python -m backend.pipeline status
```

### Example 2: Production Run with Real Data

```bash
# Ensure .env is configured with API keys
source .env

# Run full pipeline
PYTHONPATH=. python -m backend.pipeline run

# Validate output
PYTHONPATH=. python -m backend.pipeline validate --stage 5_golden

# View report
PYTHONPATH=. python -m backend.pipeline report
```

### Example 3: Re-process Without Re-harvesting

```bash
# Use cached data from previous harvest
# (much faster, useful for debugging enrichment/optimization)
PYTHONPATH=. python -m backend.pipeline process --use-cache

# Or specific command:
PYTHONPATH=. python -m backend.pipeline run --skip-ingest
```

### Example 4: Process Multiple Brands in Parallel

```bash
# Process different brands in different terminal windows
PYTHONPATH=. python -m backend.pipeline run --brands adam-audio &
PYTHONPATH=. python -m backend.pipeline run --brands neumann &
PYTHONPATH=. python -m backend.pipeline run --brands focal &

# Wait for all to complete
wait

# Deploy all results
PYTHONPATH=. python -m backend.pipeline deploy
```

### Example 5: Debugging a Single Brand

```bash
# With maximum verbosity
PYTHONPATH=. python -m backend.pipeline run \
  --brands adam-audio \
  --log-level DEBUG

# Check intermediate data
cat backend/data/1_official/adam-audio.json | jq .
cat backend/data/4_validated/adam-audio-normalized.json | jq .
cat backend/data/5_golden/adam-audio.json | jq .
```

---

## Exit Codes

```
0   Success - All operations completed without errors
1   Generic error - Check logs for details
2   Configuration error - Missing or invalid config
3   Data error - Invalid input data
4   Network error - Failed to fetch data
5   Validation error - Data failed validation
```

---

## Performance Tips

### Speed Up Processing

```bash
# Reduce concurrency if memory constrained
SCRAPER_CONCURRENT=1 PYTHONPATH=. python -m backend.pipeline run

# Skip unnecessary stages
PYTHONPATH=. python -m backend.pipeline process --skip-deploy

# Use cache when possible
PYTHONPATH=. python -m backend.pipeline run --skip-ingest
```

### Reduce Memory Usage

```bash
# Process one brand at a time
PYTHONPATH=. python -m backend.pipeline run --brands adam-audio
```

### Speed Up Development

```bash
# Only harvest (skip processing)
PYTHONPATH=. python -m backend.pipeline ingest --brands adam-audio

# Only optimize (skip normalization/enrichment)
PYTHONPATH=. python -m backend.pipeline optimize --brands adam-audio --skip-enrich
```

---

## Troubleshooting

### Command Not Found

```bash
# Make sure you're in the correct directory
cd /workspaces/Halilit-Support-Center

# Make sure PYTHONPATH is set
PYTHONPATH=. python -m backend.pipeline run

# Or use full path
PYTHONPATH=/workspaces/Halilit-Support-Center python -m backend.pipeline run
```

### Module Not Found

```bash
# Install dependencies
pip install pydantic pydantic-settings python-dotenv httpx aiohttp playwright openai

# Ensure __init__.py files exist
touch backend/__init__.py
touch backend/pipeline/__init__.py
touch backend/pipeline/harvesters/__init__.py
touch backend/pipeline/layers/__init__.py
```

### Timeout Issues

```bash
# Increase timeout
SCRAPER_TIMEOUT_MS=60000 PYTHONPATH=. python -m backend.pipeline run

# Or set in .env
echo "SCRAPER_TIMEOUT_MS=60000" >> .env
```

### Memory Errors

```bash
# Reduce concurrent operations
SCRAPER_CONCURRENT=1 python -m backend.pipeline run

# Process brands individually
for brand in adam-audio neumann focal; do
  PYTHONPATH=. python -m backend.pipeline run --brands $brand
done
```

---

## For More Help

```bash
# Show command-specific help
PYTHONPATH=. python -m backend.pipeline run --help
PYTHONPATH=. python -m backend.pipeline ingest --help
PYTHONPATH=. python -m backend.pipeline validate --help

# View logs
tail -f /tmp/halilit-pipeline.log

# Check configuration
PYTHONPATH=. python -m backend.pipeline config --show
```

---

**Last Updated**: 2026-01-31
**Version**: 5.0
