"""
OfficialBrandBase - Abstract Base Class for Brand-Specific Scrapers

This base class defines the contract that ALL official brand scrapers must implement.
It ensures consistent extraction of knowledge & media from official brand websites.

Usage Pattern:
1. Create a new scraper: class RolandScraper(OfficialBrandBase)
2. Implement: extract_manuals(), extract_official_gallery(), extract_specs()
3. Return OfficialMedia objects with proper source_domain attribution
4. Feed into MassIngestProtocol
"""

import os
import sys
from abc import ABC, abstractmethod
from typing import Dict, List, Optional
from datetime import datetime

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.unified_ingestor import OfficialMedia


class OfficialBrandBase(ABC):
    """
    Abstract base class for official brand scrapers.
    
    All brand scrapers (Roland, Moog, Nord, Boss, etc.) must inherit from this
    and implement the three core methods:
    - extract_manuals(model_name: str) → List[OfficialMedia]
    - extract_official_gallery(model_name: str) → List[str]
    - extract_specs(model_name: str) → Dict
    
    Attributes:
        brand_name: Human-readable brand name (e.g., "Roland")
        brand_domain: Official brand domain (e.g., "roland.com")
        base_url: Root URL for the brand website
    """
    
    def __init__(self, brand_name: str, brand_domain: str, base_url: str = ""):
        """
        Initialize the brand scraper.
        
        Args:
            brand_name: Official brand name (e.g., "Roland")
            brand_domain: Official brand domain (e.g., "roland.com")
            base_url: Base URL for the brand website (optional)
        """
        self.brand_name = brand_name
        self.brand_domain = brand_domain
        self.base_url = base_url or f"https://{brand_domain}"
        self.session = self._setup_session()
        
    def validate_domain(self, url: str) -> bool:
        """
        [Church and State Rule #1] Domain Whitelist
        Ensures the URL belongs to the official brand domain.
        """
        from urllib.parse import urlparse
        if not url: return False
        try:
            domain = urlparse(url).netloc
            # Allow exact match or subdomain
            is_valid = domain == self.brand_domain or domain.endswith("." + self.brand_domain)
            return is_valid
        except:
            return False

    def verify_pdf(self, url: str) -> bool:
        """
        [Church and State Rule #4] Checksum Verification
        Verifies the URL points to a valid PDF via HEAD request.
        """
        if not url: return False
        try:
             # Use a short timeout for HEAD requests to avoid hanging
             if not self.session: return False
             r = self.session.head(url, allow_redirects=True, timeout=5)
             content_type = r.headers.get('Content-Type', '').lower()
             is_pdf = 'application/pdf' in content_type and r.status_code == 200
             if not is_pdf:
                 print(f"   ⚠️ Invalid PDF Header: {url} ({content_type})")
             return is_pdf
        except Exception as e:
             # print(f"   ⚠️ PDF Check Failed: {e}")
             return False

    def safe_get(self, url: str):
        """
        Wrapper for session.get with Domain Whitelist enforcement.
        """
        if not self.validate_domain(url):
            print(f"   ⛔ BLOCKED: Domain of {url} not in whitelist for {self.brand_name}")
            return None
        return self.session.get(url, timeout=10)
    
    @staticmethod
    def _setup_session():
        """
        Setup a requests session with proper headers.
        Subclasses can override for custom session configuration.
        """
        try:
            import requests
            session = requests.Session()
            session.headers.update({
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            })
            return session
        except ImportError:
            return None
    
    def scrape_product(self, model_name: str, sku: str = "") -> Dict:
        """
        Main entry point for scraping a single product.
        
        This is the method called by MassIngestProtocol.
        
        Args:
            model_name: Product model name (e.g., "FANTOM-06")
            sku: Product SKU (optional, for disambiguation)
            
        Returns:
            Dict with keys: 'manuals', 'gallery', 'specs'
            {
                'manuals': [OfficialMedia, ...],
                'gallery': ['url1', 'url2', ...],
                'specs': {'key': 'value', ...}
            }
        """
        print(f"   🔍 Scraping {self.brand_name}: {model_name}")
        
        try:
            manuals = self.extract_manuals(model_name, sku)
            gallery = self.extract_official_gallery(model_name, sku)
            specs = self.extract_specs(model_name, sku)
            
            return {
                'manuals': manuals,
                'gallery': gallery,
                'specs': specs
            }
        except Exception as e:
            print(f"      ⚠️  Failed to scrape: {str(e)}")
            return {
                'manuals': [],
                'gallery': [],
                'specs': {}
            }
    
    @abstractmethod
    def extract_manuals(self, model_name: str, sku: str = "") -> List[OfficialMedia]:
        """
        Extract all available PDF manuals/documentation for a product.
        
        MUST return OfficialMedia objects with:
        - url: Direct link to PDF (NO proxy, NO re-hosting)
        - type: 'pdf'
        - label: Human-readable name (e.g., "Operating Manual", "Quick Start")
        - source_domain: self.brand_domain
        
        Args:
            model_name: Product model (e.g., "FANTOM-06")
            sku: Product SKU (optional)
            
        Returns:
            List of OfficialMedia objects (can be empty if no manuals found)
        """
        pass
    
    @abstractmethod
    def extract_official_gallery(self, model_name: str, sku: str = "") -> List[str]:
        """
        Extract high-resolution product images from the official brand website.
        
        MUST return direct URLs to images hosted on the official brand domain.
        DO NOT download and re-host.
        
        Args:
            model_name: Product model (e.g., "FANTOM-06")
            sku: Product SKU (optional)
            
        Returns:
            List of image URLs (can be empty if no images found)
        """
        pass
    
    @abstractmethod
    def extract_specs(self, model_name: str, sku: str = "") -> Dict:
        """
        Extract technical specifications from official product pages.
        
        MUST return a Dict with key-value pairs extracted from official specs.
        Examples:
        {
            'polyphony': '128 voices',
            'sounds': '1000+',
            'keyboard': '76-key weighted',
            'audio_outputs': 'Stereo Out + Subwoofer'
        }
        
        Args:
            model_name: Product model (e.g., "FANTOM-06")
            sku: Product SKU (optional)
            
        Returns:
            Dict of specifications (can be empty if scraping fails)
        """
        pass
    
    def _create_official_media(self, url: str, media_type: str, label: str) -> OfficialMedia:
        """
        Helper method to create OfficialMedia objects with consistent attribution.
        
        Args:
            url: Direct URL to the asset
            media_type: 'pdf', 'image', 'video', 'specification'
            label: Human-readable label
            
        Returns:
            OfficialMedia object with source_domain automatically set
        """
        return OfficialMedia(
            url=url,
            type=media_type,
            label=label,
            source_domain=self.brand_domain,
            extracted_at=datetime.now().isoformat()
        )
    
    def find_product_url(self, model_name: str, sku: str = "") -> Optional[str]:
        """
        Utility method to find the official product page URL.
        
        Override in subclass if the URL pattern is consistent.
        Example implementation:
            return f"{self.base_url}/products/{model_name.lower()}"
        
        Args:
            model_name: Product model name
            sku: Product SKU (optional)
            
        Returns:
            Product page URL or None if not found
        """
        return None
    
    def extract_from_html(self, html: str, selector: str) -> List[str]:
        """
        Utility method to extract URLs from HTML using CSS selectors.
        
        Args:
            html: HTML content
            selector: CSS selector for elements
            
        Returns:
            List of href/src attributes from matching elements
        """
        try:
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(html, 'html.parser')
            elements = soup.select(selector)
            
            urls = []
            for elem in elements:
                # Try href first (for links), then src (for images)
                url = elem.get('href') or elem.get('src')
                if url:
                    # Convert relative URLs to absolute
                    if url.startswith('/'):
                        url = self.base_url + url
                    elif not url.startswith('http'):
                        url = self.base_url + '/' + url
                    urls.append(url)
            
            return urls
        except ImportError:
            print("   ⚠️  BeautifulSoup not installed. Install with: pip install beautifulsoup4")
            return []
    
    def validate_extraction(self, manuals: List[OfficialMedia], 
                          gallery: List[str], specs: Dict) -> bool:
        """
        Validate that extracted data meets minimum quality standards.
        
        Validation Rules:
        1. If manuals extracted, each must have a valid URL
        2. If gallery extracted, each must be a valid URL
        3. Specs should not be empty (warning if it is)
        
        Args:
            manuals: List of OfficialMedia objects
            gallery: List of image URLs
            specs: Dict of specifications
            
        Returns:
            True if extraction passed validation, False otherwise
        """
        valid = True
        
        # Validate manuals
        for manual in manuals:
            if not manual.url.startswith('http'):
                print(f"      ❌ Invalid manual URL: {manual.url}")
                valid = False
        
        # Validate gallery
        for img_url in gallery:
            if not img_url.startswith('http'):
                print(f"      ❌ Invalid gallery URL: {img_url}")
                valid = False
        
        # Warn if specs empty
        if not specs:
            print(f"      ⚠️  No specs extracted (this is okay, but unusual)")
        
        return valid


# ============================================================================
# EXAMPLE IMPLEMENTATION - RolandScraper (Template)
# ============================================================================

class RolandScraper(OfficialBrandBase):
    """
    Example implementation for Roland products.
    
    This is a TEMPLATE showing how to implement a brand scraper.
    Each brand will have unique selectors, URL patterns, etc.
    """
    
    def __init__(self):
        super().__init__(
            brand_name="Roland",
            brand_domain="roland.com",
            base_url="https://roland.com"
        )
    
    def extract_manuals(self, model_name: str, sku: str = "") -> List[OfficialMedia]:
        """
        Extract manuals for Roland products from roland.com.
        
        Typical URL pattern: https://roland.com/products/{model}/downloads/
        """
        manuals = []
        
        # Example: Try to fetch product page and extract download links
        product_url = self.find_product_url(model_name)
        if not product_url:
            return manuals
        
        # In a real implementation, you would:
        # 1. Fetch the product page
        # 2. Parse the downloads section
        # 3. Extract PDF links
        # 4. Return as OfficialMedia objects
        
        # Placeholder return
        return manuals
    
    def extract_official_gallery(self, model_name: str, sku: str = "") -> List[str]:
        """
        Extract product images from Roland's official gallery.
        
        Typical URL pattern: https://roland.com/products/{model}/images/
        """
        gallery = []
        
        # In a real implementation, you would:
        # 1. Fetch the product page
        # 2. Extract image gallery URLs
        # 3. Return as direct links to High-res images
        
        return gallery
    
    def extract_specs(self, model_name: str, sku: str = "") -> Dict:
        """
        Extract technical specs from Roland product pages.
        """
        specs = {}
        
        # In a real implementation, you would parse the specs table
        
        return specs
    
    def find_product_url(self, model_name: str, sku: str = "") -> Optional[str]:
        """
        Find the official Roland product page URL.
        """
        # Example pattern (adjust based on actual Roland URL structure)
        slugified = model_name.lower().replace(' ', '-')
        return f"{self.base_url}/products/{slugified}"


if __name__ == "__main__":
    print("OfficialBrandBase - v1.0")
    print("Status: Abstract base class loaded. Create subclasses for each brand.")
