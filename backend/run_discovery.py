# backend/run_discovery.py
from services.gap_analyzer import GapAnalyzer
from services.global_radar import GlobalRadar
import sys
import os

# Add backend to path for imports to work if running as script from backend/
# sys.path.append(os.path.dirname(os.path.abspath(__file__)))


def main():
    print("🔭 Starting Global Discovery Mission...")
    
    # 1. Run Global Radar (Light Scan)
    radar = GlobalRadar()
    
    # Trigger Roland scan
    radar.scan_brand("Roland", "")
    
    # Trigger Generic placeholder for others
    # radar.scan_brand("Nord", "") 
    
    # 2. Run Gap Analysis
    print("\n🧠 Running Gap Analysis...")
    analyzer = GapAnalyzer()
    
    brands = ["roland"] # Add others as we implement their radars
    
    for brand in brands:
        analyzer.run_analysis(brand)

if __name__ == "__main__":
    main()
