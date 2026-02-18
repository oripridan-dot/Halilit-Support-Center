#!/usr/bin/env python3
"""Simple test to check OpenClaw connection and API format."""
import os
import sys
import json
from pathlib import Path

# Load .env
env_file = Path(__file__).parent / ".env"
if env_file.exists():
    for line in env_file.read_text().splitlines():
        if "=" in line and not line.strip().startswith("#"):
            key, val = line.split("=", 1)
            os.environ[key.strip()] = val.strip()

OPENCLAW_URL = os.getenv("OPENCLAW_URL", "").rstrip("/")
OPENCLAW_EXECUTE_PATH = os.getenv("OPENCLAW_EXECUTE_PATH", "/api/execute")
OPENCLAW_KEY = os.getenv("OPENCLAW_KEY", "")

print(f"OPENCLAW_URL: {OPENCLAW_URL}")
print(f"OPENCLAW_EXECUTE_PATH: {OPENCLAW_EXECUTE_PATH}")
print(f"OPENCLAW_KEY: {'***' if OPENCLAW_KEY else '(empty)'}")
print()

url = f"{OPENCLAW_URL}{OPENCLAW_EXECUTE_PATH}"
print(f"Testing URL: {url}")
print()

try:
    import httpx
    
    payload = {
        "skill": "organize_brand_catalog",
        "params": {
            "brand_slug": "test",
            "brand_name": "Test Brand",
            "products": [
                {
                    "halilit_id": "test-1",
                    "product_name": "Test Product",
                    "taxonomy": {"canonical_category": "Test Category"}
                }
            ]
        }
    }
    
    headers = {}
    if OPENCLAW_KEY:
        headers["Authorization"] = f"Bearer {OPENCLAW_KEY}"
        headers["X-API-Key"] = OPENCLAW_KEY
    
    print("Sending request...")
    print(f"Payload: {json.dumps(payload, indent=2)}")
    print()
    
    # Try with retries and longer timeout
    max_retries = 3
    for attempt in range(max_retries):
        try:
            print(f"Attempt {attempt + 1}/{max_retries}...")
            with httpx.Client(timeout=30.0) as client:
                resp = client.post(url, json=payload, headers=headers or None)
                print(f"Status: {resp.status_code}")
                print(f"Response: {resp.text[:500]}")
                
                if resp.status_code == 200:
                    print("\n✅ SUCCESS! OpenClaw is responding.")
                    data = resp.json()
                    print(f"Result keys: {list(data.keys())}")
                    sys.exit(0)
                else:
                    print(f"\n❌ FAILED: HTTP {resp.status_code}")
                    if attempt < max_retries - 1:
                        print("Retrying in 3 seconds...")
                        import time
                        time.sleep(3)
                    else:
                        sys.exit(1)
        except httpx.ReadError as e:
            if "Connection reset" in str(e) or "54" in str(e):
                print(f"⚠️  Connection reset (container might be starting or crashing)")
                if attempt < max_retries - 1:
                    print("Waiting 5 seconds and retrying...")
                    import time
                    time.sleep(5)
                else:
                    print("\n❌ Connection keeps resetting. Container might be crashing.")
                    print("   Check: docker logs halilit-field-agent")
                    sys.exit(1)
            else:
                raise
            
except httpx.ConnectError as e:
    print(f"❌ CONNECTION ERROR: {e}")
    print("\nPossible issues:")
    print("  1. Docker container not running: docker ps | grep halilit-field-agent")
    print("  2. Wrong port: check PORT_OPENCLAW in .env")
    print("  3. Container crashed: docker logs halilit-field-agent")
except Exception as e:
    print(f"❌ ERROR: {e}")
    import traceback
    traceback.print_exc()
