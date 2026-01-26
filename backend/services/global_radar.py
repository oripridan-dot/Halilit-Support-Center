"""
GlobalRadar: Lightweight Reconnaissance Unit

Visits brand "All Products" pages to map the entire theoretical scope
without downloading heavy assets or detailed content. Builds a Strategic
Manifest of what exists globally.

Usage:
    radar = GlobalRadar()
    manifest = radar.compile_manifest()
"""

import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import json
import os
from typing import List, Dict, Any
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class GlobalRadar:
    """
    Lightweight reconnaissance unit.
    Visits Brand 'All Products' pages to map the entire theoretical scope.
    Does NOT visit individual product pages. Fast execution.
    """

    def __init__(self):
        self.session = requests.Session()
        self.headers = {
            'User-Agent': 'HSC-Radar/1.0 (reconnaissance mission)'
        }
        self.radar_dir = "data/radar"
        self.manifest_dir = "data/strategic_manifests"
        os.makedirs(self.radar_dir, exist_ok=True)
        os.makedirs(self.manifest_dir, exist_ok=True)

    def save_radar_data(self, brand: str, data: List[Dict[str, Any]]):
        """Saves lightweight radar data to JSON"""
        filename = f"{brand.lower()}_global.json"
        path = os.path.join(self.radar_dir, filename)
        
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
        print(f"📡 [RADAR] Global scope saved to {path} ({len(data)} items)")


    def scan_roland_global(self) -> List[Dict[str, Any]]:
        """
        Scans Roland's product categories to map global synthesizer scope.
        Does NOT visit individual product pages. Fast execution.

        Returns:
            List of discovered product nodes with metadata
        """
        print("📡 Scanning Global Sector: ROLAND...")

        discovered_nodes = []
        base_categories = [
            "https://www.roland.com/global/categories/synthesizers/",
            "https://www.roland.com/global/categories/drums/",
            "https://www.roland.com/global/categories/keyboards/",
        ]

        for category_url in base_categories:
            try:
                response = self.session.get(
                    category_url,
                    headers=self.headers,
                    timeout=10
                )
                response.raise_for_status()

                soup = BeautifulSoup(response.text, 'html.parser')

                # Extract category hint from URL
                category_hint = category_url.split('/categories/')[-1].rstrip('/')

                # Roland uses various selectors for product items
                # This is a generic approach - in production, inspect the actual DOM
                products = soup.select('[class*="product"]')

                if not products:
                    logger.info(f"No products found on {category_url}, trying alternative selector...")
                    products = soup.select('a[href*="/products/"]')

                for p in products[:50]:  # Limit to prevent infinite loops
                    try:
                        # Extract product link
                        link = p.get('href') if p.name == 'a' else p.find('a', href=True)
                        if not link:
                            continue

                        # Extract product name
                        name_elem = p.find(['h2', 'h3', 'span', 'div'], class_=['name', 'title', 'product-name'])
                        if not name_elem:
                            name_text = link if isinstance(link, str) else link.text.strip()
                        else:
                            name_text = name_elem.get_text(strip=True)

                        if not name_text: continue

                        # Create Radar Record
                        discovered_nodes.append({
                            "brand": "Roland",
                            "model": name_text,
                            "category": category_hint,
                            "url": urljoin(category_url, link if isinstance(link, str) else link.get('href')),
                            "status": "GLOBAL_DISCOVERY"
                        })
                    except Exception as e:
                        logger.debug(f"Parsing error: {e}")

            except Exception as e:
                logger.error(f"Failed to scan {category_url}: {e}")

        # Save to Radar
        self.save_radar_data("roland", discovered_nodes)
        return discovered_nodes

    def scan_brand(self, brand_name: str, brand_url: str):
        """Generic scanner interface"""
        if brand_name.lower() == "roland":
            return self.scan_roland_global()
        else:
            print(f"📡 Radar not calibrated for {brand_name} yet.")
            return []

    def scan_nord_global(self) -> List[Dict[str, Any]]:
        """
        Scans Nord instruments catalog.
        """
        print("📡 Scanning Global Sector: NORD...")
        discovered_nodes = []

        base_url = "https://www.nordkeyboards.com/products"

        try:
            response = self.session.get(base_url, headers=self.headers, timeout=10)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, 'html.parser')

            # Nord's product structure (adjust selectors based on actual HTML)
            products = soup.select('[class*="product-card"], a[href*="/en/products/"]')

            for p in products[:50]:
                try:
                    link = p.get('href') if p.name == 'a' else p.find('a', href=True)
                    if not link:
                        continue

                    name_elem = p.find(['h2', 'h3', 'span'], class_=['name', 'title'])
                    if not name_elem:
                        name_elem = p.find(['h2', 'h3'])
                    name = name_elem.text.strip() if name_elem else "Unknown"

                    if not name or name == "Unknown":
                        continue

                    tier = "Standard"
                    if any(x in name.upper() for x in ["LEAD", "STAGE", "MODULAR"]):
                        tier = "Flagship"

                    discovered_nodes.append({
                        "name": name,
                        "brand": "nord",
                        "global_url": urljoin(base_url, link),
                        "detected_tier": tier,
                        "category_hint": "keyboards",
                        "source_domain": "nordkeyboards.com",
                        "status": "DISCOVERED"
                    })

                except Exception as e:
                    logger.debug(f"Error parsing Nord product: {e}")
                    continue

        except requests.RequestException as e:
            logger.error(f"❌ Radar Jammed on Nord: {e}")

        return discovered_nodes

    def scan_boss_global(self) -> List[Dict[str, Any]]:
        """
        Scans Boss instruments and effects.
        """
        print("📡 Scanning Global Sector: BOSS...")
        discovered_nodes = []

        base_url = "https://www.boss.info/global/products/"

        try:
            response = self.session.get(base_url, headers=self.headers, timeout=10)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, 'html.parser')

            products = soup.select('[class*="product"], a[href*="/products/"]')

            for p in products[:50]:
                try:
                    link = p.get('href') if p.name == 'a' else p.find('a', href=True)
                    if not link:
                        continue

                    name_elem = p.find(['h2', 'h3', 'span'])
                    name = name_elem.text.strip() if name_elem else "Unknown"

                    if not name or name == "Unknown":
                        continue

                    tier = "Standard"
                    if any(x in name.upper() for x in ["GT-1000", "Katana", "ME-50"]):
                        tier = "Professional"

                    discovered_nodes.append({
                        "name": name,
                        "brand": "boss",
                        "global_url": urljoin(base_url, link),
                        "detected_tier": tier,
                        "category_hint": "guitars",
                        "source_domain": "boss.info",
                        "status": "DISCOVERED"
                    })

                except Exception as e:
                    logger.debug(f"Error parsing Boss product: {e}")
                    continue

        except requests.RequestException as e:
            logger.error(f"❌ Radar Jammed on Boss: {e}")

        return discovered_nodes

    def scan_moog_global(self) -> List[Dict[str, Any]]:
        """
        Scans Moog Music synthesizers.
        """
        print("📡 Scanning Global Sector: MOOG...")
        discovered_nodes = []

        base_url = "https://www.moogmusic.com/products"

        try:
            response = self.session.get(base_url, headers=self.headers, timeout=10)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, 'html.parser')

            products = soup.select('[class*="product"], a[href*="/products/"]')

            for p in products[:50]:
                try:
                    link = p.get('href') if p.name == 'a' else p.find('a', href=True)
                    if not link:
                        continue

                    name_elem = p.find(['h2', 'h3', 'span'])
                    name = name_elem.text.strip() if name_elem else "Unknown"

                    if not name or name == "Unknown":
                        continue

                    tier = "Flagship"  # Moog products are generally flagship-tier

                    discovered_nodes.append({
                        "name": name,
                        "brand": "moog",
                        "global_url": urljoin(base_url, link),
                        "detected_tier": tier,
                        "category_hint": "synthesizers",
                        "source_domain": "moogmusic.com",
                        "status": "DISCOVERED"
                    })

                except Exception as e:
                    logger.debug(f"Error parsing Moog product: {e}")
                    continue

        except requests.RequestException as e:
            logger.error(f"❌ Radar Jammed on Moog: {e}")

        return discovered_nodes

    def compile_manifest(self) -> Dict[str, Any]:
        """
        Aggregates all radar scans into a Strategic Manifest.
        Saves to backend/data/strategic_manifests/strategic_manifest.json
        Now also saves individual radar files for Gap Analysis.
        """
        print("\n🎯 COMPILING STRATEGIC MANIFEST...\n")

        # Scan individually to save radar files
        roland_data = self.scan_roland_global()
        self.save_radar_data("roland", roland_data)
        
        nord_data = self.scan_nord_global()
        self.save_radar_data("nord", nord_data)
        
        boss_data = self.scan_boss_global()
        self.save_radar_data("boss", boss_data)
        
        moog_data = self.scan_moog_global()
        self.save_radar_data("moog", moog_data)

        universe = {
            "roland": roland_data,
            "nord": nord_data,
            "boss": boss_data,
            "moog": moog_data,
        }

        # Calculate statistics
        total_discovered = sum(len(items) for items in universe.values())
        brand_stats = {
            brand: {
                "total_discovered": len(items),
                "by_tier": {
                    tier: len([x for x in items if x['detected_tier'] == tier])
                    for tier in ["Entry", "Standard", "Professional", "Flagship"]
                }
            }
            for brand, items in universe.items()
        }

        manifest_data = {
            "timestamp": str(__import__('datetime').datetime.now()),
            "total_products_discovered": total_discovered,
            "brands_scanned": list(universe.keys()),
            "brand_statistics": brand_stats,
            "products_by_brand": universe
        }

        # Save the manifest
        manifest_path = os.path.join(self.manifest_dir, "strategic_manifest.json")
        with open(manifest_path, "w") as f:
            json.dump(manifest_data, f, indent=2)

        print(f"\n✅ MANIFEST SAVED TO: {manifest_path}")
        print(f"📊 TOTAL PRODUCTS DISCOVERED: {total_discovered}")
        print(f"\n📈 BREAKDOWN BY BRAND:")
        for brand, stats in brand_stats.items():
            print(f"  {brand.upper()}: {stats['total_discovered']} products")
            for tier, count in stats['by_tier'].items():
                if count > 0:
                    print(f"    - {tier}: {count}")

        return manifest_data

    def get_manifest_summary(self) -> Dict[str, Any]:
        """
        Returns summary statistics of the Strategic Manifest.
        """
        manifest_path = os.path.join(self.manifest_dir, "strategic_manifest.json")

        if not os.path.exists(manifest_path):
            return {"error": "No manifest found. Run compile_manifest() first."}

        with open(manifest_path, "r") as f:
            manifest = json.load(f)

        return {
            "timestamp": manifest.get("timestamp"),
            "total_products_discovered": manifest.get("total_products_discovered"),
            "brands_scanned": manifest.get("brands_scanned"),
            "brand_statistics": manifest.get("brand_statistics")
        }


if __name__ == "__main__":
    radar = GlobalRadar()
    manifest = radar.compile_manifest()
    print("\n✨ Reconnaissance Complete. Universe Mapped.\n")
