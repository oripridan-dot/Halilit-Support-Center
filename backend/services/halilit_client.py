# backend/services/halilit_client.py
"""
Halilit Intelligence Client

Checks if a product exists in the Halilit ecosystem and retrieves
availability/pricing information.

In production, this would integrate with Halilit's API or cache the
entire price list once to avoid spamming searches. For development,
we use simulated responses.
"""

import requests
from bs4 import BeautifulSoup
import re
from typing import Dict, Optional


class HalilitClient:
    """
    Checks if a product exists in the Halilit ecosystem.
    
    Returns availability status, pricing, and product URLs.
    """
    
    SEARCH_URL = "https://www.halilit.com/search"

    def __init__(self):
        self.session = requests.Session()
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        # In production, we cache the entire price list once to avoid spamming searches
        self.price_list_cache = {}

    def check_availability(self, brand: str, model_name: str) -> Dict:
        """
        Check if a product is available through Halilit.
        
        Args:
            brand: Brand name (e.g., "roland")
            model_name: Product model name
            
        Returns:
            {
                "is_sold": bool,
                "price": float,
                "url": str or None,
                "status": str  ("IN_STOCK", "OUT_OF_STOCK", "NOT_SOLD")
            }
        """
        # 1. Clean the name for search (remove "Synthesizer", "Keyboard" etc)
        clean_name = re.sub(
            r'(Synthesizer|Keyboard|Workstation|Piano|Drum Machine|Sampler|Interface)',
            '',
            model_name,
            flags=re.IGNORECASE
        ).strip()
        
        # 2. Mock Logic for Demo (Since we can't hit live Halilit constantly in dev)
        # In real deployment, implement the actual search request here.
        
        # --- SIMULATED HALILIT RESPONSE ---
        simulated_inventory = {
            "FANTOM-06": 1490.00,
            "FANTOM-08": 1890.00,
            "RD-2000": 2400.00,
            "TR-8S": 750.00,
            "NORD STAGE 4": 4500.00,
            "NORD CLAVIA": 2800.00,
            "MOOG ONE": 10999.00,
            "MOOG SUB PHATTY": 599.00,
            "JUNO-60": 1200.00,
            "TR-909": 4500.00,
            "TB-303": 399.00,
        }
        
        for key, price in simulated_inventory.items():
            if key.lower() in clean_name.lower():
                return {
                    "is_sold": True,
                    "price": price,
                    "url": f"https://www.halilit.com/product/{key}",
                    "status": "IN_STOCK"
                }

        return {
            "is_sold": False,
            "price": 0,
            "url": None,
            "status": "NOT_SOLD"
        }

    def search_halilit(self, query: str) -> Optional[Dict]:
        """
        Advanced: Search Halilit directly (uses real API in production).
        
        Args:
            query: Search query
            
        Returns:
            Product data dict or None if not found
        """
        # TODO: Implement real Halilit search when API available
        # For now, returns None (falls back to check_availability)
        return None
