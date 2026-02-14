import json
import sys
import subprocess
from pathlib import Path

# Add backend to sys.path
script_dir = Path(__file__).resolve().parent
backend_dir = script_dir.parent
sys.path.append(str(backend_dir))


def generate():
    try:
        from ingestion.data_models import IngestionProductDraft
    except ImportError as e:
        print(f"❌ Failed to import backend models: {e}")
        sys.exit(1)

    output_path = backend_dir.parent / 'frontend/src/types/generated.ts'
    schema_path = backend_dir / 'schema_dump.json'

    print("🔄 Generating JSON Schema from Pydantic models (V2)...")

    # Generate JSON Schema standard
    schema = IngestionProductDraft.model_json_schema()

    # Write temporary schema file
    with open(schema_path, 'w') as f:
        json.dump(schema, f, indent=2)

    print(f"   Schema dump: {schema_path}")
    print("🔄 Converting JSON Schema to TypeScript...")

    try:
        # Run npx json2ts from frontend dir
        frontend_dir = backend_dir.parent / 'frontend'
        cmd = [
            "npx", "json2ts",
            "-i", str(schema_path),
            "-o", str(output_path),
            "--style.singleQuote"
        ]
        subprocess.run(cmd, cwd=str(frontend_dir), check=True)
        print(f"✅ Frontend definitions updated at: {output_path}")
    except subprocess.CalledProcessError as e:
        print(f"❌ json2ts failed: {e}")
        sys.exit(1)
    finally:
        # cleanup
        if schema_path.exists():
            schema_path.unlink()


if __name__ == "__main__":
    generate()
