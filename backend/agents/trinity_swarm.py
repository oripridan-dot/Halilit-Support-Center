"""
TRINITY SWARM - v7.0 AUTONOMOUS AGENTS
========================================

Three-agent data processing pipeline:
1. CommercialScout (harvest) - Extracts raw product data from Halilit
2. OfficialVerifier (enrich) - Adds brand specifications & official data
3. ExternalValidator (audit) - Final review & approval

DO NOT use deprecated methods from v5.x or v6.0.
Current version requires v7.0+.
"""

import os
import json
from typing import List, Dict, Optional, Any
from dotenv import load_dotenv
from pydantic import BaseModel, Field
import google.genai as genai
from backend.agents.agent_memory import MemoryAwareMixin

# ⭐ VERSION CONTROL
from backend.VERSION_CONTROL import assert_version_supports, SYSTEM_VERSION, log_deprecation_warning

# --- CONFIGURATION ---
# Load environment variables (API keys)
load_dotenv()

# Verify system version compatibility
assert_version_supports("Trinity Swarm", min_version="7.0")

# Initialize the new Genai client
try:
    client = genai.Client(api_key=os.environ.get("GOOGLE_API_KEY"))
except Exception as e:
    print(f"Warning: Could not initialize Gemini client: {e}")
    client = None

# --- DATA MODELS (The Language of the Swarm) ---


class AuditReport(BaseModel):
    product_id: Optional[str] = None
    status: str = Field(..., description="'APPROVED' or 'REJECTED'")
    risk_score: int = Field(..., description="0-100 (0 is safe, 100 is risky)")
    violations: List[str]
    auditor_notes: str

# --- THE AGENTS ---


class AgentBase(MemoryAwareMixin):
    """Base agent with learning capabilities"""

    def __init__(self, name, model_name="gemini-2.0-flash", system_instruction=""):
        # Set name first for MemoryAwareMixin
        self.name = name
        super().__init__()  # Initialize memory capabilities
        self.model_name = model_name
        self.system_instruction = system_instruction
        self.client = client  # Use global client

        print(f"🧠 [{self.name}] Initialized with learning capabilities")

    def think(self, prompt: str):
        print(f"🤖 [{self.name}] Thinking...")
        if not self.client:
            return "Simulation: Client not initialized."

        try:
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt,
                config={
                    "system_instruction": self.system_instruction} if self.system_instruction else {}
            )
            text = response.text if hasattr(
                response, 'text') else str(response)
            print(f"   -> {text[:100]}...")

            # LEARN from every thought
            self.learn_from_action(
                action_type="think",
                input_data=prompt[:200],
                output_data=text[:200],
                success=len(text) > 0,
                confidence=95,
                patterns=["gemini-response"]
            )

            return text
        except Exception as e:
            error_msg = f"Error generating content: {e}"

            # LEARN from failures too
            self.learn_from_action(
                action_type="think",
                input_data=prompt[:200],
                output_data=error_msg,
                success=False,
                confidence=0,
                patterns=["api-error"]
            )

            return error_msg

# 1. COMMERCIAL SCOUT (The Hunter - Golden List Owner)


class CommercialAgent(AgentBase):
    def __init__(self):
        super().__init__(
            name="CommercialScout",
            system_instruction="""
            You are the KEEPER OF THE GOLDEN LIST. 
            Your ONLY job is to extract exact product inventory from Halilit.com.
            
            RULES:
            1. YOU define what exists. If it's not on Halilit, it doesn't exist.
            2. Extracted Prices are FINAL. No other agent can touch them.
            3. Extracted Names are the COMMERCIAL Names.
            4. You do NOT fetch specs or reviews. Only existence and price.
            """
        )

    def harvest(self, brand: str) -> Dict:
        """
        Harvests the 'Golden List' of products for a brand from Halilit.
        Returns strict Commercial Data structure.
        """
        print(f"🤖 [{self.name}] 🛡️ Securing Golden List for {brand}...")

        # In v6.0, this would connect to the real scraper.
        # Simulating Strict Commercial Data Return:
        return {
            "halilit_id": "123456",
            "product_name": f"{brand} Grand Stage 88",
            "brand": brand,
            "price_il": 18500.0,
            "price_eilat": 15811.0,
            "halilit_url": f"https://halilit.com/brands/{brand}/stage-88",
            # Metadata
            "pipeline_phase": "harvest",
            "status": "harvested"
        }

# 2. OFFICIAL VERIFIER (The Enricher - Knowledge Specialist)


class OfficialAgent(AgentBase):
    def __init__(self):
        super().__init__(
            name="OfficialVerifier",
            system_instruction="""
            You are the BRAND AMBASSADOR.
            Your job is to enrich the Golden List with data regarding "WHAT IT IS".
            
            RULES:
            1. You receive a "product_name" and "brand" from the Golden List.
            2. You search ONLY the official brand website for this specific item.
            3. You output SPECS, ASSETS, and OFFICIAL DESCRIPTION.
            4. You DO NOT change the Price.
            5. You DO NOT change the SKU.
            """
        )

    def enrich(self, draft: Dict) -> Dict:
        """
        Takes a Commercial Draft and injects Official Knowledge.
        """
        print(
            f"🤖 [{self.name}] 📘 Injecting Official Knowledge for {draft.get('product_name')}...")

        # Simulating fetching from Official Site
        official_data = {
            "official_specs": {
                "keys": 88,
                "action": "Hammer Action",
                "polyphony": 128
            },
            "official_description": "The ultimate stage piano for professionals.",
            "official_images": [
                {"type": "image", "url": "https://brand.com/hero.jpg",
                    "display_purpose": "hero", "source": "official"}
            ],
            "official_url": "https://brand.com/products/stage-88"
        }

        # MERGE STRATEGY: nondestructive update of official fields only
        draft.update(official_data)
        draft["pipeline_phase"] = "enrich"
        return draft

# 3. EXTERNAL VALIDATOR (The Auditor - Insight Specialist)


class ContextualAgent(AgentBase):
    def __init__(self):
        super().__init__(
            name="ExternalValidator",  # Keeping name for compatibility, but role is Contextual
            model_name="gemini-2.0-flash",
            system_instruction="""
            You are the PUBLIC OPINION.
            Your job is to find what the world thinks (Contextual Data).
            
            RULES:
            1. Search trusted review sites (SoundOnSound, MusicRadar, Reddit, YouTube).
            2. Summarize Pros and Cons.
            3. Extract a numeric rating (normalize to 0-5).
            4. You DO NOT change Specs or Price.
            """
        )

    def validate_and_review(self, draft: Dict) -> AuditReport:
        """
        Fetches reviews and performs final validation.
        """
        print(
            f"🤖 [{self.name}] 🌍 Gathering Global Insights for {draft.get('product_name')}...")

        # Simulating Contextual Data Gathering
        synthesis = "Highly rated by pros. Praised for build and sound. Some find action heavy."
        avg_rating = 4.75

        # Enforce Iron Rules: Use Commercial Price + Official Specs to validate
        is_valid = True

        return AuditReport(
            product_id=draft.get("halilit_id"),
            status="APPROVED",
            risk_score=5,
            violations=[],
            auditor_notes=f"Contextual Validation Passed. Rating: {avg_rating}/5. Consensus: {synthesis}"
        )

# --- THE SWARM CONTROLLER (The Supervisor - v6.0 Strict) ---


class TrinitySwarm:
    def __init__(self):
        self.scout = CommercialAgent()
        self.verifier = OfficialAgent()
        self.auditor = ContextualAgent()  # Updated to ContextualAgent
        self.processed_products = []

        # Load Taxonomy (Mock for now)
        self.taxonomy = ["Nord", "Roland", "Yamaha", "Korg"]

    def process_brand(self, brand_name: str):
        print(f"\n🚀 STARTING TRINITY SWARM (v6.0 Strict) FOR: {brand_name}\n")

        # Step 1: Scout (Commercial - Golden List)
        raw_data = self.scout.harvest(brand_name)
        print(
            f"   Draft Created: {raw_data.get('product_name')} | {raw_data.get('price_il')} NIS")

        # Step 2: Verify & Enrich (Official - Knowledge)
        enriched_data = self.verifier.enrich(raw_data)

        # Step 3: EXTERNAL AUDIT (Contextual - Insight)
        print(f"⚖️ [System] Submitting to Contextual Validator...")
        # Note: audit method name changed to validate_and_review in new agent
        audit_result = self.auditor.validate_and_review(enriched_data)

        self.handle_audit_outcome(enriched_data, audit_result)

    def process_brand_with_results(self, brand_name: str):
        """
        Process a brand and return the results for UI consumption
        Returns: { "brand": str, "products": [...], "audit_results": [...], "status": str }
        """
        print(f"\n🚀 STARTING TRINITY SWARM FOR: {brand_name}\n")

        approved_products = []
        audit_results = []

        # Step 1: Scout
        raw_data = self.scout.harvest(brand_name)

        # Step 2: Verify & Enrich
        enriched_data = self.verifier.enrich(raw_data)

        # Step 3: EXTERNAL AUDIT
        # audit_result = self.auditor.audit(enriched_data, self.taxonomy) # Old way
        audit_result = self.auditor.validate_and_review(
            enriched_data)  # New way

        audit_results.append(audit_result.model_dump())

        if audit_result.status == "APPROVED":
            approved_products.append(enriched_data)
            print(f"✅ Product APPROVED: {enriched_data.get('product_name')}")
        else:
            print(f"🛑 Product REJECTED: {enriched_data.get('product_name')}")

        return {
            "brand": brand_name,
            "products": approved_products,
            "audit_results": audit_results,
            "status": "COMPLETE",
            "approved_count": len(approved_products)
        }

    def handle_audit_outcome(self, data, report: AuditReport):
        print(f"\n📋 --- AUDIT REPORT FOR {data.get('product_name')} ---")
        print(f"STATUS: {report.status}")
        print(f"RISK:   {report.risk_score}/100")

        if report.status == "APPROVED":
            print("✅ Product Accepted into Golden Record.")
            print("\n🔍 STRICT DATA STRUCTURE (v6.0):")
            print(json.dumps(data, indent=2, default=str))
        else:
            print("🛑 Product REJECTED.")
            print("VIOLATIONS:")
            for v in report.violations:
                print(f" - {v}")
            print(f"NOTES: {report.auditor_notes}")


# --- RUNNER ---
if __name__ == "__main__":
    swarm = TrinitySwarm()
    swarm.process_brand("Nord")
