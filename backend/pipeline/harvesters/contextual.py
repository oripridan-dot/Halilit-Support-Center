"""
Contextual Data Harvester - Real web search + AI synthesis for reviews.

This harvester is responsible for:
- Searching trusted review sites for product reviews
- Extracting and synthesizing pros/cons/tips using AI
- Creating ContextualData records

Requires API keys:
  - SERP_API_KEY or GOOGLE_API_KEY for web search
  - OPENAI_API_KEY for AI synthesis
"""

import asyncio
import json
import os
import re
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime

try:
    import httpx
    HTTPX_AVAILABLE = True
except ImportError:
    HTTPX_AVAILABLE = False

try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

from ..config import config
from ..models import ContextualData, ReviewSource

logger = logging.getLogger(__name__)


class ContextualHarvester:
    """
    Harvests contextual data from web reviews using search + AI synthesis.

    The "Real World" knowledge pillar - synthesizes expert opinions
    from trusted audio/music production review sites.
    """

    TRUSTED_DOMAINS = [
        "soundonsound.com",
        "musictech.com",
        "mixonline.com",
        "tapeop.com",
        "gearspace.com",
        "attackmagazine.com",
        "residentadvisor.net",
        "pro-tools-expert.com",
        "musicradar.com",
        "audionetwork.com",
    ]

    def __init__(self):
        self.output_dir = config.CONTEXTUAL_DIR
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # API Keys
        self.serp_api_key = os.environ.get(
            'SERP_API_KEY') or config.SERP_API_KEY
        self.openai_api_key = os.environ.get(
            'OPENAI_API_KEY') or config.OPENAI_API_KEY

        # Check if real APIs are available
        self.search_enabled = bool(self.serp_api_key)
        self.ai_enabled = OPENAI_AVAILABLE and bool(self.openai_api_key)

        if not self.search_enabled:
            logger.warning(
                "⚠️ SERP_API_KEY not set - using mock search results")
        if not self.ai_enabled:
            logger.warning(
                "⚠️ OPENAI_API_KEY not set - using mock AI synthesis")

    async def harvest_product(
        self,
        product_id: str,
        product_name: str,
        brand_name: str,
    ) -> ContextualData:
        """
        Harvest contextual data for a single product.

        Args:
            product_id: Product identifier
            product_name: Product display name
            brand_name: Brand name for search context

        Returns:
            ContextualData with reviews, pros, cons, tips
        """
        logger.info(f"🔍 Researching: {brand_name} {product_name}")

        # Step 1: Search for reviews
        search_results = await self._search_reviews(brand_name, product_name)

        if len(search_results) < 2:
            logger.info(
                f"  ⚠️ Insufficient sources found ({len(search_results)})")
            return ContextualData(
                product_id=product_id,
                verified_sources=search_results,
                confidence_score=min(len(search_results) * 20, 30),
            )

        # Step 2: Synthesize insights with AI
        insights = await self._synthesize_insights(search_results, product_name)

        # Step 3: Calculate confidence score
        # Base 40 + 15 per trusted source, max 100
        confidence = 40 + (len(search_results) * 15)
        confidence = min(confidence, 100)

        return ContextualData(
            product_id=product_id,
            verified_sources=search_results,
            pros=insights.get('pros', []),
            cons=insights.get('cons', []),
            recurring_issues=insights.get('recurring_issues', []),
            expert_tips=insights.get('expert_tips', []),
            confidence_score=confidence,
        )

    async def harvest_brand(
        self,
        brand_id: str,
        products: List[Dict[str, str]]
    ) -> List[ContextualData]:
        """
        Harvest contextual data for all products in a brand.

        Args:
            brand_id: Brand identifier
            products: List of dicts with 'id', 'name' keys

        Returns:
            List of ContextualData records
        """
        results = []

        for product in products:
            data = await self.harvest_product(
                product_id=product['id'],
                product_name=product['name'],
                brand_name=product.get('brand', brand_id),
            )
            results.append(data)

            # Rate limiting
            await asyncio.sleep(1)

        # Save results
        self._save_results(brand_id, results)

        logger.info(f"✅ Harvested context for {len(results)} products")
        return results

    async def _search_reviews(
        self,
        brand: str,
        product: str
    ) -> List[ReviewSource]:
        """Search for product reviews on trusted sites."""

        if self.search_enabled and HTTPX_AVAILABLE:
            return await self._search_serp_api(brand, product)
        else:
            return await self._search_mock(brand, product)

    async def _search_serp_api(
        self,
        brand: str,
        product: str
    ) -> List[ReviewSource]:
        """Real search using SerpAPI."""
        query = f"{brand} {product} review"

        # Filter to trusted domains
        site_filter = " OR ".join(
            [f"site:{d}" for d in self.TRUSTED_DOMAINS[:5]])
        full_query = f"{query} ({site_filter})"

        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    "https://serpapi.com/search",
                    params={
                        "q": full_query,
                        "api_key": self.serp_api_key,
                        "num": 10,
                    },
                    timeout=30.0,
                )

                if response.status_code != 200:
                    logger.error(f"SerpAPI error: {response.status_code}")
                    return []

                data = response.json()
                results = []

                for item in data.get('organic_results', [])[:5]:
                    # Verify it's from a trusted domain
                    link = item.get('link', '')
                    domain = self._extract_domain(link)

                    if domain in self.TRUSTED_DOMAINS:
                        results.append(ReviewSource(
                            source_name=domain.split('.')[0].title(),
                            url=link,
                            snippet=item.get('snippet', '')[:200],
                        ))

                return results

        except Exception as e:
            logger.error(f"Search error: {e}")
            return []

    async def _search_mock(
        self,
        brand: str,
        product: str
    ) -> List[ReviewSource]:
        """Mock search results for testing."""
        # Simulate finding reviews based on product name patterns
        results = []

        # Common product patterns that would have reviews
        if any(x in product.lower() for x in ['a7', 's3h', 'sub', 't5v', 't7v', 't8v']):
            results.append(ReviewSource(
                source_name="Sound On Sound",
                url=f"https://soundonsound.com/reviews/{brand.lower().replace(' ', '-')}-{product.lower().replace(' ', '-')}",
                snippet=f"In-depth review of the {brand} {product} studio monitor.",
            ))
            results.append(ReviewSource(
                source_name="MusicTech",
                url=f"https://musictech.com/reviews/{product.lower()}",
                snippet=f"We test the {brand} {product} in our studio.",
            ))

        if any(x in product.lower() for x in ['headphone', 'interface', 'mic']):
            results.append(ReviewSource(
                source_name="TapeOp",
                url=f"https://tapeop.com/reviews/gear/{brand.lower()}-{product.lower()}",
                snippet=f"Hands-on with the {brand} {product}.",
            ))

        return results

    async def _synthesize_insights(
        self,
        sources: List[ReviewSource],
        product_name: str
    ) -> Dict[str, List[str]]:
        """Synthesize pros/cons/tips from search results using AI."""

        if self.ai_enabled:
            return await self._synthesize_openai(sources, product_name)
        else:
            return await self._synthesize_mock(sources, product_name)

    async def _synthesize_openai(
        self,
        sources: List[ReviewSource],
        product_name: str
    ) -> Dict[str, List[str]]:
        """Real AI synthesis using OpenAI."""
        try:
            client = openai.AsyncOpenAI(api_key=self.openai_api_key)

            # Build context from snippets
            context = "\n".join([
                f"- {s.source_name}: {s.snippet}"
                for s in sources if s.snippet
            ])

            prompt = f"""Analyze these review snippets for {product_name}:

{context}

Based on these sources, extract:
1. PROS: 2-4 consensus strengths mentioned across reviews
2. CONS: 2-4 consensus weaknesses or limitations  
3. RECURRING_ISSUES: Any reliability/quality issues mentioned
4. EXPERT_TIPS: Pro tips for getting the best results

Respond in JSON format:
{{"pros": [...], "cons": [...], "recurring_issues": [...], "expert_tips": [...]}}"""

            response = await client.chat.completions.create(
                model="gpt-4o-mini",  # Cost-effective for this task
                messages=[
                    {"role": "system", "content": "You are a professional audio equipment reviewer. Extract factual insights from review sources."},
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"},
                max_tokens=500,
            )

            content = response.choices[0].message.content
            return json.loads(content)

        except Exception as e:
            logger.error(f"OpenAI synthesis error: {e}")
            return await self._synthesize_mock(sources, product_name)

    async def _synthesize_mock(
        self,
        sources: List[ReviewSource],
        product_name: str
    ) -> Dict[str, List[str]]:
        """Mock AI synthesis for testing."""
        # Generate plausible insights based on product type
        is_monitor = any(x in product_name.lower()
                         for x in ['monitor', 'speaker', 'sub'])
        is_headphone = 'headphone' in product_name.lower()

        if is_monitor:
            return {
                "pros": [
                    "Excellent transient response and clarity",
                    "Wide sweet spot for mixing",
                    "Accurate low-end reproduction",
                ],
                "cons": [
                    "Rear bass port requires wall distance",
                    "Higher price point in category",
                ],
                "recurring_issues": [],
                "expert_tips": [
                    "Use room correction software for best results",
                    "Position at ear height on isolation pads",
                ],
            }
        elif is_headphone:
            return {
                "pros": [
                    "Comfortable for long sessions",
                    "Accurate frequency response",
                ],
                "cons": [
                    "Requires headphone amp for best performance",
                ],
                "recurring_issues": [],
                "expert_tips": [
                    "Break in for 40+ hours before critical listening",
                ],
            }
        else:
            return {
                "pros": [f"Well-reviewed {product_name}"],
                "cons": [],
                "recurring_issues": [],
                "expert_tips": [],
            }

    def _extract_domain(self, url: str) -> str:
        """Extract domain from URL."""
        match = re.search(r'https?://(?:www\.)?([^/]+)', url)
        return match.group(1) if match else ""

    def _save_results(self, brand_id: str, data: List[ContextualData]) -> None:
        """Save harvested data to JSON."""
        output_file = self.output_dir / f"{brand_id}.json"
        output = {
            "brand_id": brand_id,
            "harvested_at": datetime.utcnow().isoformat(),
            "product_count": len(data),
            "products": [d.model_dump(mode='json') for d in data],
        }
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(output, f, indent=2, ensure_ascii=False)
        logger.info(f"Saved contextual data to {output_file}")

    def load_cached(self, brand_id: str) -> Optional[List[ContextualData]]:
        """Load previously harvested data."""
        cache_file = self.output_dir / f"{brand_id}.json"
        if cache_file.exists():
            with open(cache_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return [ContextualData(**p) for p in data.get('products', [])]
        return None
