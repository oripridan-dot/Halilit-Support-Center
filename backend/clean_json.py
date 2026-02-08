import json
import glob
import os
from pathlib import Path

# Adjust path to be relative to the workspace root or handles '../'
DATA_DIR = Path("../frontend/public/data")


def clean_file(filepath):
    print(f"Cleaning {filepath}...")
    try:
        with open(filepath, 'r') as f:
            data = json.load(f)

        products = []
        is_dict_wrapper = False

        if isinstance(data, list):
            products = data
        elif isinstance(data, dict) and "products" in data:
            products = data["products"]
            is_dict_wrapper = True
        else:
            print(f"Skipping {filepath}: No product list found.")
            return

        cleaned_products = []
        for p in products:
            # Remove raw_snapshot to save space/recursion
            if "raw_snapshot" in p:
                del p["raw_snapshot"]

            # Also clean valid_snapshot if it exists and is huge
            if "valid_snapshot" in p:
                del p["valid_snapshot"]

            cleaned_products.append(p)

        # Write back
        if is_dict_wrapper:
            data["products"] = cleaned_products
        else:
            data = cleaned_products

        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)

        print(f"Cleaned {filepath}. Size: {os.path.getsize(filepath)} bytes")

    except Exception as e:
        print(f"Error cleaning {filepath}: {e}")


if not DATA_DIR.exists():
    print(f"Error: {DATA_DIR.resolve()} does not exist!")
else:
    files = list(DATA_DIR.glob("*.json"))
    print(f"Found {len(files)} files in {DATA_DIR}")
    for f in files:
        if "index" not in f.name and "search" not in f.name:
            clean_file(f)
