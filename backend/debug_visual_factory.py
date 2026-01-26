import sys
from pathlib import Path
# Add current directory to path so we can import services
import os
sys.path.append(os.getcwd())

from services.visual_factory import VisualFactory

def debug():
    vf = VisualFactory()
    url = "https://d3m9l0v76dty0.cloudfront.net/system/photos/15563323/original/7ee8fb310bd84180da208a727ea524ee.jpg"
    out_dir = Path("debug_output")
    out_dir.mkdir(exist_ok=True)
    out_base = str(out_dir / "test_roland")
    
    print(f"Testing URL: {url}")
    print(f"Output Base: {out_base}")
    
    try:
        result = vf.process_product_asset(url, out_base, force_reprocess=True)
        print("Result:", result)
        if result:
            print("Success! Created:")
            print(f"Thumb: {result['thumbnail_url']}")
            print(f"Inspect: {result['inspection_url']}")
    except Exception as e:
        print(f"Caught exception in main: {e}")

if __name__ == "__main__":
    debug()
