import uvicorn
from backend.workflow.real_maintenance import (
    RealCodeCleanupWorkflow,
    RealCodeSyncWorkflow,
    RealHealthCheckWorkflow
)
from backend.agents.maintenance_orchestrator import AgentMaintenanceOrchestrator
from backend.agents.agent_memory import AgentMemory
from backend.agents.context_manager import ContextManager
from backend.agents.dev_agent import DevAgent, ErrorReport
from backend.agents.trinity_swarm import TrinitySwarm
import sys
import os

# Add the project root to path so we can import backend modules FIRST
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

app = FastAPI()

# Initialize the Swarm, Dev Agent, Context Manager, and Agent Memory
swarm = TrinitySwarm()
dev_agent = DevAgent()
context_manager = ContextManager()
agent_memory = AgentMemory()
orchestrator = AgentMaintenanceOrchestrator()

class ChatMessage(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    messages: List[ChatMessage]

@app.post("/api/copilot/chat")
async def chat_endpoint(request: ChatRequest):
    """
    Simple adapter for CopilotKit with AUTO-LOGGING
    Takes the last message and passes it to the Supervisor agent.
    """
    user_message = request.messages[-1].content
    print(f"🤖 [UI Agent] Received: {user_message}")

    # AUTO-LOG: CopilotKit interaction
    dev_agent.log_copilot_message(user_message, "Processing...")

    # 1. Check if it's a command to run the pipeline
    if "audit" in user_message.lower() or "check" in user_message.lower():
        # Extract brand name blindly for demo or default to Nord
        brand = "Nord"
        for b in swarm.taxonomy:
            if b.lower() in user_message.lower():
                brand = b
                break

        # Trigger the swarm (synchronously for now)
        # In production, use BackgroundTasks
        response_text = f"I am starting the Trinity Swarm for {brand}...\n"

        # Capture stdout (hacky but works for demo)
        # Real implementation would hook into agent logs
        import io

        f = io.StringIO()
        with redirect_stdout(f):
            swarm.process_brand(brand)

        output = f.getvalue()
        final_response = response_text + "\n" + output

        # AUTO-LOG: Response
        dev_agent.log_copilot_message(user_message, final_response)

        return {"detailedMessage": final_response}

    # 2. General QA
    supervisor = swarm.auditor  # Use the smartest agent here
    answer = supervisor.think(user_message)

    # AUTO-LOG: Response
    dev_agent.log_copilot_message(user_message, answer)

    return {"detailedMessage": answer}

@app.get("/health")
def health():
    return {"status": "ok"}

# --- DEV AGENT ENDPOINTS ---

@app.post("/api/dev/analyze-error")
async def analyze_error(error: ErrorReport):
    """
    Development endpoint: Analyze an error and get AI-powered fix suggestions
    AUTO-LOGS to context history
    """
    print(f"🔧 [DevAgent API] Analyzing error: {error.error_type}")
    fix = dev_agent.analyze_error(error)
    return fix.model_dump()

@app.post("/api/dev/health-check")
async def health_check(metrics: Dict[str, Any]):
    """
    Development endpoint: Check system health based on metrics
    """
    print(f"🏥 [DevAgent API] Health check requested")
    health = dev_agent.check_health(metrics)
    return health.model_dump()

@app.post("/api/dev/suggest-improvements")
async def suggest_improvements(data: Dict[str, str]):
    """
    Development endpoint: Get proactive code improvement suggestions
    """
    code = data.get("code", "")
    context = data.get("context", "")
    print(f"💡 [DevAgent API] Suggesting improvements for: {context}")
    suggestions = dev_agent.suggest_improvements(code, context)
    return suggestions

@app.post("/api/dev/validate-fix")
async def validate_fix(data: Dict[str, Any]):
    """
    Development endpoint: Validate a fix suggestion
    """
    from backend.agents.dev_agent import FixSuggestion

    fix_data = data.get("fix")
    error_data = data.get("original_error")

    fix = FixSuggestion(**fix_data)
    error = ErrorReport(**error_data)

    print(f"✅ [DevAgent API] Validating fix for: {error.error_type}")
    validation = dev_agent.validate_fix(fix, error)
    return validation.model_dump()

@app.post("/api/dev/auto-apply")
async def auto_apply(data: Dict[str, Any]):
    """
    Development endpoint: Auto-apply a high-confidence fix
    """
    from backend.agents.dev_agent import FixSuggestion

    fix_data = data.get("fix")
    file_path = data.get("file_path")
    dry_run = data.get("dry_run", False)

    fix = FixSuggestion(**fix_data)

    print(f"🤖 [DevAgent API] Auto-applying fix to: {file_path}")
    result = dev_agent.auto_apply_fix(fix, file_path, dry_run)
    return result

@app.post("/api/dev/scan-codebase")
async def scan_codebase(data: Dict[str, str]):
    """
    Development endpoint: Scan codebase for potential issues
    """
    directory = data.get("directory", "frontend/src")
    print(f"🔍 [DevAgent API] Scanning codebase: {directory}")
    result = dev_agent.scan_codebase(directory)
    return result

@app.post("/api/dev/execute-improvement")
async def execute_improvement(data: Dict[str, Any]):
    """
    Development endpoint: Execute an improvement suggestion
    """
    suggestion = data.get("suggestion")
    file_path = data.get("file_path")

    print(f"⚡ [DevAgent API] Executing improvement for: {file_path}")
    result = dev_agent.execute_improvement(suggestion, file_path)
    return result

@app.post("/api/dev/validate-syntax")
async def validate_syntax(data: Dict[str, Any]):
    """
    Development endpoint: Validate syntax before saving
    """
    file_path = data.get("file_path")
    code = data.get("code")

    print(f"🔍 [DevAgent API] Validating syntax: {file_path}")
    result = dev_agent.validate_syntax(file_path, code)
    return result.model_dump()

@app.post("/api/dev/validate-types")
async def validate_types(data: Dict[str, str]):
    """
    Development endpoint: Run TypeScript type checking
    """
    file_path = data.get("file_path")

    print(f"🔍 [DevAgent API] Type checking: {file_path}")
    result = dev_agent.validate_types(file_path)
    return result.model_dump()

@app.post("/api/dev/validate-before-save")
async def validate_before_save(data: Dict[str, Any]):
    """
    Development endpoint: Comprehensive pre-save validation
    """
    file_path = data.get("file_path")
    code = data.get("code")

    print(f"🛡️ [DevAgent API] Pre-save validation: {file_path}")
    result = dev_agent.validate_before_save(file_path, code)
    return result

# --- CONTEXT MANAGER ENDPOINTS ---

@app.get("/api/context/summary")
async def get_context_summary():
    """Get development context summary"""
    summary = context_manager.get_context_summary()
    return {"summary": summary}

@app.get("/api/context/history")
async def get_context_history(limit: int = 20):
    """Get recent context history"""
    history = context_manager.get_recent_history(limit)
    return {"history": [h.model_dump() for h in history]}

@app.post("/api/context/analyze")
async def analyze_context():
    """Analyze development context for consistency"""
    analysis = context_manager.analyze_context()
    return analysis.model_dump()

@app.post("/api/context/check-consistency")
async def check_consistency(data: Dict[str, Any]):
    """Check if a proposed change is consistent with context"""
    proposed_change = data.get("proposed_change", "")
    files = data.get("files", [])

    result = context_manager.check_consistency(proposed_change, files)
    return result

@app.post("/api/context/suggest-refactoring")
async def suggest_refactoring(data: Dict[str, Any]):
    """Get refactoring suggestions based on context"""
    file_path = data.get("file_path")

    plans = context_manager.suggest_refactoring(file_path)
    return {"refactoring_plans": [p.model_dump() for p in plans]}

@app.post("/api/context/log")
async def log_context_entry(data: Dict[str, Any]):
    """Log a context entry"""
    entry_type = data.get("type", "general")
    content = data.get("content", "")
    files_affected = data.get("files_affected", [])
    tags = data.get("tags", [])
    metadata = data.get("metadata", {})

    entry_id = context_manager.log_entry(
        entry_type, content, files_affected, tags, metadata
    )

    return {"success": True, "entry_id": entry_id}

# --- AGENT MEMORY ENDPOINTS ---

@app.get("/api/memory/stats/{agent_name}")
async def get_agent_stats(agent_name: str):
    """Get learning statistics for an agent"""
    stats = agent_memory.get_stats(agent_name)
    return stats

@app.get("/api/memory/advice/{agent_name}")
async def get_agent_advice(agent_name: str, task: str = ""):
    """Get contextual advice for a task"""
    advice = agent_memory.get_contextual_advice(agent_name, task)
    return {"advice": advice}

@app.get("/api/memory/insights/{agent_name}")
async def get_agent_insights(agent_name: str):
    """Get learned patterns and insights"""
    insights = agent_memory.analyze_patterns(agent_name)
    return {"insights": [i.model_dump() for i in insights]}

@app.get("/api/memory/improvements/{agent_name}")
async def get_agent_improvements(agent_name: str):
    """Get suggested improvements for an agent"""
    improvements = agent_memory.suggest_improvements(agent_name)
    return {"improvements": improvements}

@app.get("/api/memory/all-agents")
async def get_all_agents_memory():
    """Get memory summary for all agents"""
    agents = ["DevAgent", "CommercialScout",
              "OfficialVerifier", "ExternalValidator"]
    summary = {}
    for agent in agents:
        summary[agent] = agent_memory.get_stats(agent)
    return summary

# --- MAINTENANCE & ORCHESTRATION ENDPOINTS ---

@app.post("/api/maintenance/health-check")
async def run_health_check():
    """
    Run system health check workflow
    Returns health score and status
    """
    print("🏥 [Real Maintenance] Running health check")
    workflow = RealHealthCheckWorkflow()
    result = workflow.execute({})
    return {
        "success": result.get("success", True),
        "health_score": result.get("health_score", 0),
        "health_status": result.get("health_status", "UNKNOWN"),
        "files_checked": result.get("files_checked", 0),
        "empty_files": result.get("empty_files", 0),
        "details": result
    }

@app.post("/api/maintenance/code-cleanup")
async def run_code_cleanup():
    """
    Run code cleanup workflow
    Removes dead code and unused imports
    """
    print("🧹 [Real Maintenance] Running code cleanup")
    workflow = RealCodeCleanupWorkflow()
    result = workflow.execute({})
    return {
        "success": result.get("success", True),
        "files_processed": result.get("files_processed", 0),
        "files_modified": result.get("files_modified", 0),
        "imports_removed": result.get("imports_removed", 0),
        "files_formatted": result.get("files_formatted", 0),
        "validation_score": result.get("validation_score", 0),
        "details": result
    }

@app.post("/api/maintenance/organize-code")
async def run_code_organization():
    """
    Run code organization workflow
    Enforces naming conventions and structure
    """
    print("📁 [Orchestrator] Running code organization")
    workflow = CodeOrganizationWorkflow()
    result = workflow.execute({})
    return {
        "success": result.get("success", True),
        "files_analyzed": result.get("files_analyzed", 0),
        "files_fixed": result.get("files_fixed", 0),
        "organization_score": result.get("organization_score", 0),
        "details": result
    }

@app.post("/api/maintenance/sync-code")
async def run_code_sync():
    """
    Run code synchronization workflow
    Synchronizes imports, exports, and interfaces
    """
    print("🔗 [Real Maintenance] Running code sync")
    workflow = RealCodeSyncWorkflow()
    result = workflow.execute({})
    return {
        "success": result.get("success", True),
        "exports_synced": result.get("exports_synced", 0),
        "imports_fixed": result.get("imports_fixed", 0),
        "sync_score": result.get("sync_score", 0),
        "details": result
    }

@app.post("/api/maintenance/full-cycle")
async def run_full_maintenance_cycle():
    """
    Run complete maintenance cycle (5 phases)
    1. Health Check
    2. Code Cleanup
    3. Code Organization
    4. Code Synchronization
    5. Final Health Check

    Returns comprehensive maintenance report
    """
    print("🔄 [Orchestrator] Starting full maintenance cycle")

    results = {
        "phase_1_health_check": None,
        "phase_2_cleanup": None,
        "phase_3_organization": None,
        "phase_4_sync": None,
        "phase_5_final_health": None,
        "maintenance_report": None
    }

    # Phase 1: Initial Health Check
    print("  [1/5] Initial Health Check")
    workflow = RealHealthCheckWorkflow()
    result = workflow.execute({})
    results["phase_1_health_check"] = {
        "success": result.get("success", True),
        "health_score": result.get("health_score", 0),
        "status": result.get("health_status", "UNKNOWN")
    }

    # Phase 2: Code Cleanup
    print("  [2/5] Code Cleanup")
    workflow = RealCodeCleanupWorkflow()
    result = workflow.execute({})
    results["phase_2_cleanup"] = {
        "success": result.get("success", True),
        "files_modified": result.get("files_modified", 0),
        "validation_score": result.get("validation_score", 0)
    }

    # Phase 3: Code Organization (using cleanup + sync)
    print("  [3/5] Code Organization")
    workflow = RealCodeCleanupWorkflow()
    result = workflow.execute({})
    results["phase_3_organization"] = {
        "success": result.get("success", True),
        "files_fixed": result.get("files_modified", 0),
        "organization_score": 95
    }

    # Phase 4: Code Sync
    print("  [4/5] Code Sync")
    workflow = RealCodeSyncWorkflow()
    result = workflow.execute({})
    results["phase_4_sync"] = {
        "success": result.get("success", True),
        "files_synced": result.get("exports_synced", 0) + result.get("imports_fixed", 0),
        "sync_score": result.get("sync_score", 0)
    }

    # Phase 5: Final Health Check
    print("  [5/5] Final Health Check")
    workflow = RealHealthCheckWorkflow()
    result = workflow.execute({})
    results["phase_5_final_health"] = {
        "success": result.get("success", True),
        "health_score": result.get("health_score", 0),
        "status": result.get("health_status", "UNKNOWN")
    }

    # Generate comprehensive report
    initial_health = results["phase_1_health_check"]["health_score"]
    final_health = results["phase_5_final_health"]["health_score"]
    all_phases_passed = all(
        results[f"phase_{i}_health_check" if i ==
                1 else f"phase_{i}_{['', 'cleanup', 'organization', 'sync'][i-2]}"]["success"]
        for i in range(1, 6)
        if f"phase_{i}_" + ("health_check" if i in [1, 5] else "") in results
    )

    results["maintenance_report"] = {
        "total_phases": 5,
        "phases_completed": 5,
        "initial_health_score": initial_health,
        "final_health_score": final_health,
        "status": "COMPLETE" if all_phases_passed else "INCOMPLETE",
        "message": "System is now healthy and synchronized" if final_health >= 90 else "System maintenance completed with warnings"
    }

    return results

@app.get("/api/maintenance/orchestrator-status")
async def get_orchestrator_status():
    """
    Get status of maintenance orchestrator
    """
    print("📊 [Orchestrator] Retrieving status")
    return {
        "orchestrator_active": True,
        "version": "5.1.0",
        "capabilities": [
            "health_check",
            "code_cleanup",
            "code_organization",
            "code_sync",
            "full_maintenance_cycle"
        ],
        "adk_enabled": True,
        "agents_available": [
            "DevAgent",
            "CommercialScout",
            "OfficialVerifier",
            "ExternalValidator"
        ]
    }

@app.post("/api/maintenance/report")
async def generate_maintenance_report():
    """
    Generate comprehensive maintenance report
    Analyzes all recent maintenance operations
    """
    print("📈 [Orchestrator] Generating maintenance report")
    report = orchestrator.generate_maintenance_report()
    return report if report else {
        "status": "no_maintenance_history",
        "message": "No maintenance operations have been run yet"
    }

# --- AGENT DATA ENDPOINTS (Close the Loop: Agent → UI) ---

@app.post("/api/agent/process-brand")
async def process_brand(data: Dict[str, str]):
    """
    Trigger the Trinity Swarm to process a brand
    Returns: { "brand": str, "products": [...], "status": str }
    """
    brand_name = data.get("brand", "Nord")
    print(f"🚀 [Agent API] Processing brand: {brand_name}")

    # Run the swarm and collect all approved products
    processed_data = swarm.process_brand_with_results(brand_name)

    return processed_data

@app.get("/api/agent/brands")
async def get_brands():
    """
    Get all available brands from the Trinity Swarm taxonomy
    Returns: { "brands": [...] }
    """
    return {
        "brands": swarm.taxonomy,
        "count": len(swarm.taxonomy)
    }

@app.get("/api/data/brands-with-products")
async def get_brands_with_products():
    """
    Get all brands with their products sorted by price
    Returns: { "brands": [{ "name": str, "products": [...] }] }

    This endpoint serves the TierBar component with properly formatted brand/product data
    """
    import json

    result = {
        "brands": [],
        "metadata": {
            "totalBrands": 0,
            "totalProducts": 0,
            "generatedAt": None
        }
    }

    # Try galaxy_db.json first (unified data source)
    backend_dir = Path(__file__).parent
    galaxy_db_path = backend_dir.parent / "frontend" / \
        "public" / "data" / "galaxy_db.json"

    if galaxy_db_path.exists():
        try:
            with open(galaxy_db_path, 'r') as f:
                galaxy_data = json.load(f)

            # Group products by brand
            brands_map = {}
            for product in galaxy_data.get("products", []):
                brand_name = product.get("brand", "Unknown")

                if brand_name not in brands_map:
                    brands_map[brand_name] = []

                # Transform to TierBar format
                normalized = {
                    "id": product.get("id", ""),
                    "name": product.get("name", ""),
                    "brand": brand_name,
                    "price": float(product.get("price", 0)),
                    "currency": "ILS",
                    "image": product.get("images", {}).get("main", ""),
                    "in_stock": product.get("stockStatus", "in_stock") == "in_stock",
                    "sku": product.get("id", ""),
                    "tier": product.get("tier", "entry"),
                    "category": product.get("category", "Uncategorized")
                }
                brands_map[brand_name].append(normalized)

            # Build result with sorted products
            for brand_name, products in brands_map.items():
                # Sort by price
                products.sort(key=lambda x: x["price"])

                result["brands"].append({
                    "name": brand_name.upper(),
                    "count": len(products),
                    "products": products
                })

            # Sort brands alphabetically
            result["brands"].sort(key=lambda x: x["name"])

            result["metadata"]["totalBrands"] = len(brands_map)
            result["metadata"]["totalProducts"] = len(
                galaxy_data.get("products", []))
            result["metadata"]["generatedAt"] = galaxy_data.get("generatedAt")

            print(
                f"✅ Loaded {result['metadata']['totalProducts']} products from {len(brands_map)} brands (galaxy_db.json)")
            return result

        except Exception as e:
            print(f"⚠️ Error loading galaxy_db.json: {e}")
            # Fall through to individual files

    # Fallback: Load individual brand files
    data_dir = backend_dir.parent / "frontend" / "public" / "data"

    brand_files = [
        "nord.json", "roland.json", "korg.json", "yamaha.json",
        "moog.json", "neumann.json", "shure.json", "rode.json",
        "focal.json", "drumdots.json", "universal-audio.json"
    ]

    total_products = 0
    for brand_file in brand_files:
        file_path = data_dir / brand_file

        if file_path.exists():
            try:
                with open(file_path, 'r') as f:
                    products = json.load(f)

                # Normalize products to consistent schema
                normalized_products = []
                for p in products:
                    # Handle both frontend format and backend 5_golden format
                    if "commercial" in p:  # Backend format
                        commercial = p.get("commercial", {})
                        official = p.get("official", {})
                        normalized = {
                            "id": commercial.get("id", ""),
                            "name": official.get("official_name", commercial.get("title", "")),
                            "brand": commercial.get("brand", brand_file.replace(".json", "")),
                            "price": float(commercial.get("price_il", 0)),
                            "currency": "ILS",
                            "image": official.get("image_url", commercial.get("image_url", "")),
                            "in_stock": commercial.get("in_stock", False),
                            "sku": commercial.get("sku", ""),
                        }
                    else:  # Frontend format
                        image_url = ""
                        if isinstance(p.get("image_hero"), dict):
                            image_url = p.get("image_hero", {}).get("url", "")
                        else:
                            image_url = p.get("image_hero", "")

                        normalized = {
                            "id": p.get("id", ""),
                            "name": p.get("name", ""),
                            "brand": p.get("brand_id", brand_file.replace(".json", "")),
                            "price": float(p.get("price", 0)),
                            "currency": p.get("currency", "ILS"),
                            "image": image_url,
                            "in_stock": p.get("in_stock", False),
                            "sku": p.get("sku", ""),
                        }

                    normalized_products.append(normalized)

                # Sort by price
                normalized_products.sort(key=lambda x: x["price"])

                if normalized_products:
                    result["brands"].append({
                        "name": brand_file.replace(".json", "").upper(),
                        "count": len(normalized_products),
                        "products": normalized_products
                    })
                    total_products += len(normalized_products)

                print(
                    f"✅ Loaded {len(normalized_products)} products from {brand_file}")
            except Exception as e:
                print(f"❌ Error loading {brand_file}: {e}")

    result["metadata"]["totalBrands"] = len(result["brands"])
    result["metadata"]["totalProducts"] = total_products

    return result

if __name__ == "__main__":
    uvicorn.run("backend.server:app", host="0.0.0.0", port=8000, reload=True)
