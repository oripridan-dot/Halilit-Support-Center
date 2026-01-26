import requests
from bs4 import BeautifulSoup
import re
import os

class HalilitBrandRegistry:
    """
    THE BIBLE: https://www.halilit.com/pages/4367
    This service defines the scope of the entire application.
    """
    BIBLE_URL = "https://www.halilit.com/pages/4367"
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers = {'User-Agent': 'HSC-Master-Registry/1.0'}

    def fetch_official_roster(self):
        print(f"📜 Reading the Bible ({self.BIBLE_URL})...")
        try:
            res = self.session.get(self.BIBLE_URL)
            if res.status_code != 200:
                print(f"❌ Failed to read registry: {res.status_code}")
                return []

            soup = BeautifulSoup(res.text, 'html.parser')
            
            # Selector found via inspection: .brands a (inside <div class="brands">)
            brand_elements = soup.select('.brands a')
            
            if not brand_elements:
                print("⚠️  Warning: Primary selector '.brands a' failed. Trying fallbacks...")
                # Fallback to general link search if class not found
                brand_elements = soup.select('a[href*="/g/"]')

            roster = []
            seen_slugs = set()
            
            for el in brand_elements:
                href = el.get('href', '')
                if not href or '/g/' not in href:
                    continue
                
                # Extract Name
                img = el.select_one('img')
                # If alt exists, use it.
                name = ""
                if img and img.get('alt'):
                    name = img['alt'].strip()
                
                # Parse URL for slug and fallback name
                # href example: https://www.halilit.com/g/5193-Brand/207910-ADAM-Audio
                parts = href.split('/')
                last_part = parts[-1] # 207910-ADAM-Audio
                
                # Regex to clean leading numbers ID (e.g. 207910-)
                clean_slug_match = re.search(r'^\d+-(.+)$', last_part)
                if clean_slug_match:
                    slug_candidate = clean_slug_match.group(1)
                else:
                    slug_candidate = last_part
                
                slug = slug_candidate.lower() # adam-audio
                
                # Avoid duplicates (sometimes there are multiple links per brand)
                if slug in seen_slugs:
                    continue
                seen_slugs.add(slug)

                if not name:
                    # Fallback name from slug, capitalizing and replacing dashes
                    name = slug_candidate.replace('-', ' ')
                
                # Logo URL
                logo_url = img['src'] if img else None
                if logo_url and not logo_url.startswith('http'):
                    logo_url = f"https://www.halilit.com{logo_url}"

                # Handle URL normalization
                if href.startswith('http'):
                    full_url = href
                else:
                    # Remove leading dots or slashes
                    clean_path = href.lstrip('./')
                    full_url = f"https://www.halilit.com/{clean_path}"

                roster.append({
                    "name": name,
                    "slug": slug,
                    "halilit_url": full_url,
                    "logo_url": logo_url
                })
                
            print(f"✅ Authenticated {len(roster)} Partners.")
            return roster

        except Exception as e:
            print(f"❌ Registry Protocol Failed: {e}")
            return []

    def sync_logos(self, roster):
        """Ensures we have a local logo for every partner"""
        # Determine correct path relative to execution
        base_dir = os.getcwd()
        # If running from backend folder
        if base_dir.endswith('backend'):
             save_dir = "../frontend/public/assets/logos"
        # If running from root
        else:
             save_dir = "frontend/public/assets/logos"
            
        os.makedirs(save_dir, exist_ok=True)
        
        for brand in roster:
            if not brand['logo_url']: continue
            
            # Simple sanitization
            safe_name = brand['slug'].replace(' ', '-')
            # Handle query params in logo url if any
            clean_url = brand['logo_url'].split('?')[0]
            ext = clean_url.split('.')[-1] or 'png'
            # Default to png if ext is weird or too long
            if len(ext) > 4: 
                ext = 'png'
            
            local_path = os.path.join(save_dir, f"{safe_name}_logo.{ext}")
            
            if not os.path.exists(local_path):
                print(f"  ⬇️  Ingesting Logo: {brand['name']}")
                try:
                    # Use session to ensure headers/User-Agent are sent
                    response = self.session.get(brand['logo_url'], timeout=10)
                    if response.status_code == 200:
                        with open(local_path, 'wb') as f:
                            f.write(response.content)
                    else:
                         print(f"     ⚪ Logo skipped (Status {response.status_code})")
                except Exception as e:
                    # Log as info/debug rather than warning if it's just a connection blip
                    print(f"     ⚪ Logo skipped for {brand['name']}")

if __name__ == "__main__":
    reg = HalilitBrandRegistry()
    roster = reg.fetch_official_roster()
    reg.sync_logos(roster)
