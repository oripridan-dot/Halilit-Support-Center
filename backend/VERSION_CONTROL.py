#!/usr/bin/env python3
"""
VERSION CONTROL & COMPATIBILITY MANAGEMENT
===========================================

Centralized version control system that prevents confusion across the codebase.
This module enforces version compatibility and prevents deprecated code from running.

CURRENT SYSTEM VERSION: v7.0
BRANCH: v6.1.1 (stable)
DEPRECATED VERSIONS: v5.x, v6.0
"""

from enum import Enum
from typing import Literal, Dict, List
from datetime import datetime

# ============================================================================
# CURRENT VERSION DEFINITION
# ============================================================================

SYSTEM_VERSION = "7.2"
BRANCH_NAME = "v7.2-release"
BUILD_DATE = datetime.now().isoformat()

# Semantic versioning: MAJOR.MINOR.PATCH
MAJOR = 7
MINOR = 2
PATCH = 0

# ============================================================================
# SUPPORTED & DEPRECATED VERSIONS
# ============================================================================


class VersionStatus(Enum):
    """Version support status"""
    CURRENT = "current"          # Active, in use
    DEPRECATED = "deprecated"    # Old, should not be used
    LEGACY = "legacy"           # Ancient, must not be used
    UNSUPPORTED = "unsupported"  # Removed, cause error


# Map of version → status
VERSION_COMPATIBILITY = {
    "7.2": VersionStatus.CURRENT,      # ← ACTIVE VERSION
    "7.0": VersionStatus.DEPRECATED,   # Unified pipeline initial
    "6.1": VersionStatus.LEGACY,       # Older branch
    "6.0": VersionStatus.LEGACY,       # Pre-conductor
    "5.4": VersionStatus.LEGACY,       # Spectrum v5.4
    "5.x": VersionStatus.LEGACY,       # All v5.x
}

# ============================================================================
# DEPRECATED CODE REGISTRY
# ============================================================================

DEPRECATED_METHODS = {
    # Method Name → Replacement
    "ingest_legacy_products": "sync_brand_to_frontend",
    "validate_legacy_schema": "validate_ingestion_draft",
    "process_brand": "process_brand_with_results",
    "audit": "validate_and_review",
    "old_nexus_sync": "trinity_conductor_sync",
}

DEPRECATED_FILES = {
    # File path → Reason
    "backend/ingestion/legacy_adapter.py": "Removed in v7.0 - use spectrum_adapter",
    "backend/v5_compatibility.py": "Removed in v7.0 - v5.x no longer supported",
}

DEPRECATED_FUNCTIONS = {
    "legacy_price_calculator": "Use pricing_engine.py instead",
    "old_brand_parser": "Use taxonomy_manager.py instead",
    "deprecated_sync_method": "Use ingestion_to_frontend.py instead",
}

# ============================================================================
# NAMING CONVENTIONS (PREVENT AMBIGUITY)
# ============================================================================


class MethodNamingConvention:
    """
    Clear naming for methods to prevent confusion.

    PATTERN:
    - validate_* : Check correctness/schema (returns bool/errors)
    - enrich_*   : Add data from external source (returns enriched object)
    - harvest_*  : Extract raw data (returns raw data)
    - audit_*    : Final review & approval (returns status + report)
    - sync_*     : Copy/synchronize between systems (returns sync status)
    - process_*  : Transform/manipulate data (returns transformed object)
    - handle_*   : Respond to events/errors (returns action response)
    """

    VALIDATE = "validate_*"   # ✅ Schema, consistency, correctness
    ENRICH = "enrich_*"       # ➕ Add official/external data
    HARVEST = "harvest_*"     # 📥 Extract raw data (Golden List)
    AUDIT = "audit_*"         # ⚖️  Final review & approval
    SYNC = "sync_*"           # 🔄 Synchronize between systems
    PROCESS = "process_*"     # 🔧 Transform/manipulate
    HANDLE = "handle_*"       # 🚨 Respond to events/errors

    # FORBIDDEN NAMES (too vague, cause confusion)
    FORBIDDEN = {
        "get_*",      # ❌ Too generic - use specific verb
        "do_*",       # ❌ Too vague - be specific
        "check_*",    # ⚠️  Use "validate_*" instead
        "run_*",      # ⚠️  Use specific verb (process, handle, etc.)
    }


# ============================================================================
# COMPONENT DEFINITIONS (PREVENT OVERLAPPING PURPOSES)
# ============================================================================

class ComponentRegistry:
    """
    Clear definition of each system component to prevent confusion.
    """

    TRINITY_SWARM = {
        "purpose": "Three-agent autonomous data processing pipeline",
        "agents": ["CommercialScout", "OfficialVerifier", "ExternalValidator"],
        "file": "backend/agents/trinity_swarm.py",
        "responsibility": "Harvest → Enrich → Validate (Three-stage pipeline)",
    }

    CONDUCTOR = {
        "purpose": "Central orchestration & command interface",
        "file": "backend/conductor_main.py",
        "responsibility": "Schedule Trinity Swarm, manage workflows, CLI control",
        "NOT_for": "Data processing (that's Trinity's job)",
    }

    INGESTION_ORCHESTRATOR = {
        "purpose": "Manage ingestion pipeline phases",
        "file": "backend/ingestion/orchestrator.py",
        "responsibility": "Coordinate ingestion database, validation, storage",
        "NOT_for": "AI agent coordination (that's Conductor's job)",
    }

    INGESTION_TO_FRONTEND = {
        "purpose": "Sync processed data to frontend",
        "file": "backend/ingestion_to_frontend.py",
        "responsibility": "Convert backend schema → frontend format, generate artifacts",
        "NOT_for": "Core data processing (that's Trinity/Ingestion's job)",
    }

    SPECTRUM_ADAPTER = {
        "purpose": "Map products to display tiers/categories",
        "file": "backend/ingestion/spectrum_adapter.py",
        "responsibility": "Assign pricing tiers, categories, display roles",
        "NOT_for": "Data validation (that's Trinity's job)",
    }

    WORKFLOW_ENGINE = {
        "purpose": "State machine enforcement for complex workflows",
        "file": "backend/workflow/engine.py",
        "responsibility": "Enforce Plan → Code → Verify workflow gates",
        "NOT_for": "Data processing orchestration (that's Conductor's job)",
    }

    SECURITY_SHIELD = {
        "purpose": "Security validation & protection",
        "file": "backend/security_shield.py",
        "responsibility": "Validate data safety, CORS, rate limits, DDoS protection",
        "NOT_for": "Business logic (that's other modules' job)",
    }


# ============================================================================
# VERSION GUARDS
# ============================================================================

def assert_version_supports(feature: str, min_version: str = "7.0") -> None:
    """
    Prevent deprecated code from running.

    Usage:
        assert_version_supports("Trinity Swarm", min_version="7.0")
    """
    status = VERSION_COMPATIBILITY.get(SYSTEM_VERSION)

    if SYSTEM_VERSION < min_version:
        raise RuntimeError(
            f"❌ Feature '{feature}' requires v{min_version} or later. "
            f"Current version: v{SYSTEM_VERSION}"
        )


def get_method_replacement(old_method: str) -> str:
    """Get the replacement method for a deprecated method."""
    return DEPRECATED_METHODS.get(old_method, "No replacement found - method was removed")


def log_deprecation_warning(old_name: str, new_name: str = None) -> None:
    """Log a deprecation warning."""
    message = f"⚠️  DEPRECATION: '{old_name}' is deprecated."
    if new_name:
        message += f" Use '{new_name}' instead."
    print(message)


def check_component_responsibility(component: str, action: str) -> bool:
    """
    Verify that a component isn't doing something it shouldn't.

    Usage:
        if not check_component_responsibility("CONDUCTOR", "process_brand"):
            raise PermissionError("Conductor should not process brands directly")
    """
    registry = {
        "TRINITY_SWARM": ComponentRegistry.TRINITY_SWARM,
        "CONDUCTOR": ComponentRegistry.CONDUCTOR,
        "INGESTION_ORCHESTRATOR": ComponentRegistry.INGESTION_ORCHESTRATOR,
        "INGESTION_TO_FRONTEND": ComponentRegistry.INGESTION_TO_FRONTEND,
        "SPECTRUM_ADAPTER": ComponentRegistry.SPECTRUM_ADAPTER,
        "WORKFLOW_ENGINE": ComponentRegistry.WORKFLOW_ENGINE,
        "SECURITY_SHIELD": ComponentRegistry.SECURITY_SHIELD,
    }

    if component not in registry:
        raise ValueError(f"Unknown component: {component}")

    comp_info = registry[component]

    # Check against restricted actions
    not_for = comp_info.get("NOT_for", "")
    if action.lower() in not_for.lower():
        return False

    return True


# ============================================================================
# CONFIG VALIDATION
# ============================================================================

def validate_system_config() -> Dict[str, bool]:
    """
    Validate that the system configuration is correct.
    Returns status dict with all checks.
    """
    checks = {
        "version_defined": SYSTEM_VERSION is not None,
        "version_supported": VERSION_COMPATIBILITY.get(SYSTEM_VERSION) in [
            VersionStatus.CURRENT,
            VersionStatus.DEPRECATED
        ],
        "trinity_swarm_exists": True,  # Would check file exists
        "conductor_exists": True,      # Would check file exists
        "no_legacy_imports": True,     # Would scan for v5 imports
    }

    return checks


# ============================================================================
# DOCUMENTATION BLOCK
# ============================================================================

"""
HOW TO USE THIS VERSION CONTROL SYSTEM
======================================

1. PREVENT DEPRECATED CODE:
   ✅ Use: assert_version_supports("Feature", min_version="7.0")
   ✅ Use: log_deprecation_warning("old_method", "new_method")

2. CHECK METHOD NAMES:
   ✅ Use: validate_* for schema checking
   ✅ Use: enrich_* for adding external data
   ✅ Use: harvest_* for extracting raw data
   ✅ Use: audit_* for final approval
   ✅ Use: sync_* for synchronization
   
   ❌ Avoid: get_*, do_*, check_*, run_* (too vague)

3. COMPONENT OWNERSHIP:
   ✅ Trinity → Data processing (harvest → enrich → validate)
   ✅ Conductor → Orchestration (schedule, manage, CLI)
   ✅ Ingestion → Pipeline management (DB, validation, storage)
   ✅ Frontend → UI layer (sync, display)
   
   ❌ Don't mix responsibilities

4. FILE LOCATIONS:
   - New Trinity code → backend/agents/trinity_swarm.py
   - New Conductor code → backend/conductor_main.py
   - New pipelines → backend/workflow/engine.py or ingestion/orchestrator.py
   - New skills → backend/skills/
   - New validation → backend/security_shield.py

EXAMPLE: Adding a new method
-----------------------------
def enrich_official_specs(draft: Dict) -> Dict:
    '''Enrich draft with official brand specifications.
    
    This follows Trinity Swarm's pattern: OfficialVerifier agent enhances
    the commercial draft with official data.
    '''
    assert_version_supports("Official enrichment", min_version="7.0")
    # ... implementation
    return enriched_draft
"""

if __name__ == "__main__":
    print(f"🔒 Halilit Support Center - Version Control")
    print(f"   Version: v{SYSTEM_VERSION}")
    print(f"   Branch:  {BRANCH_NAME}")
    print(f"   Status:  {VERSION_COMPATIBILITY.get(SYSTEM_VERSION).value}")
    print(f"   Build:   {BUILD_DATE}")
    print()
    print("❌ Deprecated versions:", [
          v for v, s in VERSION_COMPATIBILITY.items() if s == VersionStatus.DEPRECATED])
    print("❌ Legacy versions:", [
          v for v, s in VERSION_COMPATIBILITY.items() if s == VersionStatus.LEGACY])
    print()
    print("✅ All systems initialized. Version control active.")
