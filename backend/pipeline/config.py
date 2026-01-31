"""
Pipeline Configuration - Single source of truth for all paths and settings.
"""

from pathlib import Path
from pydantic_settings import BaseSettings
from typing import List, Optional
import os


class PipelineConfig(BaseSettings):
    """Unified configuration for the entire pipeline."""

    # === Base Paths ===
    ROOT_DIR: Path = Path(__file__).resolve().parent.parent.parent
    BACKEND_DIR: Path = ROOT_DIR / "backend"
    FRONTEND_DIR: Path = ROOT_DIR / "frontend"

    # === Data Storage (5 clean stages) ===
    DATA_DIR: Path = BACKEND_DIR / "data"

    # Stage 1: Raw source data
    OFFICIAL_DIR: Path = DATA_DIR / "1_official"      # Manufacturer data
    COMMERCIAL_DIR: Path = DATA_DIR / "2_commercial"  # Halilit prices/SKU
    CONTEXTUAL_DIR: Path = DATA_DIR / "3_contextual"  # Reviews/tips

    # Stage 2: Validated/processed
    VALIDATED_DIR: Path = DATA_DIR / "4_validated"    # After layer processing

    # Stage 3: Final output
    GOLDEN_DIR: Path = DATA_DIR / "5_golden"          # Production-ready catalogs

    # === Frontend Output ===
    FRONTEND_DATA_DIR: Path = FRONTEND_DIR / "public" / "data"
    FRONTEND_ASSETS_DIR: Path = FRONTEND_DIR / "public" / "assets"
    FRONTEND_LOGOS_DIR: Path = FRONTEND_ASSETS_DIR / "logos"
    FRONTEND_IMAGES_DIR: Path = FRONTEND_ASSETS_DIR / "images"

    # === Supporting Data ===
    BRANDS_DIR: Path = DATA_DIR / "brands"            # Brand metadata
    BADGES_DIR: Path = DATA_DIR / "badges"            # Quality badges
    REPORTS_DIR: Path = DATA_DIR / "reports"          # Pipeline reports

    # === Database ===
    DB_PATH: Path = DATA_DIR / "pipeline.db"

    # === Scraper Settings ===
    SCRAPER_HEADLESS: bool = True
    SCRAPER_TIMEOUT_MS: int = 30000
    SCRAPER_RETRIES: int = 3
    SCRAPER_RETRY_DELAY_S: int = 2
    SCRAPER_CONCURRENT: int = 5

    # === External URLs ===
    HALILIT_BASE_URL: str = "https://www.halilit.com"

    # === Context Agent (Real Web Search) ===
    SERP_API_KEY: Optional[str] = None  # Set via SERP_API_KEY env var
    OPENAI_API_KEY: Optional[str] = None  # Set via OPENAI_API_KEY env var
    CONTEXT_SEARCH_ENABLED: bool = True
    CONTEXT_TRUSTED_DOMAINS: List[str] = [
        "soundonsound.com",
        "musictech.com",
        "mixonline.com",
        "tapeop.com",
        "gearspace.com",
        "attackmagazine.com",
        "residentadvisor.net",
        "pro-tools-expert.com",
    ]

    # === Pipeline Settings ===
    TIER_THRESHOLDS: dict = {
        "diamond": 75,
        "gold": 60,
        "silver": 40,
        "bronze": 0,
    }

    # === TypeScript Generation ===
    GENERATE_TYPES: bool = True
    TYPES_OUTPUT_PATH: Path = FRONTEND_DIR / "src" / "types" / "generated.ts"

    # === Environment ===
    ENV: str = "development"
    DEBUG: bool = False

    class Config:
        env_prefix = "PIPELINE_"
        case_sensitive = True

    def ensure_directories(self) -> None:
        """Create all required directories."""
        dirs = [
            self.OFFICIAL_DIR,
            self.COMMERCIAL_DIR,
            self.CONTEXTUAL_DIR,
            self.VALIDATED_DIR,
            self.GOLDEN_DIR,
            self.FRONTEND_DATA_DIR,
            self.FRONTEND_LOGOS_DIR,
            self.FRONTEND_IMAGES_DIR,
            self.BRANDS_DIR,
            self.BADGES_DIR,
            self.REPORTS_DIR,
        ]
        for d in dirs:
            d.mkdir(parents=True, exist_ok=True)


# Global config instance
config = PipelineConfig()
