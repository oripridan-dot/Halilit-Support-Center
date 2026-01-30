from pydantic_settings import BaseSettings
from pathlib import Path


class Settings(BaseSettings):
    # Base Paths
    BASE_DIR: Path = Path(__file__).resolve().parent.parent.parent
    BACKEND_DIR: Path = BASE_DIR / "backend"
    FRONTEND_DIR: Path = BASE_DIR / "frontend"

    # Data Paths
    DATA_DIR: Path = BACKEND_DIR / "data"
    FRONTEND_PUBLIC_DIR: Path = FRONTEND_DIR / "public"
    FRONTEND_DATA_DIR: Path = FRONTEND_PUBLIC_DIR / "data"
    # Catalogs are stored directly in the data directory in the new workflow
    CATALOGS_DIR: Path = FRONTEND_DATA_DIR
    FRONTEND_CATALOGS_DIR: Path = FRONTEND_DATA_DIR
    FRONTEND_LOGOS_DIR: Path = FRONTEND_PUBLIC_DIR / "assets" / "logos"

    # Scraper Settings
    SCRAPER_HEADLESS: bool = True
    SCRAPER_TIMEOUT: int = 15000  # 15 seconds (reduced from 30s)
    SCRAPER_RETRIES: int = 2  # Reduced retries for faster failure
    SCRAPER_RETRY_DELAY: int = 1  # Reduced delay
    HALILIT_BASE_URL: str = "https://www.halilit.com"

    # Environment
    ENV: str = "development"

    class Config:
        case_sensitive = True


settings = Settings()

# Ensure critical directories exist


def ensure_dirs():
    dirs = [
        settings.DATA_DIR,
        settings.CATALOGS_DIR,
        settings.FRONTEND_DATA_DIR,
        settings.FRONTEND_CATALOGS_DIR,
        settings.FRONTEND_LOGOS_DIR
    ]
    for d in dirs:
        d.mkdir(parents=True, exist_ok=True)


if __name__ == "__main__":
    ensure_dirs()
    print(f"Configuration loaded. Base dir: {settings.BASE_DIR}")
