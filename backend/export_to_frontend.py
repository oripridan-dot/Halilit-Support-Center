
#!/usr/bin/env python3
"""
ADK Data Exporter v5.1
Transforms backend golden data → frontend-ready format

This script bridges the gap between:
- Backend: Structured validation data (5_golden/)
- Frontend: Flat optimized UI data (public/data/)
"""

# Paths
BACKEND_GOLDEN = Path(__file__).parent / "data" / "5_golden"
FRONTEND_DATA = Path(__file__).parent.parent / "frontend" / "public" / "data"

def transform_product(golden_record: Dict[str, Any], brand_id: str) -> Optional[Dict[str, Any]]:
                """
                Transform nested golden record → flat frontend format

                Input (Golden):
                {
                        "uuid": "...",
                        "commercial": { "id": "...", "title": "...", "price_il": ..., "price_eilat": ... },
                        "official": { "official_name": "...", "description": "...", "image_url": "..." },
                        "contextual": { "pros": [...], "cons": [...] },
                        "confidence_score": 100
                }

                Output (Frontend):
                {
                        "id": "...",
                        "sku": "...",
                        "brand_id": "...",
                        "name": "...",
                        "slug": "...",
                        "description_short": "...",
                        "description_full": "...",
                        "price": ...,
                        "currency": "ILS",
                        "in_stock": true,
                        "image_hero": { "url": "...", "alt": "..." },
                        "specs": {},
                        "reviews": { "average": 4.5, "count": 0 }
                }
                """
                commercial = golden_record.get("commercial") or {}
                official = golden_record.get("official") or {}
                contextual = golden_record.get("contextual") or {}

                # Skip if no commercial data at all
                if not commercial:
                                return None

                # Product ID & SKU
                product_id = commercial.get("id", golden_record.get("uuid", "unknown"))
                sku = commercial.get("sku", product_id)

                # Name (prefer official, fallback to commercial)
                name = official.get("official_name") or commercial.get(
                                "title", "Unknown Product")

                # Slug (URL-friendly)
                slug = name.lower().replace(" ", "-").replace("&", "and")
                slug = "".join(c for c in slug if c.isalnum() or c == "-")

                # Description
                description_full = official.get(
                                "description") or commercial.get("description", "")
                description_short = description_full[:150] + \
                                "..." if len(description_full) > 150 else description_full

                # Price (use Israel price)
                price = commercial.get("price_il", 0.0)

                # Stock
                in_stock = commercial.get("in_stock", False)

                # Images
                hero_url = official.get("image_url") or commercial.get("image_url", "")
                image_hero = {
                                "url": hero_url,
                                "alt": name
                }

                # Gallery
                gallery = official.get("gallery", [])
                if commercial.get("image_url") and commercial["image_url"] not in gallery:
                                gallery.insert(0, commercial["image_url"])

                # Specs (empty for now, can be enhanced)
                specs = commercial.get("specs", {})

                # Reviews (from contextual data)
                pros = contextual.get("pros", [])
                cons = contextual.get("cons", [])
                confidence = contextual.get("confidence_score", 0)

                # Calculate review score based on confidence and pros/cons balance
                review_avg = 4.0 if confidence > 80 else 3.5
                if len(pros) > len(cons):
                                review_avg += 0.5
                elif len(cons) > len(pros):
                                review_avg -= 0.5
                review_avg = min(5.0, max(1.0, review_avg))

                return {
                                "id": product_id,
                                "sku": sku,
                                "brand_id": brand_id,
                                "name": name,
                                "slug": slug,
                                "description_short": description_short,
                                "description_full": description_full,
                                "price": price,
                                "currency": "ILS",
                                "in_stock": in_stock,
                                "image_hero": image_hero,
                                "image_gallery": gallery[:5],  # Limit to 5 images
                                "specs": specs,
                                "reviews": {
                                                "average": round(review_avg, 2),
                                                "count": len(contextual.get("verified_sources", []))
                                },
                                "contextual": {
                                                "pros": pros[:3],  # Top 3 pros
                                                "cons": cons[:3],  # Top 3 cons
                                                "expert_tips": contextual.get("expert_tips", [])[:2]
                                }
                }

def export_brand(brand_id: str) -> Optional[Dict[str, Any]]:
                """Export a single brand from golden → frontend format"""
                golden_file = BACKEND_GOLDEN / f"{brand_id}.json"

                if not golden_file.exists():
                                print(f"⚠️  {brand_id}: No golden data found")
                                return None

                # Read golden data
                with open(golden_file, "r", encoding="utf-8") as f:
                                golden_data = json.load(f)

                if not golden_data:
                                print(f"⚠️  {brand_id}: Empty golden file")
                                return None

                # Handle different data structures
                products_list = []

                if isinstance(golden_data, dict):
                                # Format 1: {"brand": "...", "products": [...]}
                                products_list = golden_data.get("products", [])
                elif isinstance(golden_data, list):
                                # Format 2: [...] direct array
                                products_list = golden_data
                else:
                                print(f"❌ {brand_id}: Unknown data format")
                                return None

                # Check if products are already flat/optimized or need transformation
                products = []
                for record in products_list:
                                if not record or not isinstance(record, dict):
                                                continue

                                try:
                                                # Check if already flat (has 'slug' or 'render_hints')
                                                if 'slug' in record or 'render_hints' in record or 'search_text' in record:
                                                                # Already optimized format, use as-is
                                                                products.append(record)
                                                elif 'commercial' in record or 'official' in record:
                                                                # Nested format, needs transformation
                                                                transformed = transform_product(record, brand_id)
                                                                if transformed:  # Only add if transformation succeeded
                                                                                products.append(transformed)
                                                else:
                                                                # Unknown format, skip
                                                                print(f"⚠️  {brand_id}: Skipping product with unknown format")
                                                                continue
                                except Exception as e:
                                                print(f"❌ {brand_id}: Failed to process product - {e}")
                                                continue

                if not products:
                                print(f"⚠️  {brand_id}: No valid products after processing")
                                return None

                # Write to frontend
                frontend_file = FRONTEND_DATA / f"{brand_id}.json"
                with open(frontend_file, "w", encoding="utf-8") as f:
                                json.dump(products, f, indent=2, ensure_ascii=False)

                print(f"✅ {brand_id}: Exported {len(products)} products")

                return {
                                "id": brand_id,
                                "name": brand_id.replace("-", " ").title(),
                                "product_count": len(products),
                                "data_file": f"{brand_id}.json"
                }

def generate_index(brands: List[Dict[str, Any]]):
                """Generate master index.json"""
                index = {
                                "version": "5.1.0",
                                "build_timestamp": datetime.now().isoformat(),
                                "total_products": sum(b["product_count"] for b in brands),
                                "brands": brands
                }

                index_file = FRONTEND_DATA / "index.json"
                with open(index_file, "w", encoding="utf-8") as f:
                                json.dump(index, f, indent=2)

                print(f"✅ Generated index.json with {len(brands)} brands")

def generate_search_index(brands: List[Dict[str, Any]]):
                """Generate search_index.json for instant search"""
                search_items = []

                for brand_info in brands:
                                brand_file = FRONTEND_DATA / brand_info["data_file"]
                                if not brand_file.exists():
                                                continue

                                with open(brand_file, "r", encoding="utf-8") as f:
                                                products = json.load(f)

                                for product in products:
                                                # Get image safely
                                                image_hero = product.get("image_hero")
                                                if isinstance(image_hero, dict):
                                                                image_url = image_hero.get("url", "")
                                                elif isinstance(image_hero, str):
                                                                image_url = image_hero
                                                else:
                                                                image_url = product.get("image_thumbnail") or ""

                                                search_items.append({
                                                                "id": product.get("id", ""),
                                                                "name": product.get("name", "Unknown"),
                                                                "brand": brand_info["name"],
                                                                "brand_id": brand_info["id"],
                                                                "price": product.get("price", 0),
                                                                "slug": product.get("slug", ""),
                                                                "image": image_url,
                                                                "in_stock": product.get("in_stock") or product.get("stock_status") == "in_stock"
                                                })

                search_file = FRONTEND_DATA / "search_index.json"
                with open(search_file, "w", encoding="utf-8") as f:
                                json.dump(search_items, f, indent=2)

                print(f"✅ Generated search_index.json with {len(search_items)} items")

def main():
                """Main export pipeline"""
                print("=" * 60)
                print("ADK Data Exporter v5.1")
                print("Transforming golden data → frontend format")
                print("=" * 60)
                print()

                # Ensure frontend data directory exists
                FRONTEND_DATA.mkdir(parents=True, exist_ok=True)

                # Find all golden data files
                golden_files = list(BACKEND_GOLDEN.glob("*.json"))

                if not golden_files:
                                print("❌ No golden data files found!")
                                return

                print(f"Found {len(golden_files)} golden data files")
                print()

                # Export each brand
                exported_brands = []
                for golden_file in sorted(golden_files):
                                brand_id = golden_file.stem
                                brand_info = export_brand(brand_id)
                                if brand_info:
                                                exported_brands.append(brand_info)

                print()
                print("-" * 60)

                if not exported_brands:
                                print("❌ No brands exported successfully!")
                                return

                # Generate index files
                generate_index(exported_brands)
                generate_search_index(exported_brands)

                print()
                print("=" * 60)
                print(f"✅ Export complete!")
                print(f"   Brands: {len(exported_brands)}")
                print(f"   Products: {sum(b['product_count'] for b in exported_brands)}")
                print(f"   Output: {FRONTEND_DATA}")
                print("=" * 60)

if __name__ == "__main__":
                main()
