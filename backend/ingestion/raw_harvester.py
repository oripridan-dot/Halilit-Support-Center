import asyncio
import os
import json
import re
import aiohttp
from pathlib import Path
from playwright.async_api import async_playwright, Page, BrowserContext


class RawHarvester:
    def __init__(self, base_dir: str = "backend/data"):
        self.base_dir = Path(base_dir)
        self.base_raw_dir = self.base_dir / "raw"
        self.processed_dir = self.base_dir / "processed"
        self.headless = True
        self.concurrency = 5  # Number of concurrent product pages to process

    async def save_raw_page(self, page: Page, url: str, directory: Path, filename_prefix: str) -> bool:
        """Navigates to URL and saves HTML content."""
        try:
            # Increase timeout and wait for load
            await page.goto(url, wait_until="domcontentloaded", timeout=60000)
            content = await page.content()

            # Sanitization
            safe_prefix = re.sub(r'[^a-zA-Z0-9_-]', '_', filename_prefix)
            filepath = directory / f"{safe_prefix}.html"

            with open(filepath, "w", encoding="utf-8") as f:
                f.write(content)

            return True
        except Exception as e:
            print(f"    ! Error fetching {url}: {e}")
            return False

    async def _download_asset(self, session: aiohttp.ClientSession, url: str, directory: Path):
        """Downloads a PDF or asset file using an existing session."""
        try:
            filename = url.split("/")[-1]
            # Simple sanitization
            filename = filename.split("?")[0]

            # Include more valid extensions
            valid_exts = [".pdf", ".jpg", ".jpeg", ".png", ".webp", ".mp4",
                          ".mov", ".webm", ".zip"]
            if not any(filename.lower().endswith(ext) for ext in valid_exts):
                return

            save_path = directory / filename
            if save_path.exists():
                # CACHE HIT logic
                # We can touch the file to update mtime or just log it
                # print(f"      [Cache] Skiping {filename}")
                return

            # print(f"      > Downloading: {filename}")

            async with session.get(url) as resp:
                if resp.status == 200:
                    data = await resp.read()
                    with open(save_path, "wb") as f:
                        f.write(data)
                    # print(f"        Saved: {save_path}")
                else:
                    print(
                        f"        Failed download {url} status {resp.status}")

        except Exception as e:
            print(f"        Download error {url}: {e}")

    def _get_clean_search_term(self, product_name: str, brand_name: str) -> str:
        """
        Extracts a searchable model name from the full Halilit product title.
        Example: "מוניטור אולפני ADAM Audio S3H" -> "S3H"
        """
        # 1. Remove non-ascii (Hebrew)
        name = "".join([c for c in product_name if ord(c) < 128])

        # 2. Case insensitive cleanup
        lower_name = name.lower()
        lower_brand = brand_name.lower()

        # Remove brand
        lower_name = lower_name.replace(lower_brand, "")
        lower_name = lower_name.replace("adam", "")

        # 3. Remove stopwords
        stopwords = [
            "studio", "monitor", "active", "subwoofer", "headphones",
            "nearfield", "midfield", "reference", "series", "pro",
            "powered", "2-way", "3-way", "audio", "pair", "left", "right"
        ]

        for noun in stopwords:
            lower_name = lower_name.replace(noun, " ")

        # 4. Cleanup Whitespace
        parts = lower_name.split()

        if not parts:
            return ""

        # Strategy: Prioritize tokens with digits or hyphens (e.g. S3H, H-200, SP-5)
        # Regex to find tokens that contain at least one digit
        complex_tokens = [p for p in parts if any(c.isdigit() for c in p)]

        if complex_tokens:
            # Take the longest one usually? or first one.
            # S3H is short, SP-5 is short.
            # Let's take the first one.
            return complex_tokens[0].upper()

        # Fallback: take the first token (presumably specific model name)
        return parts[0].upper()

    def _score_link_match(self, href: str, search_term: str) -> int:
        """
        Scores a link for relevance. Higher is better.
        """
        score = 0
        href_lower = href.lower()
        term_lower = search_term.lower()

        # Disqualifiers
        if "search" in href_lower or "page" in href_lower:
            return -100
        if "news" in href_lower or "blog" in href_lower:
            score -= 5
        if "review" in href_lower:
            score -= 5

        # Qualifiers
        if term_lower in href_lower:
            score += 10
            # Boost if it ends with the term (e.g. .../s3h)
            if href_lower.rstrip("/").endswith(term_lower):
                score += 20

        # Structure boost
        if "product" in href_lower or "series" in href_lower:
            score += 5

        # Penalty for length (shorter URLs are usually main product pages)
        score -= len(href) * 0.05

        return score

    async def _process_single_product_deep(self, context: BrowserContext, product: dict, brand_name: str, base_url: str, official_dir: Path, sem: asyncio.Semaphore):
        """
        Process a single product inside a semaphore to limit concurrency.
        """
        async with sem:
            p_name = product.get("name", "")
            halilit_id = product.get("halilit_id", "")

            search_term = self._get_clean_search_term(p_name, brand_name)

            if not search_term or len(search_term) < 2:
                print(
                    f"    [Skip] {halilit_id}: Term too short '{search_term}'")
                return

            # Product specific directory
            product_dir = official_dir / halilit_id
            product_dir.mkdir(parents=True, exist_ok=True)

            # Simple Cache check (if folder has content, maybe skip? For now we overwrite/add)
            # pdfs = list(product_dir.glob("*.pdf"))
            # if pdfs:
            #     print(f"    [Cache] {halilit_id} already has assets.")
            #     return

            page = await context.new_page()

            try:
                # 1. Search
                search_url = f"{base_url.rstrip('/')}/en/search/{search_term}"
                # print(f"    [Search] {halilit_id}: Term '{search_term}'")

                await page.goto(search_url, wait_until="domcontentloaded", timeout=30000)

                # 2. Find Best Match
                links_eval = await page.eval_on_selector_all("a", """
                    elements => elements.map(e => ({
                        text: e.innerText,
                        href: e.href
                    }))
                """)

                # Filter valid links
                candidates = []
                unique_urls = set()

                for l in links_eval:
                    href = l['href']
                    if not href or href == search_url:
                        continue
                    if href in unique_urls:
                        continue
                    if base_url not in href:
                        continue  # Ensure specific domain

                    unique_urls.add(href)

                    score = self._score_link_match(href, search_term)

                    # Only consider positive matches (term must be in url essentially)
                    if search_term.lower() in href.lower() and score > -50:
                        candidates.append((href, score))

                if not candidates:
                    print(
                        f"    [Fail] {halilit_id}: No matches for '{search_term}'")
                    await page.close()
                    return

                # Sort by score descending
                candidates.sort(key=lambda x: x[1], reverse=True)
                best_url = candidates[0][0]

                # print(f"    [Match] {halilit_id}: {best_url}")

                # 3. Visit Product Page
                if await self.save_raw_page(page, best_url, product_dir, "official_page"):

                    # 4. Hunt for Assets (PDFs + Images)
                    asset_urls = set()

                    # A. PDFs
                    pdf_links = set(await page.eval_on_selector_all("a[href$='.pdf']", "elements => elements.map(e => e.href)"))
                    good_pdfs = [p for p in pdf_links if any(
                        x in p.lower() for x in ["manual", "datasheet", "user", "guide", "sheet"])]
                    if not good_pdfs:
                        good_pdfs = list(pdf_links)
                    asset_urls.update(good_pdfs)

                    # A2. HTML Documentation / Knowledge Base Links
                    # Look for links that might be manuals but are not PDFs
                    doc_links_eval = await page.eval_on_selector_all("a", """
                        elements => elements.map(e => ({
                            text: e.innerText,
                            href: e.href,
                            class: e.className
                        }))
                    """)

                    doc_keywords = [
                        "manual", "user guide", "documentation", "read online", "getting started"]
                    html_docs = []

                    for link in doc_links_eval:
                        href = link['href']
                        text = link['text'].lower()

                        if not href or href in asset_urls or href == best_url:
                            continue

                        # Must be same domain usually to be scrapeable
                        if base_url not in href:
                            continue

                        if any(k in text for k in doc_keywords):
                            if not href.endswith(".pdf") and not href.endswith(".zip"):
                                html_docs.append((href, text))

                    # Process HTML Docs
                    for i, (doc_url, doc_text) in enumerate(html_docs):
                        # No limit - capture all found documentation links
                        # Save them as raw html
                        safe_text = re.sub(
                            r'[^a-zA-Z0-9_-]', '_', doc_text[:20])
                        fname = f"doc_{safe_text}_{i}"
                        print(
                            f"      > Found HTML Doc: {doc_text} -> {doc_url}")
                        await self.save_raw_page(page, doc_url, product_dir, fname)

                    # C. Videos & 3D Models
                    # Broaden the search for links
                    media_links = await page.eval_on_selector_all("a", """
                        elements => elements.map(e => e.href)
                    """)

                    media_exts = [".mp4", ".mov", ".webm", ".zip"]
                    for link in media_links:
                        if not link:
                            continue
                         # Clean url
                        link_clean = link.split("?")[0].lower()
                        if any(link_clean.endswith(ext) for ext in media_exts):
                            asset_urls.add(link)

                    # B. Images
                    # B1. OG Image
                    try:
                        og_image = await page.get_attribute('meta[property="og:image"]', 'content')
                        if og_image:
                            asset_urls.add(og_image)
                    except:
                        pass

                    # B2. Linked Images (Gallery)
                    img_links = await page.eval_on_selector_all("a", """
                        elements => elements.map(e => e.href)
                    """)
                    good_imgs = [
                        l for l in img_links
                        if l and any(l.lower().endswith(ext) for ext in ['.jpg', '.jpeg', '.png', '.webp'])
                        and not any(x in l.lower() for x in ['logo', 'icon', 'avatar'])
                    ]
                    asset_urls.update(good_imgs)

                    # B3. Embedded Images (<img> tags)
                    # Capture high quality images found directly on page
                    img_srcs = await page.eval_on_selector_all("img", """
                        elements => elements.map(e => e.src)
                    """)
                    good_srcs = [
                        l for l in img_srcs
                        if l and any(l.lower().endswith(ext) for ext in ['.jpg', '.jpeg', '.png', '.webp'])
                        and not any(x in l.lower() for x in ['logo', 'icon', 'avatar'])
                    ]
                    # Filter out tiny images (tracking pixels, small ui elements) if possible?
                    # For now, just grab them, optimizer will deal with valid images.
                    asset_urls.update(good_srcs)

                    if asset_urls:
                        print(
                            f"    [Assets] {halilit_id}: Downloading {len(asset_urls)} assets...")
                        async with aiohttp.ClientSession() as session:
                            tasks = [self._download_asset(
                                session, url, product_dir) for url in asset_urls]
                            await asyncio.gather(*tasks)
                        print(f"    [Done] {halilit_id}: Completed assets.")
                    else:
                        print(f"    [Done] {halilit_id}: No assets found.")

                else:
                    print(
                        f"    [Fail] {halilit_id}: Could not load page {best_url}")

            except Exception as e:
                print(f"    [Error] {halilit_id}: {e}")
            finally:
                await page.close()

    async def harvest_brand_technical_deep(self, brand_id: str, brand_name: str, url: str):
        print(f"Harvesting Technical Deep [Official Search]: {brand_name}")

        official_dir = self.base_raw_dir / "official" / brand_id
        official_dir.mkdir(parents=True, exist_ok=True)

        processed_file = self.processed_dir / f"{brand_id}.json"
        if not processed_file.exists():
            print(f"  ! No processed list found for {brand_id}")
            return

        with open(processed_file, "r") as f:
            data = json.load(f)
            products = data.get("products", [])

        print(
            f"  > Processing {len(products)} products with {self.concurrency}x concurrency...")

        sem = asyncio.Semaphore(self.concurrency)
        tasks = []

        # Create tasks for all products
        for product in products:
            tasks.append(
                self._process_single_product_deep(
                    self.context, product, brand_name, url, official_dir, sem
                )
            )

        # Run all
        await asyncio.gather(*tasks)

    async def harvest_brand_commercial(self, brand_id: str, brand_name: str, url: str):
        print(f"Harvesting Commercial [Halilit]: {brand_name} ({url})")

        brand_dir = self.base_raw_dir / "halilit" / brand_id
        brand_dir.mkdir(parents=True, exist_ok=True)

        page = await self.context.new_page()
        success = await self.save_raw_page(page, url, brand_dir, filename_prefix="brand_listing")

        if success:
            links = await page.eval_on_selector_all("a", """
                elements => elements.map(e => e.href)
            """)

            product_urls = set([
                l for l in links
                if ("/items/" in l or "/p/" in l)
                and l != url
                and "halilit.com" in l
            ])

            print(f"  > Found {len(product_urls)} potential product links.")

            # Processing commercial products sequentially is fine for now as it's just one list
            for i, prod_url in enumerate(product_urls):
                try:
                    slug = prod_url.split("/")[-1].split("?")[0]
                    if not slug:
                        slug = f"product_{i}"

                    existing_file = brand_dir / f"{slug}.html"
                    if not existing_file.exists():
                        print(f"    - Fetching product: {slug}")
                        await self.save_raw_page(page, prod_url, brand_dir, filename_prefix=slug)
                except Exception as e:
                    print(f"    ! Failed to fetch {prod_url}: {e}")

        await page.close()

    async def run(self, brand_id: str, step: str = "all"):
        # Load Manifest
        manifest_path = Path("backend/ingestion/manifest.json")
        brands_config = {}
        if manifest_path.exists():
            with open(manifest_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                for b in data.get("brands", []):
                    brands_config[b["id"]] = {
                        "name": b["name"],
                        "halilit_url": b.get("commercial", {}).get("source_url"),
                        "official_url": b.get("technical", {}).get("source_url")
                    }

        # Fallback / Override for testing if not in manifest or specific overrides needed
        # But prefer manifest.

        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=self.headless)
            self.context = await browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            )

            if brand_id in brands_config:
                b = brands_config[brand_id]
                halilit_url = b.get("halilit_url")
                official_url = b.get("official_url")

                if halilit_url and step in ["all", "commercial"]:
                    # 1. Harvest Commercial (Halilit)
                    print(
                        f"--- 🛒 Harvesting Commercial Data (Halilit) for {b['name']} ---")
                    await self.harvest_brand_commercial(brand_id, b["name"], halilit_url)
                elif not halilit_url:
                    print(f"--- ⚠️ No Commercial URL found for {brand_id} ---")

                if official_url and step in ["all", "technical"]:
                    # 2. Harvest Technical (Official)
                    print(
                        f"--- 🧬 Harvesting Technical Data (Official) for {b['name']} ---")
                    # Note: We need to ensure harvest_brand_technical_deep is defined or used correctly
                    # It seems I missed checking if that method exists in the previous read_file.
                    # But the previous code called it, so it must exist or be intended.
                    if hasattr(self, 'harvest_brand_technical_deep'):
                        await self.harvest_brand_technical_deep(brand_id, b["name"], official_url)
                    else:
                        print("Technical harvesting method not implemented yet.")
                elif not official_url and step in ["all", "technical"]:
                    print(f"--- ⚠️ No Official URL found for {brand_id} ---")
            else:
                print(f"Brand {brand_id} not found in manifest.")

            await browser.close()


if __name__ == "__main__":
    import argparse
    import sys

    parser = argparse.ArgumentParser()
    parser.add_argument("brand_id", help="Brand ID")
    parser.add_argument(
        "--step", choices=["all", "commercial", "technical"], default="all", help="Which step to run")
    args = parser.parse_args()

    harvester = RawHarvester()
    # Pass the step to run method? Or just handle it here?
    # Better to update run method signature or handle logic inside run.
    # Let's handle it by creating a modified run method or just monkey-patching in thought,
    # but practically I need to pass it to run.

    asyncio.run(harvester.run(args.brand_id, step=args.step))
