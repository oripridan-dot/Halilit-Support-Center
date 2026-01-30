import asyncio
import re
import aiohttp
from pathlib import Path
from playwright.async_api import async_playwright, Page
from backend.models.core import BrandInfo
import logging

logger = logging.getLogger("BrandHarvester")


class BrandHarvester:
    def __init__(self, output_dir: str = "backend/data/brands", headless: bool = True):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.headless = headless

    async def harvest_brand(self, brand_id: str, brand_name: str, url: str) -> BrandInfo:
        """
        Scrapes the brand's official website for metadata and assets.
        """
        if not url:
            logger.warning(
                f"No official URL provided for {brand_name} ({brand_id})")
            return None

        logger.info(f"Harvesting brand: {brand_name} from {url}")

        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=self.headless)
            page = await browser.new_page()

            try:
                # Go to homepage
                await page.goto(url, wait_until="domcontentloaded", timeout=60000)

                # Extract Info
                description = await self._extract_description(page)
                logo_url = await self._extract_logo(page)
                social_links = await self._extract_socials(page)

                # Create Model
                brand_info = BrandInfo(
                    id=brand_id,
                    name=brand_name,
                    official_website=url,
                    logo_url=logo_url,
                    description=description,
                    social_links=social_links
                )

                # Download Logo if found
                if logo_url:
                    local_logo_path = await self._download_logo(logo_url, brand_id)
                    brand_info.logo_local_path = str(local_logo_path)

                # Save JSON
                self._save_brand_info(brand_info)

                return brand_info

            except Exception as e:
                logger.error(f"Error harvesting brand {brand_name}: {e}")
                return None
            finally:
                await browser.close()

    async def _extract_description(self, page: Page) -> str:
        # Metatag description
        try:
            elm = await page.query_selector("meta[name='description']")
            if elm:
                return await elm.get_attribute("content")

            # Open Graph description
            elm = await page.query_selector("meta[property='og:description']")
            if elm:
                return await elm.get_attribute("content")
        except:
            pass
        return None

    async def _extract_logo(self, page: Page) -> str:
        # Strategy 1: Look for schema.org Organization logo
        try:
            # TODO: parsing JSON-LD
            pass
        except:
            pass

        # Strategy 2: Look for og:image
        try:
            elm = await page.query_selector("meta[property='og:image']")
            if elm:
                val = await elm.get_attribute("content")
                if val:
                    return val
        except:
            pass

        # Strategy 3: Heuristic on <img> tags
        try:
            images = await page.query_selector_all("img")
            for img in images:
                src = await img.get_attribute("src")
                alt = await img.get_attribute("alt") or ""
                cls = await img.get_attribute("class") or ""
                id_ = await img.get_attribute("id") or ""

                # Check for "logo" keyword
                if "logo" in alt.lower() or "logo" in cls.lower() or "logo" in id_.lower() or "logo" in src.lower():
                    if src:
                        # Resolve relative URLs
                        return await page.evaluate(f"new URL('{src}', document.baseURI).href")
        except:
            pass

        return None

    async def _extract_socials(self, page: Page) -> dict:
        socials = {}
        known_platforms = {
            "facebook.com": "facebook",
            "instagram.com": "instagram",
            "twitter.com": "twitter",
            "x.com": "twitter",
            "youtube.com": "youtube",
            "linkedin.com": "linkedin",
            "tiktok.com": "tiktok"
        }

        try:
            links = await page.query_selector_all("a[href]")
            for link in links:
                href = await link.get_attribute("href")
                if not href:
                    continue

                for domain, platform in known_platforms.items():
                    if domain in href and platform not in socials:
                        socials[platform] = href
        except:
            pass

        return socials

    async def _download_logo(self, url: str, brand_id: str) -> Path:
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(url) as resp:
                    if resp.status == 200:
                        data = await resp.read()

                        # Determine info
                        # simplistic extension detection
                        ext = url.split('.')[-1].split('?')[0]
                        if len(ext) > 4 or "/" in ext:
                            ext = "png"  # fallback

                        filename = f"{brand_id}_logo.{ext}"
                        path = self.output_dir / filename

                        with open(path, "wb") as f:
                            f.write(data)

                        # Relative path for JSON
                        return f"backend/data/brands/{filename}"
            except Exception as e:
                logger.error(f"Failed to download logo: {e}")
        return None

    def _save_brand_info(self, brand_info: BrandInfo):
        path = self.output_dir / f"{brand_info.id}.json"
        with open(path, "w", encoding="utf-8") as f:
            f.write(brand_info.model_dump_json(indent=2))
        logger.info(f"Saved brand info to {path}")


if __name__ == "__main__":
    # Test
    h = BrandHarvester()
    # logging.basicConfig(level=logging.INFO)
    # asyncio.run(h.harvest_brand("test-brand", "Test", "https://example.com"))
