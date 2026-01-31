"""
Halilit Pipeline CLI - Single entry point for all pipeline operations.

Usage:
    python -m backend.pipeline run [--brands BRAND1,BRAND2] [--skip-ingest] [--skip-deploy]
    python -m backend.pipeline ingest [--brands BRAND1,BRAND2]
    python -m backend.pipeline process [--brands BRAND1,BRAND2]  
    python -m backend.pipeline deploy
    python -m backend.pipeline types
    python -m backend.pipeline status
"""

import argparse
import asyncio
import logging
import sys
from pathlib import Path

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)-7s | %(message)s',
    datefmt='%H:%M:%S'
)


def setup_parser() -> argparse.ArgumentParser:
    """Create argument parser."""
    parser = argparse.ArgumentParser(
        prog="pipeline",
        description="Halilit Data Pipeline v5.0 - Single source of truth for all data processing",
    )

    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug logging",
    )

    subparsers = parser.add_subparsers(
        dest="command", help="Available commands")

    # run - Full pipeline
    run_parser = subparsers.add_parser("run", help="Run the complete pipeline")
    run_parser.add_argument(
        "--brands",
        type=str,
        help="Comma-separated list of brand IDs to process",
    )
    run_parser.add_argument(
        "--skip-ingest",
        action="store_true",
        help="Skip data harvesting, use cached data",
    )
    run_parser.add_argument(
        "--skip-process",
        action="store_true",
        help="Skip layer processing",
    )
    run_parser.add_argument(
        "--skip-deploy",
        action="store_true",
        help="Skip frontend deployment",
    )

    # ingest - Only harvest data
    ingest_parser = subparsers.add_parser(
        "ingest", help="Harvest data from sources")
    ingest_parser.add_argument(
        "--brands",
        type=str,
        help="Comma-separated list of brand IDs to process",
    )

    # process - Only process through layers
    process_parser = subparsers.add_parser(
        "process", help="Process data through layers")
    process_parser.add_argument(
        "--brands",
        type=str,
        help="Comma-separated list of brand IDs to process",
    )

    # deploy - Only deploy to frontend
    subparsers.add_parser("deploy", help="Deploy catalogs to frontend")

    # types - Generate TypeScript types
    subparsers.add_parser(
        "types", help="Generate TypeScript types from models")

    # status - Show pipeline status
    subparsers.add_parser(
        "status", help="Show pipeline status and data summary")

    return parser


def parse_brands(brands_arg: str) -> list:
    """Parse comma-separated brand list."""
    if not brands_arg:
        return None
    return [b.strip() for b in brands_arg.split(",") if b.strip()]


async def cmd_run(args) -> int:
    """Execute full pipeline."""
    from .runner import run_pipeline

    brand_ids = parse_brands(args.brands)

    report = await run_pipeline(
        brand_ids=brand_ids,
        skip_ingest=args.skip_ingest,
        skip_process=args.skip_process,
        skip_deploy=args.skip_deploy,
    )

    if report.get("errors"):
        print(f"\n⚠️ Completed with {len(report['errors'])} errors")
        return 1

    print(f"\n✅ Pipeline complete!")
    return 0


async def cmd_ingest(args) -> int:
    """Execute ingestion only."""
    from .runner import PipelineRunner

    runner = PipelineRunner()
    brand_ids = parse_brands(args.brands)

    report = await runner.run_full_pipeline(
        brand_ids=brand_ids,
        skip_process=True,
        skip_deploy=True,
    )

    print(f"✅ Ingestion complete: {report['brands_processed']} brands")
    return 0


def cmd_process(args) -> int:
    """Execute processing only."""
    from .runner import process_layers

    brand_ids = parse_brands(args.brands)
    report = process_layers(brand_ids)

    print(f"✅ Processing complete: {report['products_total']} products")
    return 0


def cmd_deploy(args) -> int:
    """Execute deployment only."""
    from .runner import deploy_catalog

    deploy_catalog()
    print("✅ Deployment complete!")
    return 0


def cmd_types(args) -> int:
    """Generate TypeScript types."""
    from .typescript_generator import generate_types
    from .config import config

    output_path = config.TYPES_OUTPUT_PATH
    generate_types(output_path)
    print(f"✅ Generated TypeScript types at {output_path}")
    return 0


def cmd_status(args) -> int:
    """Show pipeline status."""
    from .config import config
    import json

    print("\n📊 Pipeline Status")
    print("=" * 60)

    # Check directories
    dirs = {
        "Official Data": config.OFFICIAL_DIR,
        "Commercial Data": config.COMMERCIAL_DIR,
        "Contextual Data": config.CONTEXTUAL_DIR,
        "Validated Data": config.VALIDATED_DIR,
        "Golden Catalogs": config.GOLDEN_DIR,
        "Frontend Data": config.FRONTEND_DATA_DIR,
    }

    for name, path in dirs.items():
        if path.exists():
            count = len(list(path.glob("*.json")))
            print(f"  {name}: {count} files")
        else:
            print(f"  {name}: (not created)")

    print()

    # Check frontend index
    index_file = config.FRONTEND_DATA_DIR / "index.json"
    if index_file.exists():
        with open(index_file, 'r') as f:
            index = json.load(f)
        print(f"📦 Frontend Catalog:")
        print(f"   Version: {index.get('version', 'unknown')}")
        print(f"   Brands: {len(index.get('brands', []))}")
        print(f"   Products: {index.get('total_products', 0)}")
        print(f"   Verified: {index.get('total_verified', 0)}")
        print(f"   Last Build: {index.get('build_timestamp', 'unknown')}")
    else:
        print("📦 Frontend Catalog: Not deployed yet")

    print()
    return 0


def main() -> int:
    """Main entry point."""
    parser = setup_parser()
    args = parser.parse_args()

    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)

    if not args.command:
        parser.print_help()
        return 1

    try:
        if args.command == "run":
            return asyncio.run(cmd_run(args))
        elif args.command == "ingest":
            return asyncio.run(cmd_ingest(args))
        elif args.command == "process":
            return cmd_process(args)
        elif args.command == "deploy":
            return cmd_deploy(args)
        elif args.command == "types":
            return cmd_types(args)
        elif args.command == "status":
            return cmd_status(args)
        else:
            parser.print_help()
            return 1

    except KeyboardInterrupt:
        print("\n⏹️ Pipeline interrupted")
        return 130
    except Exception as e:
        logging.error(f"Pipeline failed: {e}")
        if args.debug:
            raise
        return 1


if __name__ == "__main__":
    sys.exit(main())
