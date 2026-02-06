# Developer Standards & Conductor Clarity Framework

**Version**: v7.0  
**Branch**: v6.1.1 (stable)  
**Last Updated**: February 6, 2026

---

## Overview

This document defines clear standards for:

- **Version Management**: Which code is current, deprecated, or legacy
- **Naming Conventions**: Method/function naming to prevent confusion
- **Component Ownership**: What each system is responsible for
- **Code Organization**: Where code lives and why
- **Deprecation Policy**: How to handle old code

---

## Part 1: System Version Control

### Current Version

```
MAJOR: 7
MINOR: 0
PATCH: 0
VERSION: 7.0
BRANCH: v6.1.1 (stable)
```

### Version Timeline

| Version | Status         | Use            | Notes                          |
| ------- | -------------- | -------------- | ------------------------------ |
| **7.0** | ✅ **CURRENT** | **USE THIS**   | Active, production-ready       |
| 6.1     | ⚠️ Deprecated  | Avoid          | Old branch, superseded by v7.0 |
| 6.0     | ❌ Legacy      | **DO NOT USE** | Pre-conductor, removed         |
| 5.4     | ❌ Legacy      | **DO NOT USE** | Ancient Spectrum version       |
| 5.x     | ❌ Legacy      | **DO NOT USE** | Removed entirely               |

### How to Require a Minimum Version

```python
from backend.VERSION_CONTROL import assert_version_supports

# Prevent deprecated code from running
assert_version_supports("Trinity Swarm", min_version="7.0")
```

---

## Part 2: Naming Conventions (Prevent Ambiguity)

### Method Naming Patterns

Use these patterns to make function purpose IMMEDIATELY CLEAR:

| Pattern      | Purpose                  | Returns                | Example                   |
| ------------ | ------------------------ | ---------------------- | ------------------------- |
| `validate_*` | Check correctness/schema | `bool`, list of errors | `validate_pricing()`      |
| `enrich_*`   | Add external data        | Enriched object        | `enrich_official_specs()` |
| `harvest_*`  | Extract raw data         | Raw data               | `harvest_products()`      |
| `audit_*`    | Final review & approval  | Status + Report        | `audit_product()`         |
| `sync_*`     | Synchronize systems      | Sync status            | `sync_to_frontend()`      |
| `process_*`  | Transform/manipulate     | Transformed data       | `process_brand()`         |
| `handle_*`   | Respond to events        | Action response        | `handle_error()`          |

### ❌ FORBIDDEN Names (Too Vague)

| Name        | Why Ambiguous       | Use Instead                                |
| ----------- | ------------------- | ------------------------------------------ |
| `get_*`     | Too generic         | Use specific verb (`harvest_`, `extract_`) |
| `do_*`      | Too vague           | Use specific verb (`process_`, `handle_`)  |
| `check_*`   | Unclear intent      | Use `validate_`                            |
| `run_*`     | Could mean anything | Use specific verb                          |
| `execute_*` | Too generic         | Use specific verb or `handle_`             |

### Example: Clear Naming

```python
# ✅ GOOD - Purpose is immediately clear
def harvest_products(url: str) -> List[Dict]:
    """Extract raw products from Halilit.com"""

def enrich_official_specs(draft: Dict) -> Dict:
    """Add official specs from brand website"""

def audit_quality_score(product: Dict) -> QualityReport:
    """Perform final quality review and approval"""

# ❌ BAD - Unclear what these do
def get_data(source):            # What data? Where from?
def do_processing(input):        # Process how? What does it do?
def check_something(x):          # Check what exactly?
def run_validation(product):     # Validate what? How?
```

---

## Part 3: Component Registry (Prevent Overlap)

### Clear Component Responsibilities

Each component has **ONE** clear purpose. Do not mix responsibilities.

#### 1. **Trinity Swarm** (Data Processing)

- **File**: `backend/agents/trinity_swarm.py`
- **Purpose**: Three-agent autonomous pipeline
- **Agents**:
  - `CommercialScout` → **Harvest** raw data from Halilit
  - `OfficialVerifier` → **Enrich** with official specs
  - `ExternalValidator` → **Audit** & approve
- **Returns**: Validated products ready for frontend
- **❌ NOT responsible for**: Orchestration, scheduling, workflow management

#### 2. **Google Conductor** (Orchestration)

- **File**: `backend/conductor_main.py`
- **Purpose**: Central command & scheduling
- **Responsibilities**:
  - Schedule Trinity Swarm agents
  - CLI interface (`conductor_main.py ingest`, `sync`, `build`, etc.)
  - Coordinate all system operations
  - Version checking & validation gates
- **❌ NOT responsible for**: Data processing (Trinity's job)

#### 3. **Ingestion Orchestrator** (Pipeline Management)

- **File**: `backend/ingestion/orchestrator.py`
- **Purpose**: Manage ingestion pipeline phases
- **Responsibilities**:
  - Coordinate ingestion database
  - Manage validation batches
  - Store approved products
  - Run pipeline phases (harvest → enrich → validate)
- **❌ NOT responsible for**: AI agent coordination (Conductor's job)

#### 4. **Ingestion → Frontend Sync**

- **File**: `backend/ingestion_to_frontend.py`
- **Purpose**: Sync processed data to frontend
- **Responsibilities**:
  - Convert backend schema → frontend schema
  - Generate search indexes
  - Create category shards
  - Generate galaxy_db.json
- **❌ NOT responsible for**: Core data processing (Trinity's job)

#### 5. **Spectrum Adapter** (Display Mapping)

- **File**: `backend/ingestion/spectrum_adapter.py`
- **Purpose**: Map products to display tiers/categories
- **Responsibilities**:
  - Assign pricing tiers (entry, mid, pro, flagship)
  - Assign categories
  - Map display roles
  - Calculate relevance scores
- **❌ NOT responsible for**: Data validation (Trinity's job)

#### 6. **Workflow Engine** (State Machines)

- **File**: `backend/workflow/engine.py`
- **Purpose**: Enforce complex workflow gates
- **Responsibilities**:
  - Plan → Code → Verify cycle
  - Feature build workflows
  - State machine enforcement
- **❌ NOT responsible for**: Data pipeline management

#### 7. **Security Shield** (Protection)

- **File**: `backend/security_shield.py`
- **Purpose**: Security validation & protection
- **Responsibilities**:
  - CORS management
  - Rate limiting
  - DDoS protection
  - Data safety validation
- **❌ NOT responsible for**: Business logic

---

## Part 4: Code Organization

### File Locations and Meanings

```
backend/
├── VERSION_CONTROL.py          ← Version management (current v7.0)
├── conductor_main.py           ← Orchestration & CLI (v7.0)
├── server.py                   ← FastAPI bridge
│
├── agents/
│   ├── trinity_swarm.py        ← Trinity Swarm (v7.0+, CURRENT)
│   ├── agent_memory.py         ← Learning capabilities
│   ├── agent_workflows.py      ← Workflow definitions
│   ├── dev_agent.py            ← Development helper
│   └── maintenance_orchestrator.py ← System maintenance
│
├── ingestion/
│   ├── orchestrator.py         ← Pipeline management (v7.0+)
│   ├── data_models.py          ← Pydantic schemas
│   ├── spectrum_adapter.py     ← Display tier mapping
│   ├── pricing_engine.py       ← Pricing strategy
│   ├── taxonomy_manager.py     ← Category classification
│   ├── guardrails.py           ← Data quality rules
│   └── trinity_integration.py  ← Trinity ↔ Ingestion bridge
│
├── workflow/
│   └── engine.py               ← State machine workflows
│
├── skills/
│   ├── base_skill.py           ← Skill interface
│   └── frontend_builder.py     ← Safe component builder
│
└── security_shield.py          ← Security validation & protection
```

### What Goes Where?

**Trinity Swarm Code**:

- Add to `backend/agents/trinity_swarm.py`
- Must follow naming conventions
- Must have version guards

**New orchestration**:

- Add to `backend/conductor_main.py`
- Must use Conductor pattern
- Must call Trinity, not process directly

**New pipeline steps**:

- Add to `backend/ingestion/orchestrator.py`
- Must coordinate with Trinity
- Must follow harvest → enrich → validate pattern

**New skills**:

- Add to `backend/skills/`
- Must inherit from `BaseSkill`
- Must verify before executing

**New validation**:

- Add to `backend/security_shield.py`
- Must prevent invalid data
- Must log violations

---

## Part 5: Deprecation Policy

### How to Mark Code as Deprecated

```python
from backend.VERSION_CONTROL import log_deprecation_warning

def old_method():
    """
    ❌ DEPRECATED - DO NOT USE

    This method is deprecated since v7.0.
    REPLACEMENT: Use new_method() instead.
    REMOVAL DATE: v8.0
    """
    log_deprecation_warning("old_method", "new_method")
    # ... still works but warns
```

### Deprecation Timeline

1. **First Release**: Mark as deprecated (❌)
2. **Next Major Version**: Still works but warns (⚠️)
3. **Following Major Version**: Remove entirely

---

## Part 6: Testing Confusion Prevention

### Before Committing Code

```python
from backend.VERSION_CONTROL import (
    MethodNamingConvention,
    check_component_responsibility,
    validate_system_config
)

# ✅ Check naming conventions
if method_name not in MethodNamingConvention.FORBIDDEN:
    print("✅ Method naming is good")

# ✅ Check component responsibilities
if check_component_responsibility("TRINITY_SWARM", "process_brands"):
    print("✅ Component is not overreaching")

# ✅ Validate system config
checks = validate_system_config()
if all(checks.values()):
    print("✅ System configuration is valid")
```

---

## Part 7: Quick Reference for Developers

### "Where do I add...?"

| Task              | Location                        | Pattern                                              |
| ----------------- | ------------------------------- | ---------------------------------------------------- |
| New agent logic   | `agents/trinity_swarm.py`       | `def harvest_*()`, `def enrich_*()`, `def audit_*()` |
| New orchestration | `conductor_main.py`             | Check Trinity ↔ Conductor pattern                    |
| New pipeline      | `ingestion/orchestrator.py`     | Follow harvest → enrich → validate                   |
| New display logic | `ingestion/spectrum_adapter.py` | Map products to tiers/categories                     |
| New validation    | `security_shield.py`            | Use `validate_*()`                                   |
| New workflow      | `workflow/engine.py`            | Define state machine                                 |
| New skill         | `skills/`                       | Inherit `BaseSkill`, implement `validate_context()`  |

### "How do I..."?

| Question           | Answer                                                  |
| ------------------ | ------------------------------------------------------- |
| Require v7.0?      | `assert_version_supports("Feature", min_version="7.0")` |
| Mark deprecated?   | Add `❌ DEPRECATED` doc + `log_deprecation_warning()`   |
| Check naming?      | Use patterns from Part 2 (validate*\*, enrich*\*, etc.) |
| Prevent confusion? | Check ComponentRegistry in VERSION_CONTROL.py           |
| Add new agent?     | Create in trinity_swarm.py, inherit AgentBase           |

---

## Part 8: Version Control Commands

```bash
# Check system version
python3 -c "from backend.VERSION_CONTROL import SYSTEM_VERSION; print(f'Current: v{SYSTEM_VERSION}')"

# Validate all checks
python3 backend/VERSION_CONTROL.py

# Find deprecated code
grep -r "❌ DEPRECATED" backend --include="*.py"

# Find ambiguous method names
grep -r "def get_\|def do_\|def check_\|def run_" backend --include="*.py"
```

---

## Summary

✅ **Follow this framework to prevent confusion**:

1. **Know the version**: v7.0 is current
2. **Use clear names**: `validate_*`, `harvest_*`, `enrich_*`, `audit_*`, `sync_*`
3. **Avoid ambiguity**: Don't use `get_*`, `do_*`, `check_*`, `run_*`
4. **Respect ownership**: Trinity processes, Conductor orchestrates
5. **Mark deprecated**: Use `❌ DEPRECATED` + replacement
6. **Version guard**: Use `assert_version_supports()`
7. **Test clarity**: Run `python3 backend/VERSION_CONTROL.py`

---

**Questions?** Refer to [`backend/VERSION_CONTROL.py`](VERSION_CONTROL.py) or this document.  
**Version**: v7.0  
**Last Review**: February 6, 2026
