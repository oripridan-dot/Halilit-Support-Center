# backend/services/official_brand_base.py
import os
import sys
import time
import logging
from abc import ABC, abstractmethod
from typing import Dict, List
from datetime import datetime
from urllib.parse import urlparse

# Setup basic logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from services.unified_ingestor import OfficialMedia

class OfficialBrandBase(ABC):
    def __init__(self, brand_name: str, brand_domain: str, base_url: str = ""):
        self.brand_name = brand_name
        self.brand_domain = brand_domain
        self.base_url = base_url or f"https://{brand_domain}"
        self.session = self._setup_session()

    @staticmethod
    def _setup_session():
        """
        Creates a session with automatic retries and connection pooling.
        Prevents the scraper from failing on transient network glitches.
        """
        try:
            import requests
            from requests.adapters import HTTPAdapter
            from urllib3.util.retry import Retry

            session = requests.Session()
            
            # Retry Strategy: 3 retries, exponential backoff (0.5s, 1s, 2s)
            # Retries on: 500, 502, 503, 504 errors
            retry_strategy = Retry(
                total=3,
                backoff_factor=0.5,
                status_forcelist=[429, 500, 502, 503, 504],
                allowed_methods=["HEAD", "GET", "OPTIONS"]
            )
            adapter = HTTPAdapter(max_retries=retry_strategy)
            session.mount("https://", adapter)
            session.mount("http://", adapter)

            session.headers.update({
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept-Language': 'en-US,en;q=0.9',
            })
            return session
        except ImportError:
            logger.error("Requests library missing. Please install: pip install requests")
            return None

    def safe_get(self, url: str, delay: float = 0.5):
        """
        Wrapper for session.get with Domain Whitelist enforcement and Rate Limiting.
        """
        if not self.validate_domain(url):
            logger.warning(f"⛔ BLOCKED: External domain {url}")
            return None
        
        # Be polite to the server
        if delay > 0:
            time.sleep(delay)

        try:
            response = self.session.get(url, timeout=15)
            response.raise_for_status() # Raise error for 4xx/5xx
            return response
        except Exception as e:
            logger.error(f"Failed to fetch {url}: {e}")
            return None

    def validate_domain(self, url: str) -> bool:
        if not url: return False
        try:
            domain = urlparse(url).netloc
            return domain == self.brand_domain or domain.endswith("." + self.brand_domain)
        except:
            return False

    def verify_pdf(self, url: str) -> bool:
        if not url: return False
        try:
             # Increased timeout to 10s for slow asset servers
             if not self.session: return False
             r = self.session.head(url, allow_redirects=True, timeout=10)
             content_type = r.headers.get('Content-Type', '').lower()
             return ('application/pdf' in content_type or url.lower().endswith('.pdf')) and r.status_code == 200
        except Exception:
             return False

    def scrape_product(self, model_name: str, sku: str = "") -> Dict:
        logger.info(f"🔍 Scraping {self.brand_name}: {model_name}")
        try:
            return {
                'manuals': self.extract_manuals(model_name, sku),
                'gallery': self.extract_official_gallery(model_name, sku),
                'specs': self.extract_specs(model_name, sku)
            }
        except Exception as e:
            logger.error(f"⚠️ Failed to scrape {model_name}: {e}")
            return {'manuals': [], 'gallery': [], 'specs': {}}

    # ... [Keep abstract methods extract_manuals, extract_official_gallery, extract_specs as is] ...
    @abstractmethod
    def extract_manuals(self, model_name: str, sku: str = "") -> List[OfficialMedia]: pass
    
    @abstractmethod
    def extract_official_gallery(self, model_name: str, sku: str = "") -> List[str]: pass
    
    @abstractmethod
    def extract_specs(self, model_name: str, sku: str = "") -> Dict: pass

    def _create_official_media(self, url: str, media_type: str, label: str) -> OfficialMedia:
        return OfficialMedia(
            url=url,
            type=media_type,
            label=label,
            source_domain=self.brand_domain,
            extracted_at=datetime.now().isoformat()
        )
