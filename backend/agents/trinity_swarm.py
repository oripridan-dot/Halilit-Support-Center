import os
import json
from typing import List, Dict, Optional, Any
from dotenv import load_dotenv
from pydantic import BaseModel, Field
import google.genai as genai
from backend.agents.agent_memory import MemoryAwareMixin

# --- CONFIGURATION ---
# Load environment variables (API keys)
load_dotenv()

# Initialize the new Genai client
client = genai.Client(api_key=os.environ.get("GOOGLE_API_KEY"))

# --- DATA MODELS (The Language of the Swarm) ---

class ProductDraft(BaseModel):
    id: str
    name: str
    brand: str
    price_il: float
    price_eilat: float
    image_url: Optional[str] = None
    source_url: Optional[str] = None
    official_match: Optional[bool] = False

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

# 1. COMMERCIAL SCOUT (The Hunter)
# Uses the Harvester Tool we wrote earlier

class CommercialAgent(AgentBase):
    def __init__(self):
        super().__init__(
            name="CommercialScout",
            system_instruction="You are a data harvester. Extract strict data from Halilit. Do not halllucinate prices."
        )

    def harvest(self, brand: str):
        # In a real run, this calls the python function `harvest_brand(brand)`
        # For this demo, we simulate the tool output
        print(f"🤖 [{self.name}] Running harvester tool for {brand}...")
        return {
            "id": "12345",
            "name": f"{brand} Stage 4 88",
            "brand": brand,
            "price_il": 18500,  # Verified Halilit Price
            "price_eilat": 15811,
            "url": "https://halilit.com/..."
        }

# 2. OFFICIAL VERIFIER (The Enricher)

class OfficialAgent(AgentBase):
    def __init__(self):
        super().__init__(
            name="OfficialVerifier",
            system_instruction="You are a brand expert. You match retail products to official specs."
        )

    def enrich(self, draft: Dict):
        # Simulating finding a better image
        return {
            **draft,
            "image_url": "https://official-brand-site.com/assets/high-res.jpg",  # Overwritten
            "official_match": True
        }

# 3. EXTERNAL VALIDATOR (The Auditor - "From Aside")

class ValidatorAgent(AgentBase):
    def __init__(self):
        super().__init__(
            name="ExternalValidator",
            model_name="gemini-2.0-flash",  # Updated to a valid model
            system_instruction="""
            You are the COMPLIANCE AUDITOR. You check product drafts against Strict Rules.

            STRICT RULES:
            1. Price Consistency: Eilat price must be ~17% lower than IL price.
            2. Brand Integrity: Brand must match the provided Taxonomy List.
            3. Data Completeness: ID, Name, and Image are mandatory.

            You output JSON only.
            """
        )

    def audit(self, product_data: Dict, taxonomy_list: List[str]) -> AuditReport:
        prompt = f"""
        AUDIT THIS RECORD:
        {json.dumps(product_data, indent=2)}

        VALID TAXONOMY: {json.dumps(taxonomy_list)}

        Output strictly valid JSON matching the AuditReport schema. Return a SINGLE JSON OBJECT.
        Structure:
        {{
            "product_id": "...",
            "status": "APPROVED" | "REJECTED",
            "risk_score": 0-100,
            "violations": ["...", "..."],
            "auditor_notes": "..."
        }}
        """

        # Force JSON response
        try:
            result = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt,
                config={
                    "system_instruction": self.system_instruction,
                    "response_mime_type": "application/json"
                }
            )
            try:
                text = result.text if hasattr(result, 'text') else str(result)
                return AuditReport.model_validate_json(text)
            except:
                # Fallback for list response
                text = result.text if hasattr(result, 'text') else str(result)
                data = json.loads(text)
                if isinstance(data, list) and len(data) > 0:
                    return AuditReport.model_validate(data[0])
                raise
        except Exception as e:
            print(f"[{self.name}] AI Error: {e}. Returning mock result.")

        # Fallback Mock for Demo/No-API-Key scenario
        print(f"[{self.name}] (Mocking response due to missing API/Error)")

        # Simple logic to simulate the AI's "Thought"
        violations = []
        if product_data.get('brand') not in taxonomy_list:
            violations.append(
                f"Brand '{product_data.get('brand')}' not in taxonomy.")

        # Eilat price check
        il_price = product_data.get('price_il', 0)
        eilat_price = product_data.get('price_eilat', 0)
        ratio = eilat_price / il_price if il_price else 0
        if not (0.80 < ratio < 0.90):  # roughly 17% off is 0.83
            violations.append(f"Price ratio suspiciously off: {ratio:.2f}")

        if violations:
            return AuditReport(
                product_id=product_data.get('id'),
                status="REJECTED",
                risk_score=90,
                violations=violations,
                auditor_notes="Automated fallback check failed."
            )
        else:
            return AuditReport(
                product_id=product_data.get('id'),
                status="APPROVED",
                risk_score=0,
                violations=[],
                auditor_notes="Automated fallback check passed."
            )

# --- THE SWARM CONTROLLER (The Supervisor) ---

class TrinitySwarm:
    def __init__(self):
        self.scout = CommercialAgent()
        self.verifier = OfficialAgent()
        self.auditor = ValidatorAgent()
        self.processed_products = []  # Store processed products

        # Load Taxonomy for the Auditor
        # Adjust path to be relative to this script execution or absolute
        taxonomy_path = os.path.join(os.path.dirname(
            __file__), '../../frontend/public/data/taxonomy_brands.json')
        # If not found, use a mockup
        if os.path.exists(taxonomy_path):
            with open(taxonomy_path, 'r') as f:
                self.taxonomy = list(json.load(f).keys())
        else:
            # Try another location or mock
            self.taxonomy = ["Nord", "Roland", "Yamaha", "Korg"]  # Mock

    def process_brand(self, brand_name: str):
        print(f"\n🚀 STARTING TRINITY SWARM FOR: {brand_name}\n")

        # Step 1: Scout
        raw_data = self.scout.harvest(brand_name)

        # Step 2: Verify & Enrich
        enriched_data = self.verifier.enrich(raw_data)

        # Step 3: EXTERNAL AUDIT (The "Aside" Review)
        print(f"⚖️ [System] Submitting to External Validator...")
        audit_result = self.auditor.audit(enriched_data, self.taxonomy)

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

        # Step 3: EXTERNAL AUDIT (The "Aside" Review)
        print(f"⚖️ [System] Submitting to External Validator...")
        audit_result = self.auditor.audit(enriched_data, self.taxonomy)

        audit_results.append(audit_result.model_dump())

        if audit_result.status == "APPROVED":
            approved_products.append(enriched_data)
            print(f"✅ Product APPROVED: {enriched_data.get('name')}")
        else:
            print(f"🛑 Product REJECTED: {enriched_data.get('name')}")

        return {
            "brand": brand_name,
            "products": approved_products,
            "audit_results": audit_results,
            "status": "COMPLETE",
            "approved_count": len(approved_products)
        }

    def handle_audit_outcome(self, data, report: AuditReport):
        print(f"\n📋 --- AUDIT REPORT FOR {data['name']} ---")
        print(f"STATUS: {report.status}")
        print(f"RISK:   {report.risk_score}/100")

        if report.status == "APPROVED":
            print("✅ Product Accepted into Golden Record.")
            # Save to DB logic here
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
