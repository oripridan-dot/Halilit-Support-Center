## [v4.1] — 2026-02-20
- [feat] Added Catalog Explorer view.
- [feat] Added Telescope icon for Explorer navigation.
- [feat] Added navigation to Explorer view.
- [feat] Added Explorer view to the navigation sidebar.
- [fix] Fixed error handling in EcosystemTab component.
- [feat] Added ImageWithFallback component.
- [refactor] Replaced direct image tags in EcosystemTab with ImageWithFallback component for improved error handling.
- [feat] Added a new navigation item for Explorer view.
- [feat] Added handling for Explorer view in navigation store.
- [feat] Added resilient extraction using API-first and Gemini semantic fallback in `halilit_page_scraper_async.py`.
- [feat] Added holographic spec hydration engine.
- [feat] Added YAML frontmatter parsing.
- [refactor] Updated `build_component` to use the hydration engine.
- [feat] Added Catalog Explorer view.
- [feat] Added Telescope icon for Explorer navigation.
- [feat] Added navigation to Explorer view.
- [feat] Added Explorer view to the navigation sidebar.
- [feat] Added new contract `product_detail_-_accessory_recommendations.schema.ts`.
- [feat] Added new interface spec `product_detail_-_accessory_recommendations.md`.

## [v4.1] — 2026-02-20
## v4.1

- [feat] Added Catalog Explorer view.
- [feat] Added Telescope icon for Explorer navigation.
- [feat] Added navigation to Explorer view.
- [feat] Added Explorer view to the navigation sidebar.
- [fix] Fixed error handling in EcosystemTab component.
- [feat] Added ImageWithFallback component.
- [refactor] Replaced direct image tags in EcosystemTab with ImageWithFallback component for improved error handling.
- [feat] Added a new navigation item for Explorer view.
- [feat] Added handling for Explorer view in navigation store.
- [feat] Added resilient extraction using API-first and Gemini semantic fallback in `halilit_page_scraper_async.py`.
- [feat] Added holographic spec hydration engine.
- [feat] Added YAML frontmatter parsing.
- [refactor] Updated `build_component` to use the hydration engine.

## [v4.1] — 2026-02-20
## v4.1

- [feat] Added Catalog Explorer view.
- [feat] Added Telescope icon for Explorer navigation.
- [feat] Added navigation to Explorer view.
- [feat] Added Explorer view to the navigation sidebar.
- [fix] Fixed error handling in EcosystemTab component.
- [feat] Added ImageWithFallback component.
- [refactor] Replaced direct image tags in EcosystemTab with ImageWithFallback component for improved error handling.
- [feat] Added a new navigation item for Explorer view.
- [feat] Added handling for Explorer view in navigation store.
- [feat] Added resilient extraction using API-first and Gemini semantic fallback in `halilit_page_scraper_async.py`.

## [v4.1] — 2026-02-20
- [feat] Added Catalog Explorer view.
- [feat] Added Telescope icon for Explorer navigation.
- [feat] Added navigation to Explorer view.
- [feat] Added Explorer view to the navigation sidebar.
- [fix] Fixed error handling in EcosystemTab component.
- [feat] Added ImageWithFallback component.
- [refactor] Replaced direct image tags in EcosystemTab with ImageWithFallback component for improved error handling.
- [feat] Added a new navigation item for Explorer view.
- [feat] Added handling for Explorer view in navigation store.

## [v4.1] — 2026-02-20
## [v4.1]

- [feat] Added `get_relevant_lore` function to `agent_core.py` using vector memory.
- [feat] Implemented embedding and cosine similarity for finding relevant lessons from `LEARNED_GUIDELINES.md`.
- [fix] Improved fallback to full text read if embedding API is unavailable in `get_relevant_lore`.
- [chore] Formatted `mcp_servers.json` for readability and set web-search enabled status to true.

## [v4.1] — 2026-02-20
### v4.1

- [feat] Added get_relevant_lore function using vector memory to agent_core.py
- [feat] Added support for embedding and cosine similarity for finding relevant lessons from LEARNED_GUIDELINES.md.
- [fix] Improved graceful fallback to full text read if embedding API is unavailable in get_relevant_lore.
- [chore] Formatted mcp_servers.json for readability and changed web-search enabled status to true.

## [v9.7.1] — 2026-02-20

### Cleanup & Hardening
- [chore] Deleted orphaned root `src/` directory (8 legacy components never wired into build)
- [chore] Removed duplicate `services/catalog_organizer.py` (identical to `backend/catalog_organizer.py`)
- [chore] Removed legacy `start_console.sh` (superseded by `factory.py start`)
- [chore] Removed `backend/scripts/archive/` (3 archived one-off scripts)
- [chore] Deleted 10 duplicate spec files in `specs/interface/` — reduced from 44 to 34 specs
- [fix] Optimizer agent: file-existence pre-flight guard in `nexus.py` blocks hallucinated `optimize` targets
- [fix] Chief agent: anti-hallucination rule in system prompt — `optimize` only on confirmed existing files
- [chore] Bumped `frontend/package.json` 9.6.0 → 9.7.1
- [chore] Updated version strings across README, copilot-instructions, ignite_factory.sh, .version

## [v4.1] — 2026-02-20
## [v4.1]

- [feat] Added `v0_design` tool to `chief_agent.py`.
- [refactor] Updated `cmd_status` in `factory.py`.
- [feat] Added `cmd_v0_design` function to `factory.py`.
- [feat] Added result caching for visual QA.
- [feat] Added caching functions for visual QA.
- [refactor] Added `hashlib`, `json`, and `time` imports to `visual_qa.py`.
- [feat] Added spec file: `specs/interface/global_search_-_prioritize_exact_sku_matches.md`.
- [feat] Global search prioritizes exact SKU matches.
- [refactor] Updated `GlobalSearch.tsx` for efficient search result handling.
- [feat] Added JIT Intelligence integration to ProductDetailView.
- [feat] Added sourcing badges.
- [feat] Used ConductorCatalog for product details.
- [refactor] Updated imports in ProductDetailView.tsx.
- [feat] Added useRef to ProductDetailView.tsx.
- [feat] Added JITPhase and JITIntelligenceState to useJITIntelligence hook.
- [feat] Added useConductorCatalog hook.
- [feat] Added SourcingBadge component.
- [refactor] Updated RelationshipSection to handle product sources.
- [refactor] Updated styling and logic in ProductDetailView.tsx.
- [feat] Added logic to ProductDetailView to display information from conductor catalog.
- [refactor] Added a check to ProductDetailView to prevent calling useProductRelationships if there's no product.
- [refactor] Updated the SYSTEM_PROMPT in `chief_agent.py`.
- [feat] Added a new file `OrganizedCatalog.ts` with type definitions for brand catalog.
- [feat] Added spec for product tile image sourcing badges.
- [refactor] Removed optional Family and Relationship Inference logic in `OrganizedCatalog.ts`.
- [refactor] Return the `OrganizedCatalog` result directly in `OrganizedCatalog.ts`.
- [feat] Added a new API endpoint `/machines/{machine_id}/status` to fetch machine status.
- [feat] Implemented a FastAPI application `halilit_api/machines.py`.
- [feat] Added v0 agent file `backend/factory/v0_agent.py`.
- [refactor] Added a check to ProductDetailView to prevent calling useProductRelationships if there's no product.
- [refactor] Updated SYSTEM_PROMPT in `chief_agent.py`.
- [feat] Added v0 agent file `backend/factory/v0_agent.py`.
- [refactor] Added a check to ProductDetailView to prevent calling useProductRelationships if there's no product.
- [refactor] Updated SYSTEM_PROMPT in `chief_agent.py`.
- [feat] Added v0 agent file `backend/factory/v0_agent.py`.
- [refactor] Added a check to ProductDetailView to prevent calling useProductRelationships if there's no product.
- [refactor] Updated SYSTEM_PROMPT in `chief_agent.py`.
- [refactor] Added a check to ProductDetailView to prevent calling useProductRelationships if there's no product.
- [refactor] Updated SYSTEM_PROMPT in `chief_agent.py`.
- [refactor] Added a check to ProductDetailView to prevent calling useProductRelationships if there's no product.
- [refactor] Updated SYSTEM_PROMPT in `chief_agent.py`.
- [refactor] Added a check to ProductDetailView to prevent calling useProductRelationships if there's no product.
- [refactor] Updated SYSTEM_PROMPT in `chief_agent.py`.
- [refactor] Added a check to ProductDetailView to prevent calling useProductRelationships if there's no product.
- [refactor] Updated SYSTEM_PROMPT in `chief_agent.py`.
- [feat] Added `v0_design` tool to `chief_agent.py`.

## [v4.1] — 2026-02-20
## [v4.1]

- [feat] Added `v0_design` tool to `chief_agent.py`.
- [refactor] Updated `cmd_status` in `factory.py`.
- [feat] Added `cmd_v0_design` function to `factory.py`.
- [feat] Added result caching for visual QA.
- [feat] Added caching functions for visual QA.
- [refactor] Added `hashlib`, `json`, and `time` imports to `visual_qa.py`.
- [feat] Added spec file: `specs/interface/global_search_-_prioritize_exact_sku_matches.md`.
- [feat] Global search prioritizes exact SKU matches.
- [refactor] Updated `GlobalSearch.tsx` for efficient search result handling.
- [feat] Added JIT Intelligence integration to ProductDetailView.
- [feat] Added sourcing badges.
- [feat] Used ConductorCatalog for product details.
- [refactor] Updated imports in ProductDetailView.tsx.
- [feat] Added useRef to ProductDetailView.tsx.
- [feat] Added JITPhase and JITIntelligenceState to useJITIntelligence hook.
- [feat] Added useConductorCatalog hook.
- [feat] Added SourcingBadge component.
- [refactor] Updated RelationshipSection to handle product sources.
- [refactor] Updated styling and logic in ProductDetailView.tsx.
- [feat] Added logic to ProductDetailView to display information from conductor catalog.
- [refactor] Added a check to ProductDetailView to prevent calling useProductRelationships if there's no product.
- [refactor] Updated the SYSTEM_PROMPT in `chief_agent.py`.
- [feat] Added a new file `OrganizedCatalog.ts` with type definitions for brand catalog.
- [feat] Added spec for product tile image sourcing badges.
- [refactor] Removed optional Family and Relationship Inference logic in `OrganizedCatalog.ts`.
- [refactor] Return the `OrganizedCatalog` result directly in `OrganizedCatalog.ts`.
- [feat] Added a new API endpoint `/machines/{machine_id}/status` to fetch machine status.
- [feat] Implemented a FastAPI application `halilit_api/machines.py`.
- [feat] Added v0 agent file `backend/factory/v0_agent.py`.
- [refactor] Added a check to ProductDetailView to prevent calling useProductRelationships if there's no product.
- [refactor] Updated SYSTEM_PROMPT in `chief_agent.py`.
- [feat] Added v0 agent file `backend/factory/v0_agent.py`.
- [refactor] Added a check to ProductDetailView to prevent calling useProductRelationships if there's no product.
- [refactor] Updated SYSTEM_PROMPT in `chief_agent.py`.
- [feat] Added v0 agent file `backend/factory/v0_agent.py`.
- [refactor] Added a check to ProductDetailView to prevent calling useProductRelationships if there's no product.
- [refactor] Updated SYSTEM_PROMPT in `chief_agent.py`.
- [refactor] Added a check to ProductDetailView to prevent calling useProductRelationships if there's no product.
- [refactor] Updated SYSTEM_PROMPT in `chief_agent.py`.
- [refactor] Added a check to ProductDetailView to prevent calling useProductRelationships if there's no product.
- [refactor] Updated SYSTEM_PROMPT in `chief_agent.py`.
- [refactor] Added a check to ProductDetailView to prevent calling useProductRelationships if there's no product.
- [refactor] Updated SYSTEM_PROMPT in `chief_agent.py`.
- [refactor] Added a check to ProductDetailView to prevent calling useProductRelationships if there's no product.
- [refactor] Updated SYSTEM_PROMPT in `chief_agent.py`.
- [feat] Added `v0_design` tool to `chief_agent.py`.

## [v4.1] — 2026-02-20
## v4.1

- [feat] Added `v0_design` tool to `chief_agent.py`.
- [refactor] Updated `cmd_status` in `factory.py`.
- [feat] Added `cmd_v0_design` function to `factory.py`.
- [feat] Added result caching for visual QA.
- [feat] Added caching functions for visual QA.
- [refactor] Added `hashlib`, `json`, and `time` imports to `visual_qa.py`.
- [feat] Added spec file: `specs/interface/global_search_-_prioritize_exact_sku_matches.md`.
- [feat] Global search prioritizes exact SKU matches.
- [refactor] Updated `GlobalSearch.tsx` for efficient search result handling.
- [feat] Added JIT Intelligence integration to ProductDetailView.
- [feat] Added sourcing badges.
- [feat] Used ConductorCatalog for product details.
- [refactor] Updated imports in ProductDetailView.tsx.
- [feat] Added useRef to ProductDetailView.tsx.
- [feat] Added JITPhase and JITIntelligenceState to useJITIntelligence hook.
- [feat] Added useConductorCatalog hook.
- [feat] Added SourcingBadge component.
- [refactor] Updated RelationshipSection to handle product sources.
- [refactor] Updated styling and logic in ProductDetailView.tsx.
- [feat] Added logic to ProductDetailView to display information from conductor catalog.
- [refactor] Added a check to ProductDetailView to prevent calling useProductRelationships if there's no product.
- [refactor] Updated the SYSTEM_PROMPT in `chief_agent.py`.
- [feat] Added a new file `OrganizedCatalog.ts` with type definitions for brand catalog.
- [feat] Added spec for product tile image sourcing badges.
- [refactor] Removed optional Family and Relationship Inference logic in `OrganizedCatalog.ts`.
- [refactor] Return the `OrganizedCatalog` result directly in `OrganizedCatalog.ts`.
- [feat] Added a new API endpoint `/machines/{machine_id}/status` to fetch machine status.
- [feat] Implemented a FastAPI application `halilit_api/machines.py`.
- [feat] Added v0 agent file `backend/factory/v0_agent.py`.
- [refactor] Added a check to ProductDetailView to prevent calling useProductRelationships if there's no product.
- [refactor] Updated SYSTEM_PROMPT in `chief_agent.py`.
- [feat] Added v0 agent file `backend/factory/v0_agent.py`.
- [refactor] Added a check to ProductDetailView to prevent calling useProductRelationships if there's no product.
- [refactor] Updated SYSTEM_PROMPT in `chief_agent.py`.
- [feat] Added v0 agent file `backend/factory/v0_agent.py`.
- [refactor] Added a check to ProductDetailView to prevent calling useProductRelationships if there's no product.
- [refactor] Updated SYSTEM_PROMPT in `chief_agent.py`.
- [refactor] Added a check to ProductDetailView to prevent calling useProductRelationships if there's no product.
- [refactor] Updated SYSTEM_PROMPT in `chief_agent.py`.
- [refactor] Added a check to ProductDetailView to prevent calling useProductRelationships if there's no product.
- [refactor] Updated SYSTEM_PROMPT in `chief_agent.py`.
- [refactor] Added a check to ProductDetailView to prevent calling useProductRelationships if there's no product.
- [refactor] Updated SYSTEM_PROMPT in `chief_agent.py`.
- [refactor] Added a check to ProductDetailView to prevent calling useProductRelationships if there's no product.
- [refactor] Updated SYSTEM_PROMPT in `chief_agent.py`.
- [feat] Added `v0_design` tool to `chief_agent.py`.

## [v4.1] — 2026-02-20
### [v4.1]

- [feat] Added `v0_design` tool to `chief_agent.py`.
- [refactor] Updated `cmd_status` in `factory.py`.
- [feat] Added `cmd_v0_design` function to `factory.py`.
- [feat] Added result caching for visual QA.
- [feat] Added caching functions for visual QA.
- [refactor] Added `hashlib`, `json`, and `time` imports to `visual_qa.py`.
- [feat] Added spec file: `specs/interface/global_search_-_prioritize_exact_sku_matches.md`.
- [feat] Global search prioritizes exact SKU matches.
- [refactor] Updated `GlobalSearch.tsx` for efficient search result handling.
- [feat] Added JIT Intelligence integration to ProductDetailView.
- [feat] Added sourcing badges.
- [feat] Used ConductorCatalog for product details.
- [refactor] Updated imports in ProductDetailView.tsx.
- [feat] Added useRef to ProductDetailView.tsx.
- [feat] Added JITPhase and JITIntelligenceState to useJITIntelligence hook.
- [feat] Added useConductorCatalog hook.
- [feat] Added SourcingBadge component.
- [refactor] Updated RelationshipSection to handle product sources.
- [refactor] Updated styling and logic in ProductDetailView.tsx.
- [feat] Added logic to ProductDetailView to display information from conductor catalog.
- [refactor] Added a check to ProductDetailView to prevent calling useProductRelationships if there's no product.
- [refactor] Updated the SYSTEM_PROMPT in `chief_agent.py`.
- [feat] Added a new file `OrganizedCatalog.ts` with type definitions for brand catalog.
- [feat] Added spec for product tile image sourcing badges.
- [refactor] Removed optional Family and Relationship Inference logic in `OrganizedCatalog.ts`.
- [refactor] Return the `OrganizedCatalog` result directly in `OrganizedCatalog.ts`.
- [feat] Added a new API endpoint `/machines/{machine_id}/status` to fetch machine status.
- [feat] Implemented a FastAPI application `halilit_api/machines.py`.
- [feat] Added v0 agent file `backend/factory/v0_agent.py`.
- [refactor] Added a check to ProductDetailView to prevent calling useProductRelationships if there's no product.
- [refactor] Updated SYSTEM_PROMPT in `chief_agent.py`.
- [feat] Added v0 agent file `backend/factory/v0_agent.py`.
- [refactor] Added a check to ProductDetailView to prevent calling useProductRelationships if there's no product.
- [refactor] Updated SYSTEM_PROMPT in `chief_agent.py`.
- [feat] Added v0 agent file `backend/factory/v0_agent.py`.
- [refactor] Added a check to ProductDetailView to prevent calling useProductRelationships if there's no product.
- [refactor] Updated SYSTEM_PROMPT in `chief_agent.py`.
- [refactor] Added a check to ProductDetailView to prevent calling useProductRelationships if there's no product.
- [refactor] Updated SYSTEM_PROMPT in `chief_agent.py`.
- [refactor] Added a check to ProductDetailView to prevent calling useProductRelationships if there's no product.
- [refactor] Updated SYSTEM_PROMPT in `chief_agent.py`.
- [refactor] Added a check to ProductDetailView to prevent calling useProductRelationships if there's no product.
- [refactor] Updated SYSTEM_PROMPT in `chief_agent.py`.
- [refactor] Added a check to ProductDetailView to prevent calling useProductRelationships if there's no product.
- [refactor] Updated SYSTEM_PROMPT in `chief_agent.py`.
- [feat] Added `v0_design` tool to `chief_agent.py`.

## [v4.1] — 2026-02-20
### v4.1

- [feat] Added `v0_design` tool to `chief_agent.py`.
- [refactor] Updated `cmd_status` in `factory.py`.
- [feat] Added `cmd_v0_design` function to `factory.py`.
- [feat] Added result caching for visual QA.
- [feat] Added caching functions for visual QA.
- [refactor] Added `hashlib`, `json`, and `time` imports to `visual_qa.py`.
- [feat] Added spec file: `specs/interface/global_search_-_prioritize_exact_sku_matches.md`.
- [feat] Global search prioritizes exact SKU matches.
- [refactor] Updated `GlobalSearch.tsx` for efficient search result handling.
- [feat] Added JIT Intelligence integration to ProductDetailView.
- [feat] Added sourcing badges.
- [feat] Used ConductorCatalog for product details.
- [refactor] Updated imports in ProductDetailView.tsx.
- [feat] Added useRef to ProductDetailView.tsx.
- [feat] Added JITPhase and JITIntelligenceState to useJITIntelligence hook.
- [feat] Added useConductorCatalog hook.
- [feat] Added SourcingBadge component.
- [refactor] Updated RelationshipSection to handle product sources.
- [refactor] Updated styling and logic in ProductDetailView.tsx.
- [feat] Added logic to ProductDetailView to display information from conductor catalog.
- [refactor] Added a check to ProductDetailView to prevent calling useProductRelationships if there's no product.
- [refactor] Updated the SYSTEM_PROMPT in `chief_agent.py`.
- [feat] Added a new file `OrganizedCatalog.ts` with type definitions for brand catalog.
- [feat] Added spec for product tile image sourcing badges.
- [refactor] Removed optional Family and Relationship Inference logic in `OrganizedCatalog.ts`.
- [refactor] Return the `OrganizedCatalog` result directly in `OrganizedCatalog.ts`.
- [feat] Added a new API endpoint `/machines/{machine_id}/status` to fetch machine status.
- [feat] Implemented a FastAPI application `halilit_api/machines.py`.
- [feat] Added v0 agent file `backend/factory/v0_agent.py`.
- [refactor] Added a check to ProductDetailView to prevent calling useProductRelationships if there's no product.
- [refactor] Updated SYSTEM_PROMPT in `chief_agent.py`.
- [feat] Added v0 agent file `backend/factory/v0_agent.py`.
- [refactor] Added a check to ProductDetailView to prevent calling useProductRelationships if there's no product.
- [refactor] Updated SYSTEM_PROMPT in `chief_agent.py`.
- [feat] Added v0 agent file `backend/factory/v0_agent.py`.
- [refactor] Added a check to ProductDetailView to prevent calling useProductRelationships if there's no product.
- [refactor] Updated SYSTEM_PROMPT in `chief_agent.py`.
- [refactor] Added a check to ProductDetailView to prevent calling useProductRelationships if there's no product.
- [refactor] Updated SYSTEM_PROMPT in `chief_agent.py`.
- [refactor] Added a check to ProductDetailView to prevent calling useProductRelationships if there's no product.
- [refactor] Updated SYSTEM_PROMPT in `chief_agent.py`.
- [refactor] Added a check to ProductDetailView to prevent calling useProductRelationships if there's no product.
- [refactor] Updated SYSTEM_PROMPT in `chief_agent.py`.
- [refactor] Added a check to ProductDetailView to prevent calling useProductRelationships if there's no product.
- [refactor] Updated SYSTEM_PROMPT in `chief_agent.py`.
- [feat] Added `v0_design` tool to `chief_agent.py`.

## [v4.1] — 2026-02-20
## [v4.1]

- [feat] Added `v0_design` tool to `chief_agent.py`.
- [refactor] Updated `cmd_status` in `factory.py`.
- [feat] Added `cmd_v0_design` function to `factory.py`.
- [feat] Added result caching for visual QA.
- [feat] Added caching functions for visual QA.
- [refactor] Added `hashlib`, `json`, and `time` imports to `visual_qa.py`.
- [feat] Added spec file: `specs/interface/global_search_-_prioritize_exact_sku_matches.md`.
- [feat] Global search prioritizes exact SKU matches.
- [refactor] Updated `GlobalSearch.tsx` for efficient search result handling.
- [feat] Added JIT Intelligence integration to ProductDetailView.
- [feat] Added sourcing badges.
- [feat] Used ConductorCatalog for product details.
- [refactor] Updated imports in ProductDetailView.tsx.
- [feat] Added useRef to ProductDetailView.tsx.
- [feat] Added JITPhase and JITIntelligenceState to useJITIntelligence hook.
- [feat] Added useConductorCatalog hook.
- [feat] Added SourcingBadge component.
- [refactor] Updated RelationshipSection to handle product sources.
- [refactor] Updated styling and logic in ProductDetailView.tsx.
- [feat] Added logic to ProductDetailView to display information from conductor catalog.
- [refactor] Added a check to ProductDetailView to prevent calling useProductRelationships if there's no product.
- [refactor] Updated the SYSTEM_PROMPT in `chief_agent.py`.
- [feat] Added a new file `OrganizedCatalog.ts` with type definitions for brand catalog.
- [feat] Added spec for product tile image sourcing badges.
- [refactor] Removed optional Family and Relationship Inference logic in `OrganizedCatalog.ts`.
- [refactor] Return the `OrganizedCatalog` result directly in `OrganizedCatalog.ts`.
- [feat] Added a new API endpoint `/machines/{machine_id}/status` to fetch machine status.
- [feat] Implemented a FastAPI application `halilit_api/machines.py`.
- [feat] Added v0 agent file `backend/factory/v0_agent.py`.
- [refactor] Added a check to ProductDetailView to prevent calling useProductRelationships if there's no product.
- [refactor] Updated SYSTEM_PROMPT in `chief_agent.py`.
- [feat] Added v0 agent file `backend/factory/v0_agent.py`.
- [refactor] Added a check to ProductDetailView to prevent calling useProductRelationships if there's no product.
- [refactor] Updated SYSTEM_PROMPT in `chief_agent.py`.
- [feat] Added v0 agent file `backend/factory/v0_agent.py`.
- [refactor] Added a check to ProductDetailView to prevent calling useProductRelationships if there's no product.
- [refactor] Updated SYSTEM_PROMPT in `chief_agent.py`.
- [refactor] Added a check to ProductDetailView to prevent calling useProductRelationships if there's no product.
- [refactor] Updated SYSTEM_PROMPT in `chief_agent.py`.
- [refactor] Added a check to ProductDetailView to prevent calling useProductRelationships if there's no product.
- [refactor] Updated SYSTEM_PROMPT in `chief_agent.py`.
- [refactor] Added a check to ProductDetailView to prevent calling useProductRelationships if there's no product.
- [refactor] Updated SYSTEM_PROMPT in `chief_agent.py`.
- [refactor] Added a check to ProductDetailView to prevent calling useProductRelationships if there's no product.
- [refactor] Updated SYSTEM_PROMPT in `chief_agent.py`.
- [feat] Added `v0_design` tool to `chief_agent.py`.

## [v4.1] — 2026-02-20
## v4.1

- [feat] Added `v0_design` tool to `chief_agent.py`.
- [refactor] Updated `cmd_status` in `factory.py`.
- [feat] Added `cmd_v0_design` function to `factory.py`.
- [feat] Added result caching for visual QA.
- [feat] Added caching functions for visual QA.
- [refactor] Added `hashlib`, `json`, and `time` imports to `visual_qa.py`.
- [feat] Added spec file: `specs/interface/global_search_-_prioritize_exact_sku_matches.md`.
- [feat] Global search prioritizes exact SKU matches.
- [refactor] Updated `GlobalSearch.tsx` for efficient search result handling.
- [feat] Added JIT Intelligence integration to ProductDetailView.
- [feat] Added sourcing badges.
- [feat] Used ConductorCatalog for product details.
- [refactor] Updated imports in ProductDetailView.tsx.
- [feat] Added useRef to ProductDetailView.tsx.
- [feat] Added JITPhase and JITIntelligenceState to useJITIntelligence hook.
- [feat] Added useConductorCatalog hook.
- [feat] Added SourcingBadge component.
- [refactor] Updated RelationshipSection to handle product sources.
- [refactor] Updated styling and logic in ProductDetailView.tsx.
- [feat] Added logic to ProductDetailView to display information from conductor catalog.
- [refactor] Added a check to ProductDetailView to prevent calling useProductRelationships if there's no product.
- [refactor] Updated the SYSTEM_PROMPT in `chief_agent.py`.
- [feat] Added a new file `OrganizedCatalog.ts` with type definitions for brand catalog.
- [feat] Added spec for product tile image sourcing badges.
- [refactor] Removed optional Family and Relationship Inference logic in `OrganizedCatalog.ts`.
- [refactor] Return the `OrganizedCatalog` result directly in `OrganizedCatalog.ts`.
- [feat] Added a new API endpoint `/machines/{machine_id}/status` to fetch machine status.
- [feat] Implemented a FastAPI application `halilit_api/machines.py`.
- [feat] Added v0 agent file `backend/factory/v0_agent.py`.
- [refactor] Added a check to ProductDetailView to prevent calling useProductRelationships if there's no product.
- [refactor] Updated SYSTEM_PROMPT in `chief_agent.py`.
- [feat] Added v0 agent file `backend/factory/v0_agent.py`.
- [refactor] Added a check to ProductDetailView to prevent calling useProductRelationships if there's no product.
- [refactor] Updated SYSTEM_PROMPT in `chief_agent.py`.
- [feat] Added v0 agent file `backend/factory/v0_agent.py`.
- [refactor] Added a check to ProductDetailView to prevent calling useProductRelationships if there's no product.
- [refactor] Updated SYSTEM_PROMPT in `chief_agent.py`.
- [refactor] Added a check to ProductDetailView to prevent calling useProductRelationships if there's no product.
- [refactor] Updated SYSTEM_PROMPT in `chief_agent.py`.
- [refactor] Added a check to ProductDetailView to prevent calling useProductRelationships if there's no product.
- [refactor] Updated SYSTEM_PROMPT in `chief_agent.py`.
- [refactor] Added a check to ProductDetailView to prevent calling useProductRelationships if there's no product.
- [refactor] Updated SYSTEM_PROMPT in `chief_agent.py`.
- [refactor] Added a check to ProductDetailView to prevent calling useProductRelationships if there's no product.
- [refactor] Updated SYSTEM_PROMPT in `chief_agent.py`.
- [feat] Added `v0_design` tool to `chief_agent.py`.

## [v4.1] — 2026-02-20
## [v4.1]

- [feat] Added `v0_design` tool to `chief_agent.py`.
- [refactor] Updated `cmd_status` in `factory.py`.
- [feat] Added `cmd_v0_design` function to `factory.py`.
- [feat] Added result caching for visual QA.
- [feat] Added caching functions for visual QA.
- [refactor] Added `hashlib`, `json`, and `time` imports to `visual_qa.py`.
- [feat] Added spec file: `specs/interface/global_search_-_prioritize_exact_sku_matches.md`.
- [feat] Global search prioritizes exact SKU matches.
- [refactor] Updated `GlobalSearch.tsx` for efficient search result handling.
- [feat] Added JIT Intelligence integration to ProductDetailView.
- [feat] Added sourcing badges.
- [feat] Used ConductorCatalog for product details.
- [refactor] Updated imports in ProductDetailView.tsx.
- [feat] Added useRef to ProductDetailView.tsx.
- [feat] Added JITPhase and JITIntelligenceState to useJITIntelligence hook.
- [feat] Added useConductorCatalog hook.
- [feat] Added SourcingBadge component.
- [refactor] Updated RelationshipSection to handle product sources.
- [refactor] Updated styling and logic in ProductDetailView.tsx.
- [feat] Added logic to ProductDetailView to display information from conductor catalog.
- [refactor] Added a check to ProductDetailView to prevent calling useProductRelationships if there's no product.
- [refactor] Updated the SYSTEM_PROMPT in `chief_agent.py`.
- [feat] Added a new file `OrganizedCatalog.ts` with type definitions for brand catalog.
- [feat] Added spec for product tile image sourcing badges.
- [refactor] Removed optional Family and Relationship Inference logic in `OrganizedCatalog.ts`.
- [refactor] Return the `OrganizedCatalog` result directly in `OrganizedCatalog.ts`.
- [feat] Added a new API endpoint `/machines/{machine_id}/status` to fetch machine status.
- [feat] Implemented a FastAPI application `halilit_api/machines.py`.
- [feat] Added v0 agent file `backend/factory/v0_agent.py`.
- [refactor] Added a check to ProductDetailView to prevent calling useProductRelationships if there's no product.
- [refactor] Updated SYSTEM_PROMPT in `chief_agent.py`.
- [feat] Added v0 agent file `backend/factory/v0_agent.py`.
- [refactor] Added a check to ProductDetailView to prevent calling useProductRelationships if there's no product.
- [refactor] Updated SYSTEM_PROMPT in `chief_agent.py`.
- [feat] Added v0 agent file `backend/factory/v0_agent.py`.
- [refactor] Added a check to ProductDetailView to prevent calling useProductRelationships if there's no product.
- [refactor] Updated SYSTEM_PROMPT in `chief_agent.py`.
- [refactor] Added a check to ProductDetailView to prevent calling useProductRelationships if there's no product.
- [refactor] Updated SYSTEM_PROMPT in `chief_agent.py`.
- [refactor] Added a check to ProductDetailView to prevent calling useProductRelationships if there's no product.
- [refactor] Updated SYSTEM_PROMPT in `chief_agent.py`.
- [refactor] Added a check to ProductDetailView to prevent calling useProductRelationships if there's no product.
- [refactor] Updated SYSTEM_PROMPT in `chief_agent.py`.
- [refactor] Added a check to ProductDetailView to prevent calling useProductRelationships if there's no product.
- [refactor] Updated SYSTEM_PROMPT in `chief_agent.py`.
- [feat] Added `v0_design` tool to `chief_agent.py`.

## [v4.1] — 2026-02-19
## [v4.1]

- [feat] Added `v0_design` tool to `chief_agent.py`.
- [refactor] Updated `cmd_status` in `factory.py`.
- [feat] Added `cmd_v0_design` function to `factory.py`.
- [feat] Added result caching for visual QA.
- [feat] Added caching functions for visual QA.
- [refactor] Added `hashlib`, `json`, and `time` imports to `visual_qa.py`.
- [feat] Added spec file: `specs/interface/global_search_-_prioritize_exact_sku_matches.md`.
- [feat] Global search prioritizes exact SKU matches.
- [refactor] Updated `GlobalSearch.tsx` for efficient search result handling.
- [feat] Added JIT Intelligence integration to ProductDetailView.
- [feat] Added sourcing badges.
- [feat] Used ConductorCatalog for product details.
- [refactor] Updated imports in ProductDetailView.tsx.
- [feat] Added useRef to ProductDetailView.tsx.
- [feat] Added JITPhase and JITIntelligenceState to useJITIntelligence hook.
- [feat] Added useConductorCatalog hook.
- [feat] Added SourcingBadge component.
- [refactor] Updated RelationshipSection to handle product sources.
- [refactor] Updated styling and logic in ProductDetailView.tsx.
- [feat] Added logic to ProductDetailView to display information from conductor catalog.
- [refactor] Added a check to ProductDetailView to prevent calling useProductRelationships if there's no product.
- [refactor] Updated the SYSTEM_PROMPT in `chief_agent.py`.
- [feat] Added a new file `OrganizedCatalog.ts` with type definitions for brand catalog.
- [feat] Added spec for product tile image sourcing badges.
- [refactor] Removed optional Family and Relationship Inference logic in `OrganizedCatalog.ts`.
- [refactor] Return the `OrganizedCatalog` result directly in `OrganizedCatalog.ts`.
- [feat] Added a new API endpoint `/machines/{machine_id}/status` to fetch machine status.
- [feat] Implemented a FastAPI application `halilit_api/machines.py`.
- [feat] Added v0 agent file `backend/factory/v0_agent.py`.
- [refactor] Added a check to ProductDetailView to prevent calling useProductRelationships if there's no product.
- [refactor] Updated SYSTEM_PROMPT in `chief_agent.py`.
- [feat] Added v0 agent file `backend/factory/v0_agent.py`.
- [refactor] Added a check to ProductDetailView to prevent calling useProductRelationships if there's no product.
- [refactor] Updated SYSTEM_PROMPT in `chief_agent.py`.
- [feat] Added v0 agent file `backend/factory/v0_agent.py`.
- [refactor] Added a check to ProductDetailView to prevent calling useProductRelationships if there's no product.
- [refactor] Updated SYSTEM_PROMPT in `chief_agent.py`.
- [refactor] Added a check to ProductDetailView to prevent calling useProductRelationships if there's no product.
- [refactor] Updated SYSTEM_PROMPT in `chief_agent.py`.
- [refactor] Added a check to ProductDetailView to prevent calling useProductRelationships if there's no product.
- [refactor] Updated SYSTEM_PROMPT in `chief_agent.py`.
- [refactor] Added a check to ProductDetailView to prevent calling useProductRelationships if there's no product.
- [refactor] Updated SYSTEM_PROMPT in `chief_agent.py`.
- [refactor] Added a check to ProductDetailView to prevent calling useProductRelationships if there's no product.
- [refactor] Updated SYSTEM_PROMPT in `chief_agent.py`.
- [feat] Added `v0_design` tool to `chief_agent.py`.

## [v4.1] — 2026-02-19
## v4.1

- [feat] Added `v0_design` tool to `chief_agent.py`.
- [refactor] Updated `cmd_status` in `factory.py`.
- [feat] Added `cmd_v0_design` function to `factory.py`.
- [feat] Added result caching for visual QA.
- [feat] Added caching functions for visual QA.
- [refactor] Added `hashlib`, `json`, and `time` imports to `visual_qa.py`.
- [feat] Added spec file: `specs/interface/global_search_-_prioritize_exact_sku_matches.md`.
- [feat] Global search prioritizes exact SKU matches.
- [refactor] Updated `GlobalSearch.tsx` for efficient search result handling.
- [feat] Added JIT Intelligence integration to ProductDetailView.
- [feat] Added sourcing badges.
- [feat] Used ConductorCatalog for product details.
- [refactor] Updated imports in ProductDetailView.tsx.
- [feat] Added useRef to ProductDetailView.tsx.
- [feat] Added JITPhase and JITIntelligenceState to useJITIntelligence hook.
- [feat] Added useConductorCatalog hook.
- [feat] Added SourcingBadge component.
- [refactor] Updated RelationshipSection to handle product sources.
- [refactor] Updated styling and logic in ProductDetailView.tsx.
- [feat] Added logic to ProductDetailView to display information from conductor catalog.
- [refactor] Added a check to ProductDetailView to prevent calling useProductRelationships if there's no product.
- [refactor] Updated the SYSTEM_PROMPT in `chief_agent.py`.
- [feat] Added a new file `OrganizedCatalog.ts` with type definitions for brand catalog.
- [feat] Added spec for product tile image sourcing badges.
- [refactor] Removed optional Family and Relationship Inference logic in `OrganizedCatalog.ts`.
- [refactor] Return the `OrganizedCatalog` result directly in `OrganizedCatalog.ts`.
- [feat] Added a new API endpoint `/machines/{machine_id}/status` to fetch machine status.
- [feat] Implemented a FastAPI application `halilit_api/machines.py`.
- [feat] Added v0 agent file `backend/factory/v0_agent.py`.
- [refactor] Added a check to ProductDetailView to prevent calling useProductRelationships if there's no product.
- [refactor] Updated SYSTEM_PROMPT in `chief_agent.py`.
- [feat] Added v0 agent file `backend/factory/v0_agent.py`.
- [refactor] Added a check to ProductDetailView to prevent calling useProductRelationships if there's no product.
- [refactor] Updated SYSTEM_PROMPT in `chief_agent.py`.
- [feat] Added v0 agent file `backend/factory/v0_agent.py`.
- [refactor] Added a check to ProductDetailView to prevent calling useProductRelationships if there's no product.
- [refactor] Updated SYSTEM_PROMPT in `chief_agent.py`.
- [refactor] Added a check to ProductDetailView to prevent calling useProductRelationships if there's no product.
- [refactor] Updated SYSTEM_PROMPT in `chief_agent.py`.
- [refactor] Added a check to ProductDetailView to prevent calling useProductRelationships if there's no product.
- [refactor] Updated SYSTEM_PROMPT in `chief_agent.py`.
- [refactor] Added a check to ProductDetailView to prevent calling useProductRelationships if there's no product.
- [refactor] Updated SYSTEM_PROMPT in `chief_agent.py`.
- [refactor] Added a check to ProductDetailView to prevent calling useProductRelationships if there's no product.
- [refactor] Updated SYSTEM_PROMPT in `chief_agent.py`.
- [feat] Added `v0_design` tool to `chief_agent.py`.

## [v4.1] — 2026-02-19
## v4.1

- [feat] Added `v0_design` tool to `chief_agent.py`.
- [refactor] Updated `cmd_status` in `factory.py`.
- [feat] Added `cmd_v0_design` function to `factory.py`.
- [feat] Added result caching for visual QA.
- [feat] Added caching functions for visual QA.
- [refactor] Added `hashlib`, `json`, and `time` imports to `visual_qa.py`.
- [feat] Added spec file: `specs/interface/global_search_-_prioritize_exact_sku_matches.md`.
- [feat] Global search prioritizes exact SKU matches.
- [refactor] Updated `GlobalSearch.tsx` for efficient search result handling.
- [feat] Added JIT Intelligence integration to ProductDetailView.
- [feat] Added sourcing badges.
- [feat] Used ConductorCatalog for product details.
- [refactor] Updated imports in ProductDetailView.tsx.
- [feat] Added useRef to ProductDetailView.tsx.
- [feat] Added JITPhase and JITIntelligenceState to useJITIntelligence hook.
- [feat] Added useConductorCatalog hook.
- [feat] Added SourcingBadge component.
- [refactor] Updated RelationshipSection to handle product sources.
- [refactor] Updated styling and logic in ProductDetailView.tsx.
- [feat] Added logic to ProductDetailView to display information from conductor catalog.
- [refactor] Added a check to ProductDetailView to prevent calling useProductRelationships if there's no product.
- [refactor] Updated the SYSTEM_PROMPT in `chief_agent.py`.
- [feat] Added a new file `OrganizedCatalog.ts` with type definitions for brand catalog.
- [feat] Added spec for product tile image sourcing badges.
- [refactor] Removed optional Family and Relationship Inference logic in `OrganizedCatalog.ts`.
- [refactor] Return the `OrganizedCatalog` result directly in `OrganizedCatalog.ts`.
- [feat] Added a new API endpoint `/machines/{machine_id}/status` to fetch machine status.
- [feat] Implemented a FastAPI application `halilit_api/machines.py`.
- [feat] Added v0 agent file `backend/factory/v0_agent.py`.
- [refactor] Added a check to ProductDetailView to prevent calling useProductRelationships if there's no product.
- [refactor] Updated SYSTEM_PROMPT in `chief_agent.py`.
- [feat] Added v0 agent file `backend/factory/v0_agent.py`.
- [refactor] Added a check to ProductDetailView to prevent calling useProductRelationships if there's no product.
- [refactor] Updated SYSTEM_PROMPT in `chief_agent.py`.
- [feat] Added v0 agent file `backend/factory/v0_agent.py`.
- [refactor] Added a check to ProductDetailView to prevent calling useProductRelationships if there's no product.
- [refactor] Updated SYSTEM_PROMPT in `chief_agent.py`.
- [refactor] Added a check to ProductDetailView to prevent calling useProductRelationships if there's no product.
- [refactor] Updated SYSTEM_PROMPT in `chief_agent.py`.
- [refactor] Added a check to ProductDetailView to prevent calling useProductRelationships if there's no product.
- [refactor] Updated SYSTEM_PROMPT in `chief_agent.py`.
- [refactor] Added a check to ProductDetailView to prevent calling useProductRelationships if there's no product.
- [refactor] Updated SYSTEM_PROMPT in `chief_agent.py`.
- [refactor] Added a check to ProductDetailView to prevent calling useProductRelationships if there's no product.
- [refactor] Updated SYSTEM_PROMPT in `chief_agent.py`.
- [feat] Added `v0_design` tool to `chief_agent.py`.

## [v4.1] — 2026-02-19
## [v4.1]

- [feat] Added `v0_design` tool to `chief_agent.py`.
- [refactor] Updated `cmd_status` in `factory.py`.
- [feat] Added `cmd_v0_design` function to `factory.py`.
- [feat] Added result caching for visual QA.
- [feat] Added caching functions for visual QA.
- [refactor] Added `hashlib`, `json`, and `time` imports to `visual_qa.py`.
- [feat] Added spec file: `specs/interface/global_search_-_prioritize_exact_sku_matches.md`.
- [feat] Global search prioritizes exact SKU matches.
- [refactor] Updated `GlobalSearch.tsx` for efficient search result handling.
- [feat] Added JIT Intelligence integration to ProductDetailView.
- [feat] Added sourcing badges.
- [feat] Used ConductorCatalog for product details.
- [refactor] Updated imports in ProductDetailView.tsx.
- [feat] Added useRef to ProductDetailView.tsx.
- [feat] Added JITPhase and JITIntelligenceState to useJITIntelligence hook.
- [feat] Added useConductorCatalog hook.
- [feat] Added SourcingBadge component.
- [refactor] Updated RelationshipSection to handle product sources.
- [refactor] Updated styling and logic in ProductDetailView.tsx.
- [feat] Added logic to ProductDetailView to display information from conductor catalog.
- [refactor] Added a check to ProductDetailView to prevent calling useProductRelationships if there's no product.
- [refactor] Updated the SYSTEM_PROMPT in `chief_agent.py`.
- [feat] Added a new file `OrganizedCatalog.ts` with type definitions for brand catalog.
- [feat] Added spec for product tile image sourcing badges.
- [refactor] Removed optional Family and Relationship Inference logic in `OrganizedCatalog.ts`.
- [refactor] Return the `OrganizedCatalog` result directly in `OrganizedCatalog.ts`.
- [feat] Added a new API endpoint `/machines/{machine_id}/status` to fetch machine status.
- [feat] Implemented a FastAPI application `halilit_api/machines.py`.
- [feat] Added v0 agent file `backend/factory/v0_agent.py`.
- [refactor] Added a check to ProductDetailView to prevent calling useProductRelationships if there's no product.
- [refactor] Updated SYSTEM_PROMPT in `chief_agent.py`.
- [feat] Added v0 agent file `backend/factory/v0_agent.py`.
- [refactor] Added a check to ProductDetailView to prevent calling useProductRelationships if there's no product.
- [refactor] Updated SYSTEM_PROMPT in `chief_agent.py`.
- [feat] Added v0 agent file `backend/factory/v0_agent.py`.
- [refactor] Added a check to ProductDetailView to prevent calling useProductRelationships if there's no product.
- [refactor] Updated SYSTEM_PROMPT in `chief_agent.py`.
- [refactor] Added a check to ProductDetailView to prevent calling useProductRelationships if there's no product.
- [refactor] Updated SYSTEM_PROMPT in `chief_agent.py`.
- [refactor] Added a check to ProductDetailView to prevent calling useProductRelationships if there's no product.
- [refactor] Updated SYSTEM_PROMPT in `chief_agent.py`.
- [refactor] Added a check to ProductDetailView to prevent calling useProductRelationships if there's no product.
- [refactor] Updated SYSTEM_PROMPT in `chief_agent.py`.
- [refactor] Added a check to ProductDetailView to prevent calling useProductRelationships if there's no product.
- [refactor] Updated SYSTEM_PROMPT in `chief_agent.py`.
- [feat] Added `v0_design` tool to `chief_agent.py`.

## [v4.1] — 2026-02-19
## v4.1

- [feat] Added `v0_design` tool to `chief_agent.py`.
- [refactor] Updated `cmd_status` in `factory.py`.
- [feat] Added `cmd_v0_design` function to `factory.py`.
- [feat] Added result caching for visual QA.
- [feat] Added caching functions for visual QA.
- [refactor] Added `hashlib`, `json`, and `time` imports to `visual_qa.py`.
- [feat] Added spec file: `specs/interface/global_search_-_prioritize_exact_sku_matches.md`.
- [feat] Global search prioritizes exact SKU matches.
- [refactor] Updated `GlobalSearch.tsx` for efficient search result handling.
- [feat] Added JIT Intelligence integration to ProductDetailView.
- [feat] Added sourcing badges.
- [feat] Used ConductorCatalog for product details.
- [refactor] Updated imports in ProductDetailView.tsx.
- [feat] Added useRef to ProductDetailView.tsx.
- [feat] Added JITPhase and JITIntelligenceState to useJITIntelligence hook.
- [feat] Added useConductorCatalog hook.
- [feat] Added SourcingBadge component.
- [refactor] Updated RelationshipSection to handle product sources.
- [refactor] Updated styling and logic in ProductDetailView.tsx.
- [feat] Added logic to ProductDetailView to display information from conductor catalog.
- [refactor] Added a check to ProductDetailView to prevent calling useProductRelationships if there's no product.
- [refactor] Updated the SYSTEM_PROMPT in chief_agent.py.
- [feat] Added a new file `OrganizedCatalog.ts` with type definitions for brand catalog.
- [feat] Added spec for product tile image sourcing badges.
- [refactor] Removed optional Family and Relationship Inference logic in `OrganizedCatalog.ts`.
- [refactor] Return the `OrganizedCatalog` result directly in `OrganizedCatalog.ts`.
- [feat] Added a new API endpoint `/machines/{machine_id}/status` to fetch machine status.
- [feat] Implemented a FastAPI application `halilit_api/machines.py`.
- [feat] Added v0 agent file `backend/factory/v0_agent.py`.
- [refactor] Added a check to ProductDetailView to prevent calling useProductRelationships if there's no product.
- [refactor] Updated SYSTEM_PROMPT in chief_agent.py.
- [feat] Added v0 agent file `backend/factory/v0_agent.py`.
- [refactor] Added a check to ProductDetailView to prevent calling useProductRelationships if there's no product.
- [refactor] Updated SYSTEM_PROMPT in chief_agent.py.
- [feat] Added v0 agent file `backend/factory/v0_agent.py`.
- [refactor] Added a check to ProductDetailView to prevent calling useProductRelationships if there's no product.
- [refactor] Updated SYSTEM_PROMPT in chief_agent.py.
- [refactor] Added a check to ProductDetailView to prevent calling useProductRelationships if there's no product.
- [refactor] Updated SYSTEM_PROMPT in chief_agent.py.
- [refactor] Added a check to ProductDetailView to prevent calling useProductRelationships if there's no product.
- [refactor] Updated SYSTEM_PROMPT in chief_agent.py.
- [refactor] Added a check to ProductDetailView to prevent calling useProductRelationships if there's no product.
- [refactor] Updated SYSTEM_PROMPT in chief_agent.py.
- [refactor] Added a check to ProductDetailView to prevent calling useProductRelationships if there's no product.
- [refactor] Updated SYSTEM_PROMPT in chief_agent.py.
- [refactor] Added a check to ProductDetailView to prevent calling useProductRelationships if there's no product.
- [refactor] Updated SYSTEM_PROMPT in chief_agent.py.
- [feat] Added `v0_design` tool to `chief_agent.py`.

## [v4.1] — 2026-02-19
## v4.1

- [feat] Added `v0_design` tool to `chief_agent.py`.
- [refactor] Updated `cmd_status` in `factory.py`.
- [feat] Added `cmd_v0_design` function to `factory.py`.
- [feat] Added result caching for visual QA.
- [feat] Added caching functions for visual QA.
- [refactor] Added `hashlib`, `json`, and `time` imports to `visual_qa.py`.
- [feat] Added spec file: `specs/interface/global_search_-_prioritize_exact_sku_matches.md`.
- [feat] Global search prioritizes exact SKU matches.
- [refactor] Updated `GlobalSearch.tsx` for efficient search result handling.
- [feat] Added JIT Intelligence integration to ProductDetailView.
- [feat] Added sourcing badges.
- [feat] Used ConductorCatalog for product details.
- [refactor] Updated imports in ProductDetailView.tsx.
- [feat] Added useRef to ProductDetailView.tsx.
- [feat] Added JITPhase and JITIntelligenceState to useJITIntelligence hook.
- [feat] Added useConductorCatalog hook.
- [feat] Added SourcingBadge component.
- [refactor] Updated RelationshipSection to handle product sources.
- [refactor] Updated styling and logic in ProductDetailView.tsx.
- [feat] Added logic to ProductDetailView to display information from conductor catalog.
- [refactor] Added a check to ProductDetailView to prevent calling useProductRelationships if there's no product.
- [refactor] Updated the SYSTEM_PROMPT in chief_agent.py.
- [feat] Added a new file `OrganizedCatalog.ts` with type definitions for brand catalog.
- [feat] Added spec for product tile image sourcing badges.
- [refactor] Removed optional Family and Relationship Inference logic in `OrganizedCatalog.ts`.
- [refactor] Return the `OrganizedCatalog` result directly in `OrganizedCatalog.ts`.
- [feat] Added a new API endpoint `/machines/{machine_id}/status` to fetch machine status.
- [feat] Implemented a FastAPI application `halilit_api/machines.py`.
- [feat] Added v0 agent file `backend/factory/v0_agent.py`.
- [refactor] Added a check to ProductDetailView to prevent calling useProductRelationships if there's no product.
- [refactor] Updated SYSTEM_PROMPT in chief_agent.py.
- [feat] Added v0 agent file `backend/factory/v0_agent.py`.
- [refactor] Added a check to ProductDetailView to prevent calling useProductRelationships if there's no product.
- [refactor] Updated SYSTEM_PROMPT in chief_agent.py.
- [feat] Added v0 agent file `backend/factory/v0_agent.py`.
- [refactor] Added a check to ProductDetailView to prevent calling useProductRelationships if there's no product.
- [refactor] Updated SYSTEM_PROMPT in chief_agent.py.
- [refactor] Added a check to ProductDetailView to prevent calling useProductRelationships if there's no product.
- [refactor] Updated SYSTEM_PROMPT in chief_agent.py.
- [refactor] Added a check to ProductDetailView to prevent calling useProductRelationships if there's no product.
- [refactor] Updated SYSTEM_PROMPT in chief_agent.py.
- [refactor] Added a check to ProductDetailView to prevent calling useProductRelationships if there's no product.
- [refactor] Updated SYSTEM_PROMPT in chief_agent.py.
- [refactor] Added a check to ProductDetailView to prevent calling useProductRelationships if there's no product.
- [refactor] Updated SYSTEM_PROMPT in chief_agent.py.
- [refactor] Added a check to ProductDetailView to prevent calling useProductRelationships if there's no product.
- [refactor] Updated SYSTEM_PROMPT in chief_agent.py.
- [feat] Added `v0_design` tool to `chief_agent.py`.

## [v4.1] — 2026-02-19
## [v4.1]

- [feat] Added `v0_design` tool to `chief_agent.py`.
- [refactor] Updated `cmd_status` in `factory.py`.
- [feat] Added `cmd_v0_design` function to `factory.py`.
- [feat] Added result caching for visual QA.
- [feat] Added caching functions for visual QA.
- [refactor] Added `hashlib`, `json`, and `time` imports to `visual_qa.py`.
- [feat] Added spec file: `specs/interface/global_search_-_prioritize_exact_sku_matches.md`.
- [feat] Global search prioritizes exact SKU matches.
- [refactor] Updated `GlobalSearch.tsx` for efficient search result handling.
- [feat] Added JIT Intelligence integration to ProductDetailView.
- [feat] Added sourcing badges.
- [feat] Used ConductorCatalog for product details.
- [refactor] Updated imports in ProductDetailView.tsx.
- [feat] Added useRef to ProductDetailView.tsx.
- [feat] Added JITPhase and JITIntelligenceState to useJITIntelligence hook.
- [feat] Added useConductorCatalog hook.
- [feat] Added SourcingBadge component.
- [refactor] Updated RelationshipSection to handle product sources.
- [refactor] Updated styling and logic in ProductDetailView.tsx.
- [feat] Added logic to ProductDetailView to display information from conductor catalog.
- [refactor] Added a check to ProductDetailView to prevent calling useProductRelationships if there's no product.
- [refactor] Updated the SYSTEM_PROMPT in chief_agent.py.
- [feat] Added a new file `OrganizedCatalog.ts` with type definitions for brand catalog.
- [feat] Added spec for product tile image sourcing badges.
- [refactor] Removed optional Family and Relationship Inference logic in `OrganizedCatalog.ts`.
- [refactor] Return the `OrganizedCatalog` result directly in `OrganizedCatalog.ts`.
- [feat] Added a new API endpoint `/machines/{machine_id}/status` to fetch machine status.
- [feat] Implemented a FastAPI application `halilit_api/machines.py`.
- [feat] Added v0 agent file `backend/factory/v0_agent.py`.
- [refactor] Added a check to ProductDetailView to prevent calling useProductRelationships if there's no product.
- [refactor] Updated SYSTEM_PROMPT in chief_agent.py.
- [feat] Added v0 agent file `backend/factory/v0_agent.py`.
- [refactor] Added a check to ProductDetailView to prevent calling useProductRelationships if there's no product.
- [refactor] Updated SYSTEM_PROMPT in chief_agent.py.
- [feat] Added v0 agent file `backend/factory/v0_agent.py`.
- [refactor] Added a check to ProductDetailView to prevent calling useProductRelationships if there's no product.
- [refactor] Updated SYSTEM_PROMPT in chief_agent.py.
- [refactor] Added a check to ProductDetailView to prevent calling useProductRelationships if there's no product.
- [refactor] Updated SYSTEM_PROMPT in chief_agent.py.
- [refactor] Added a check to ProductDetailView to prevent calling useProductRelationships if there's no product.
- [refactor] Updated SYSTEM_PROMPT in chief_agent.py.
- [refactor] Added a check to ProductDetailView to prevent calling useProductRelationships if there's no product.
- [refactor] Updated SYSTEM_PROMPT in chief_agent.py.
- [refactor] Added a check to ProductDetailView to prevent calling useProductRelationships if there's no product.
- [refactor] Updated SYSTEM_PROMPT in chief_agent.py.
- [refactor] Added a check to ProductDetailView to prevent calling useProductRelationships if there's no product.
- [refactor] Updated SYSTEM_PROMPT in chief_agent.py.
- [feat] Added `v0_design` tool to `chief_agent.py`.

## [v4.1] — 2026-02-19
## [v4.1]

- [feat] Added `v0_design` tool to `chief_agent.py`.
- [refactor] Updated `cmd_status` in `factory.py`.
- [feat] Added `cmd_v0_design` function to `factory.py`.
- [feat] Added result caching for visual QA.
- [feat] Added caching functions for visual QA.
- [refactor] Added `hashlib`, `json`, and `time` imports to `visual_qa.py`.
- [feat] Added spec file: `specs/interface/global_search_-_prioritize_exact_sku_matches.md`.
- [feat] Global search prioritizes exact SKU matches.
- [refactor] Updated `GlobalSearch.tsx` for efficient search result handling.
- [feat] Added JIT Intelligence integration to ProductDetailView.
- [feat] Added sourcing badges.
- [feat] Used ConductorCatalog for product details.
- [refactor] Updated imports in ProductDetailView.tsx.
- [feat] Added useRef to ProductDetailView.tsx.
- [feat] Added JITPhase and JITIntelligenceState to useJITIntelligence hook.
- [feat] Added useConductorCatalog hook.
- [feat] Added SourcingBadge component.
- [refactor] Updated RelationshipSection to handle product sources.
- [refactor] Updated styling and logic in ProductDetailView.tsx.
- [feat] Added logic to ProductDetailView to display information from conductor catalog.
- [refactor] Added a check to ProductDetailView to prevent calling useProductRelationships if there's no product.
- [refactor] Updated the SYSTEM_PROMPT in chief_agent.py.
- [feat] Added a new file `OrganizedCatalog.ts` with type definitions for brand catalog.
- [feat] Added spec for product tile image sourcing badges.
- [refactor] Removed optional Family and Relationship Inference logic in `OrganizedCatalog.ts`.
- [refactor] Return the `OrganizedCatalog` result directly in `OrganizedCatalog.ts`.
- [feat] Added a new API endpoint `/machines/{machine_id}/status` to fetch machine status.
- [feat] Implemented a FastAPI application `halilit_api/machines.py`.
- [feat] Added v0 agent file `backend/factory/v0_agent.py`.
- [refactor] Added a check to ProductDetailView to prevent calling useProductRelationships if there's no product.
- [refactor] Updated SYSTEM_PROMPT in chief_agent.py.
- [feat] Added v0 agent file `backend/factory/v0_agent.py`.
- [refactor] Added a check to ProductDetailView to prevent calling useProductRelationships if there's no product.
- [refactor] Updated SYSTEM_PROMPT in chief_agent.py.
- [feat] Added v0 agent file `backend/factory/v0_agent.py`.
- [refactor] Added a check to ProductDetailView to prevent calling useProductRelationships if there's no product.
- [refactor] Updated SYSTEM_PROMPT in chief_agent.py.
- [refactor] Added a check to ProductDetailView to prevent calling useProductRelationships if there's no product.
- [refactor] Updated SYSTEM_PROMPT in chief_agent.py.
- [refactor] Added a check to ProductDetailView to prevent calling useProductRelationships if there's no product.
- [refactor] Updated SYSTEM_PROMPT in chief_agent.py.
- [refactor] Added a check to ProductDetailView to prevent calling useProductRelationships if there's no product.
- [refactor] Updated SYSTEM_PROMPT in chief_agent.py.
- [refactor] Added a check to ProductDetailView to prevent calling useProductRelationships if there's no product.
- [refactor] Updated SYSTEM_PROMPT in chief_agent.py.
- [refactor] Added a check to ProductDetailView to prevent calling useProductRelationships if there's no product.
- [refactor] Updated SYSTEM_PROMPT in chief_agent.py.
- [refactor] Added a check to ProductDetailView to prevent calling useProductRelationships if there's no product.
- [refactor] Updated SYSTEM_PROMPT in chief_agent.py.

## [v4.1] — 2026-02-19
## [v4.1] — 2026-02-19
- [feat] Added `v0_design` tool to `chief_agent.py`.
- [refactor] Updated `cmd_status` in `factory.py`.
- [feat] Added `cmd_v0_design` function to `factory.py`.
- [feat] Added result caching for visual QA.
- [feat] Added caching functions for visual QA.
- [refactor] Added `hashlib`, `json`, and `time` imports to `visual_qa.py`.
- [feat] Added spec file: `specs/interface/global_search_-_prioritize_exact_sku_matches.md`.
- [feat] Global search prioritizes exact SKU matches.
- [refactor] Updated `GlobalSearch.tsx` for efficient search result handling.
- [feat] Added JIT Intelligence integration to ProductDetailView.
- [feat] Added sourcing badges.
- [feat] Used ConductorCatalog for product details.
- [refactor] Updated imports in ProductDetailView.tsx.
- [feat] Added useRef to ProductDetailView.tsx.
- [feat] Added JITPhase and JITIntelligenceState to useJITIntelligence hook.
- [feat] Added useConductorCatalog hook.
- [feat] Added SourcingBadge component.
- [refactor] Updated RelationshipSection to handle product sources.
- [refactor] Updated styling and logic in ProductDetailView.tsx.
- [feat] Added logic to ProductDetailView to display information from conductor catalog.
- [refactor] Added a check to ProductDetailView to prevent calling useProductRelationships if there's no product.
- [refactor] Updated the SYSTEM_PROMPT in chief_agent.py.
- [feat] Added a new file `OrganizedCatalog.ts` with type definitions for brand catalog.
- [feat] Added spec for product tile image sourcing badges.
- [refactor] Removed optional Family and Relationship Inference logic in `OrganizedCatalog.ts`.
- [refactor] Return the `OrganizedCatalog` result directly in `OrganizedCatalog.ts`.
- [feat] Added a new API endpoint `/machines/{machine_id}/status` to fetch machine status.
- [feat] Implemented a FastAPI application `halilit_api/machines.py`.
- [feat] Added v0 agent file `backend/factory/v0_agent.py`.
- [refactor] Added a check to ProductDetailView to prevent calling useProductRelationships if there's no product.
- [refactor] Updated SYSTEM_PROMPT in chief_agent.py.
- [feat] Added v0 agent file `backend/factory/v0_agent.py`.
- [refactor] Added a check to ProductDetailView to prevent calling useProductRelationships if there's no product.
- [refactor] Updated SYSTEM_PROMPT in chief_agent.py.
- [refactor] Added a check to ProductDetailView to prevent calling useProductRelationships if there's no product.
- [refactor] Updated SYSTEM_PROMPT in chief_agent.py.
- [feat] Added v0 agent file `backend/factory/v0_agent.py`.
- [refactor] Added a check to ProductDetailView to prevent calling useProductRelationships if there's no product.
- [refactor] Updated SYSTEM_PROMPT in chief_agent.py.
- [refactor] Added a check to ProductDetailView to prevent calling useProductRelationships if there's no product.
- [refactor] Updated SYSTEM_PROMPT in chief_agent.py.
- [refactor] Added a check to ProductDetailView to prevent calling useProductRelationships if there's no product.
- [refactor] Updated SYSTEM_PROMPT in chief_agent.py.
- [refactor] Added a check to ProductDetailView to prevent calling useProductRelationships if there's no product.
- [refactor] Updated SYSTEM_PROMPT in chief_agent.py.
- [refactor] Added a check to ProductDetailView to prevent calling useProductRelationships if there's no product.
- [refactor] Updated SYSTEM_PROMPT in chief_agent.py.
- [refactor] Added a check to ProductDetailView to prevent calling useProductRelationships if there's no product.
- [refactor] Updated SYSTEM_PROMPT in chief_agent.py.
- [refactor] Added a check to ProductDetailView to prevent calling useProductRelationships if there's no product.
- [refactor] Updated SYSTEM_PROMPT in chief_agent.py.
- [refactor] Added a check to ProductDetailView to prevent calling useProductR

## [v4.1] — 2026-02-19
- [feat] Added `v0_design` tool to `chief_agent.py`.
- [refactor] Updated `cmd_status` in `factory.py`.
- [feat] Added `cmd_v0_design` function to `factory.py`.
- [feat] Added result caching for visual QA.
- [feat] Added caching functions for visual QA.
- [refactor] Added `hashlib`, `json`, and `time` imports to `visual_qa.py`.
- [feat] Added a new spec file: `specs/interface/global_search_-_prioritize_exact_sku_matches.md`.
- [feat] Global search prioritizes exact SKU matches.
- [refactor] Updated `GlobalSearch.tsx` for efficient search result handling.
- [feat] Added JIT Intelligence integration to ProductDetailView.
- [feat] Added sourcing badges.
- [feat] Used ConductorCatalog for product details.
- [refactor] Updated imports in ProductDetailView.tsx.
- [feat] Added useRef to ProductDetailView.tsx.
- [feat] Added JITPhase and JITIntelligenceState to useJITIntelligence hook.
- [feat] Added useConductorCatalog hook.
- [feat] Added SourcingBadge component.
- [refactor] Updated RelationshipSection to handle product sources.
- [refactor] Updated styling and logic in ProductDetailView.tsx.
- [feat] Added logic to ProductDetailView to display information from conductor catalog.
- [refactor] Added a check to ProductDetailView to prevent calling useProductRelationships if there's no product.
- [refactor] Updated the SYSTEM_PROMPT in chief_agent.py.
- [feat] Added a new file `OrganizedCatalog.ts` with type definitions for brand catalog.
- [feat] Added spec for product tile image sourcing badges.
- [refactor] Removed optional Family and Relationship Inference logic in `OrganizedCatalog.ts`.
- [refactor] Return the `OrganizedCatalog` result directly in `OrganizedCatalog.ts`.
- [feat] Added a new API endpoint `/machines/{machine_id}/status` to fetch machine status.
- [feat] Implemented a FastAPI application `halilit_api/machines.py`.
- [feat] Added v0 agent file `backend/factory/v0_agent.py`.
- [refactor] Added a check to ProductDetailView to prevent calling useProductRelationships if there's no product.
- [refactor] Updated SYSTEM_PROMPT in chief_agent.py.
- [feat] Added v0 agent file `backend/factory/v0_agent.py`.
- [refactor] Added a check to ProductDetailView to prevent calling useProductRelationships if there's no product.
- [refactor] Updated SYSTEM_PROMPT in chief_agent.py.
- [refactor] Added a check to ProductDetailView to prevent calling useProductRelationships if there's no product.
- [refactor] Updated SYSTEM_PROMPT in chief_agent.py.
- [feat] Added v0 agent file `backend/factory/v0_agent.py`.
- [refactor] Added a check to ProductDetailView to prevent calling useProductRelationships if there's no product.
- [refactor] Updated SYSTEM_PROMPT in chief_agent.py.
- [refactor] Added a check to ProductDetailView to prevent calling useProductRelationships if there's no product.
- [refactor] Updated SYSTEM_PROMPT in chief_agent.py.
- [refactor] Added a check to ProductDetailView to prevent calling useProductRelationships if there's no product.
- [refactor] Updated SYSTEM_PROMPT in chief_agent.py.
- [refactor] Added a check to ProductDetailView to prevent calling useProductRelationships if there's no product.
- [refactor] Updated SYSTEM_PROMPT in chief_agent.py.
- [refactor] Added a check to ProductDetailView to prevent calling useProductRelationships if there's no product.
- [refactor] Updated SYSTEM_PROMPT in chief_agent.py.
- [refactor] Added a check to ProductDetailView to prevent calling useProductRelationships if there's no product.
- [refactor] Updated SYSTEM_PROMPT in chief_agent.py.
- [refactor] Added a check to ProductDetailView to prevent calling useProductRelationships if there's no product.
- [refactor] Updated SYSTEM_PROMPT in chief_agent.py.
- [refactor] Added a check to ProductDetailView to prevent calling useProductRelationships if there's no product.
- [refactor] Updated SYSTEM_PROMPT in chief_agent.py.
- [feat] Added v0 agent file `backend/factory/v0_agent.py`.
- [refactor] Added a check to ProductDetailView to prevent calling useProductRelationships if there's no product.
- [refactor] Updated SYSTEM_PROMPT in chief_agent.py.
- [feat] Added v0 agent file `backend/factory/v0_agent.py`.
- [refactor] Added a check to ProductDetailView to prevent calling useProductRelationships if there's no product.
- [refactor] Updated SYSTEM_PROMPT in chief_agent.py.
- [feat] Added v0 agent file `backend/factory/v0_agent.py`.
- [refactor] Added a check to ProductDetailView to prevent calling useProductRelationships if there's no product.
- [refactor] Updated SYSTEM_PROMPT in chief_agent.py.
- [feat] Added v0 agent file `backend/factory/v0_agent.py`.
- [refactor] Added a check to ProductDetailView to prevent calling useProductRelationships if there's no product.
- [refactor] Updated SYSTEM_PROMPT in chief_agent.py.
- [feat] Added v0 agent file `backend/factory/v0_agent.py`.
- [refactor] Added a check to ProductDetailView to prevent calling useProductRelationships if there's no product.
- [refactor] Updated SYSTEM_PROMPT in chief_agent.py.
- [feat] Added v0 agent file `backend/factory/v0_agent.py`.
- [refactor] Added a check to ProductDetailView to prevent calling useProductRelationships if there's no product.
- [refactor] Updated SYSTEM_PROMPT in chief_agent.py.
- [feat] Added v0 agent file `backend/factory/v0_agent.py`.
- [refactor] Added a check to ProductDetailView to prevent calling useProductRelationships if there's no product.
- [refactor] Updated SYSTEM_PROMPT in chief_agent.py.
- [feat] Added v0 agent file `backend/factory/v0_agent.py`.
- [refactor] Added a check to ProductDetailView to prevent calling useProductRelationships if there's no product.
- [refactor] Updated SYSTEM_PROMPT in chief_agent.py.
- [feat] Added v0 agent file `backend/factory/v0_agent.py`.
- [refactor] Added a check to ProductDetailView to prevent calling useProductRelationships if there's no product.
- [refactor] Updated SYSTEM_PROMPT in chief_agent.py.
- [feat] Added v0 agent file `backend/factory/v0_agent.py`.
- [refactor] Added a check to ProductDetailView to prevent calling useProductRelationships if there's no product.
- [refactor] Updated SYSTEM_PROMPT in chief_agent.py.
- [feat] Added v0 agent file `backend/factory/v0_agent.py`.
- [refactor] Added a check to ProductDetailView to prevent calling useProductRelationships if there's no product.
- [refactor] Updated SYSTEM_PROMPT in chief_agent.py.
- [feat] Added v0 agent file `backend/factory/v0_agent.py`.
- [refactor] Added a check to ProductDetailView to prevent calling useProductRelationships if there's no product.
- [refactor] Updated SYSTEM_PROMPT in chief_agent.py.
- [feat] Added v0 agent file `backend/factory/v0_agent.py`.
- [refactor] Added a check to ProductDetailView to prevent calling useProductRelationships if there's no product.
- [refactor] Updated SYSTEM_PROMPT in chief_agent.py.
- [feat] Added v0 agent file `backend/factory/v0_agent.py`.
- [refactor] Added a check to ProductDetailView to prevent calling useProductRelationships if there's no product.
- [refactor] Updated SYSTEM_PROMPT in chief_agent.py.
- [feat] Added v0 agent file `backend/factory/v0_agent.py`.
- [refactor] Added a check to ProductDetailView to prevent calling useProductRelationships if there's no product.
- [refactor] Updated SYSTEM_PROMPT in chief_agent.py.
- [feat] Added v0 agent file `backend/factory/v0_agent.py`.
- [refactor] Added a check to ProductDetailView to prevent calling useProductRelationships if there's no product.
- [refactor] Updated SYSTEM_PROMPT in chief_agent.py.
- [feat] Added v0 agent file `backend/factory/v0_agent.py`.
- [refactor] Added a check to ProductDetailView to prevent calling useProductRelationships if there's no product.
- [refactor] Updated SYSTEM_PROMPT in chief_agent.py.
- [feat] Added v0 agent file `backend/factory/v0_agent.py`.
- [refactor] Added a check to ProductDetailView to prevent calling useProductRelationships if there's no product.
- [refactor] Updated SYSTEM_PROMPT in chief_agent.py.
- [feat] Added v0 agent file `backend/factory/v0_agent.py`.
- [refactor] Added a check to ProductDetailView to prevent calling useProductRelationships if there's no product.
- [refactor] Updated SYSTEM_PROMPT in chief_agent.py.
- [feat] Added v0 agent file `backend/factory/v0_agent.py`.
- [refactor] Added a check to ProductDetailView to prevent calling useProductRelationships if there's no product.
- [refactor] Updated SYSTEM_PROMPT in chief_agent.py.
- [feat] Added v0 agent file `backend/factory/v0_agent.py`.
- [refactor] Added a check to ProductDetailView to prevent calling useProductRelationships if there's no product.
- [refactor] Updated SYSTEM_PROMPT in chief_agent.py.
- [feat] Added v0 agent file `backend/factory/v0_agent.py`.
- [refactor] Added a check to ProductDetailView to prevent calling useProductRelationships if there's no product.
- [refactor] Updated SYSTEM_PROMPT in chief_agent.py.
- [feat] Added v0 agent file `backend/factory/v0_agent.py`.
- [refactor] Added a check to ProductDetailView to prevent calling useProductRelationships if there's no product.
- [refactor] Updated SYSTEM_PROMPT in chief_agent.py.
- [feat] Added v0 agent file `backend/factory/v0_agent.py`.
- [refactor] Added a check to ProductDetailView to prevent calling useProductRelationships if there's no product.
- [refactor] Updated SYSTEM_PROMPT in chief_agent.py.
- [feat] Added v0 agent file `backend/factory/v0_agent.py`.
- [refactor] Added a check to ProductDetailView to prevent calling useProductRelationships if there's no product.
- [refactor] Updated SYSTEM_PROMPT in chief_agent.py.
- [feat] Added v0 agent file `backend/factory/v0_agent.py`.
- [refactor] Added a check to ProductDetailView to prevent calling useProductRelationships if there's no product.
- [refactor] Updated SYSTEM_PROMPT in chief_agent.py.
- [feat] Added v0 agent file `backend/factory/v0_agent.py`.
- [refactor] Added a check to ProductDetailView to prevent calling useProductRelationships if there's no product.
- [refactor] Updated SYSTEM_PROMPT in chief_agent.py.
- [feat] Added v0 agent file `backend/factory/v0_agent.py`.
- [refactor] Added a check to ProductDetailView to prevent calling useProductRelationships if there's no product.
- [refactor] Updated SYSTEM_PROMPT in chief_agent.py.
- [feat] Added v0 agent file `backend/factory/v0_agent.py`.
- [refactor] Added a check to ProductDetailView to prevent calling useProductRelationships if there's no product.
- [refactor] Updated SYSTEM_PROMPT in chief_agent.py.
- [feat] Added v0 agent file `backend/factory/v0_agent.py`.
- [refactor] Added a check to ProductDetailView to prevent calling useProductRelationships if there's no product.
- [refactor] Updated SYSTEM_PROMPT in chief_agent.py.
- [feat] Added v0 agent file `backend/factory/v0_agent.py`.
- [refactor] Added a check to ProductDetailView to prevent calling useProductRelationships if there's no product.
- [refactor] Updated SYSTEM_PROMPT in chief_agent.py.
- [feat] Added v0 agent file `backend/factory/v0_agent.py`.
- [refactor] Added a check to ProductDetailView to prevent calling useProductRelationships if there's no product.
- [refactor] Updated SYSTEM_PROMPT in chief_agent.py.
- [feat] Added v0 agent file `backend/factory/v0_agent.py`.
- [refactor] Added a check to ProductDetailView to prevent calling useProductRelationships if there's no product.
- [refactor] Updated SYSTEM_PROMPT in chief_agent.py.
- [feat] Added v0 agent file `backend/factory/v0_agent.py`.
- [refactor] Added a check to ProductDetailView to prevent calling useProductRelationships if there's no product.
- [refactor] Updated SYSTEM_PROMPT in chief_agent.py.
- [feat] Added v0 agent file `backend/factory/v0_agent.py`.
- [refactor] Added a check to ProductDetailView to prevent calling useProductRelationships if there's no product.
- [refactor] Updated SYSTEM_PROMPT in chief_agent.py.
- [feat] Added v0 agent file `backend/factory/v0_agent.py`.
- [refactor] Added a check to ProductDetailView to prevent calling useProductRelationships if there's no product.
- [refactor] Updated SYSTEM_PROMPT in chief_agent.py.
- [feat] Added v0 agent file `backend/factory/v0_agent.py`.
- [refactor] Added a check to ProductDetailView to prevent calling useProductRelationships if there's no product.
- [refactor] Updated SYSTEM_PROMPT in chief_agent.py.
- [feat] Added v0 agent file `backend/factory/v0_agent.py`.
- [refactor] Added a check to ProductDetailView to prevent calling useProductRelationships if there's no product.
- [refactor] Updated SYSTEM_PROMPT in chief_agent.py.
- [feat] Added v0 agent file `backend/factory/v0_agent.py`.
- [refactor] Added a check to ProductDetailView to prevent calling useProductRelationships if there's no product.
- [refactor] Updated SYSTEM_PROMPT in chief_agent.py.
- [feat] Added v0 agent file `backend/factory/v0_agent.py`.
- [refactor] Added a check to ProductDetailView to prevent calling useProductRelationships if there's no product.
- [refactor] Updated SYSTEM_PROMPT in chief_agent.py.
- [feat] Added v0 agent file `backend/factory/v0_agent.py`.
- [refactor] Added a check to ProductDetailView to prevent calling useProductRelationships if there's no product.
- [refactor] Updated SYSTEM_PROMPT in chief_agent.py.
- [feat] Added v0 agent file `backend/factory/v0_agent.py`.
- [refactor] Added a check to ProductDetailView to prevent calling useProductRelationships if there's no product.
- [refactor] Updated SYSTEM_PROMPT in chief_agent.py.
- [feat] Added v0 agent file `backend/factory/v0_agent.py`.
- [refactor] Added a check to ProductDetailView to prevent calling useProductRelationships if there's no product.
- [refactor] Updated SYSTEM_PROMPT in chief_agent.py.
- [feat] Added v0 agent file `backend/factory/v0_agent.py`.
- [refactor] Added a check to ProductDetailView to prevent calling useProductRelationships if there's no product.
- [refactor] Updated SYSTEM_PROMPT in chief_agent.py.
- [feat] Added v0 agent file `backend/factory/v0_agent.py`.
- [refactor] Added a check to ProductDetailView to prevent calling useProductRelationships if there's no product.
- [refactor] Updated SYSTEM_PROMPT in chief_agent.py.
- [feat] Added v0 agent file `backend/factory/v0_agent.py`.
- [refactor] Added a check to ProductDetailView to prevent calling useProductRelationships if there's no product.
- [refactor] Updated SYSTEM_PROMPT in chief_agent.py.
- [feat] Added v0 agent file `backend/factory/v0_agent.py`.
- [refactor] Added a check to ProductDetailView to prevent calling useProductRelationships if there's no product.
- [refactor] Updated SYSTEM_PROMPT in chief_agent.py.
- [feat] Added v0 agent file `backend/factory/v0_agent.py`.
- [refactor] Added a check to ProductDetailView to prevent calling useProductRelationships if there's no product.
- [refactor] Updated SYSTEM_PROMPT in chief_agent.py.
- [feat] Added v0 agent file `backend/factory/v0_agent.py`.
- [refactor] Added a check to ProductDetailView to prevent calling useProductRelationships if there's no product.
- [refactor] Updated SYSTEM_PROMPT in chief_agent.py.
- [feat] Added v0 agent file `backend/factory/v0_agent.py`.
- [refactor] Added a check to ProductDetailView to prevent calling useProductRelationships if there's no product.
- [refactor] Updated SYSTEM_PROMPT in chief_agent.py.
- [feat] Added v0 agent file `backend/factory/v0_agent.py`.
- [refactor] Added a check to ProductDetailView to prevent calling useProductRelationships if there's no product.
- [refactor] Updated SYSTEM_PROMPT in chief_agent.py.
- [feat] Added v0 agent file `backend/factory/v0_agent.py`.
- [refactor] Added a check to ProductDetailView to prevent calling useProductRelationships if there's no product.
- [refactor] Updated SYSTEM_PROMPT in chief_agent.py.
- [feat] Added v0 agent file `backend/factory/v0_agent.py`.
- [refactor] Added a check to ProductDetailView to prevent calling useProductRelationships if there's no product.
- [refactor] Updated SYSTEM_PROMPT in chief_agent.py.
- [feat] Added v0 agent file `backend/factory/v0_agent.py`.
- [refactor] Added a check to ProductDetailView to prevent calling useProductRelationships if there's no product.
- [refactor] Updated SYSTEM_PROMPT in chief_agent.py.
- [feat] Added v0 agent file `backend/factory/v0_agent.py`.
- [refactor] Added a check to ProductDetailView to prevent calling useProductRelationships if there's no product.
- [refactor] Updated SYSTEM_PROMPT in chief_agent.py.
- [feat] Added v0 agent file `backend/factory/v0_agent.py`.
- [refactor] Added a check to ProductDetailView to prevent calling useProductRelationships if there's no product.
- [refactor] Updated SYSTEM_PROMPT in chief_agent.py.
- [feat] Added v0 agent file `backend/factory/v0_agent.py`.
- [refactor] Added a check to ProductDetailView to prevent calling useProductRelationships if there's no product.
- [refactor] Updated SYSTEM_PROMPT in chief_agent.py.
- [feat] Added v0 agent file `backend/factory/v0_agent.py`.
- [refactor] Added a check to ProductDetailView to prevent calling useProductRelationships if there's no product.
- [refactor] Updated SYSTEM_PROMPT in chief_agent.py.
- [feat] Added v0 agent file `backend/factory/v0_agent.py`.
- [refactor] Added a check to ProductDetailView to prevent calling useProductRelationships if there's no product.
- [refactor] Updated SYSTEM_PROMPT in chief_agent.py.
- [feat] Added v0 agent file `backend/factory/v0_agent.py`.
- [refactor] Added a check to ProductDetailView to prevent calling useProductRelationships if there's no product.
- [refactor] Updated SYSTEM_PROMPT in chief_agent.py.
- [feat] Added v0 agent file `backend/factory/v0_agent.py`.
- [refactor] Added a check to ProductDetailView to prevent calling useProductRelationships if there's no product.
- [refactor] Updated SYSTEM_PROMPT in chief_agent.py.
- [feat] Added v0 agent file `backend/factory/v0_agent.py`.
- [refactor] Added a check to ProductDetailView to prevent calling useProductRelationships if there's no product.
- [refactor] Updated SYSTEM_PROMPT in chief_agent.py.
- [feat] Added v0 agent file `backend/factory/v0_agent.py`.
- [refactor] Added a check to ProductDetailView to prevent calling useProductRelationships if there's no product.
- [refactor] Updated SYSTEM_PROMPT in chief_agent.py.
- [feat] Added v0 agent file `backend/factory/v0_agent.py`.
- [refactor] Added a check to ProductDetailView to prevent calling useProductRelationships if there's no product.
- [refactor] Updated SYSTEM_PROMPT in chief_agent.py.
- [feat] Added v0 agent file `backend/factory/v0_agent.py`.
- [refactor] Added a check to ProductDetailView to prevent calling useProductRelationships if there's no product.
- [refactor] Updated SYSTEM_PROMPT in chief_agent.py.
- [feat] Added v0 agent file `backend/factory/v0_agent.py`.
- [refactor] Added a check to ProductDetailView to prevent calling useProductRelationships if there's no product.
- [refactor] Updated SYSTEM_PROMPT in chief_agent.py.
- [feat] Added v0 agent file `backend/factory/v0_agent.py`.
- [refactor] Added a check to ProductDetailView to prevent calling useProductRelationships if there's no product.
- [refactor] Updated SYSTEM_PROMPT in chief_agent.py.
- [feat] Added v0 agent file `backend/factory/v0_agent.py`.
- [refactor] Added a check to ProductDetailView to prevent calling useProductRelationships if there's no product.
- [refactor] Updated SYSTEM_PROMPT in chief_agent.py.
- [feat] Added v0 agent file `backend/factory/v0_agent.py`.
- [refactor] Added a check to ProductDetailView to prevent calling useProductRelationships if there's no product.
- [refactor] Updated SYSTEM_PROMPT in chief_agent.py.
- [feat] Added v0 agent file `backend/factory/v0_agent.py`.
- [refactor] Added a check to ProductDetailView to prevent calling useProductRelationships if there's no product.
- [refactor] Updated SYSTEM_PROMPT in chief_agent.py.
- [feat] Added v0 agent file `backend/factory/v0_agent.py`.
- [refactor] Added a check to ProductDetailView to prevent calling useProductRelationships if there's no product.
- [refactor] Updated SYSTEM_PROMPT in chief_agent.py.
- [feat] Added v0 agent file `backend/factory/v0_agent.py`.
- [refactor] Added a check to ProductDetailView to prevent calling useProductRelationships if there's no product.
- [refactor] Updated SYSTEM_PROMPT in chief_agent.py.
- [feat] Added v0 agent file `backend/factory/v0_agent.py`.
- [refactor] Added a check to ProductDetailView to prevent calling useProductRelationships if there's no product.
- [refactor] Updated SYSTEM_PROMPT in chief_agent.py.
- [feat] Added v0 agent file `backend/factory/v0_agent.py`.
- [refactor] Added a check to ProductDetailView to prevent calling useProductRelationships if there's no product.
- [refactor] Updated SYSTEM_PROMPT in chief_agent.py.
- [feat] Added v0 agent file `backend/factory/v0_agent.py`.
- [refactor] Added a check to ProductDetailView to prevent calling useProductRelationships if there's no product.
- [refactor] Updated SYSTEM_PROMPT in chief_agent.py.
- [feat] Added v0 agent file `backend/factory/v0_agent.py`.
- [refactor] Added a check to ProductDetailView to prevent calling useProductRelationships if there's no product.
- [refactor] Updated SYSTEM_PROMPT in chief_agent.py.
- [feat] Added v0 agent file `backend/factory/v0_agent.py`.
- [refactor] Added a check to ProductDetailView to prevent calling useProductRelationships if there's no product.
- [refactor] Updated SYSTEM_PROMPT in chief_agent.py.
- [feat] Added v0 agent file `backend/factory/v0_agent.py`.
- [refactor] Added a check to ProductDetailView to prevent calling useProductRelationships if there's no product.
- [refactor] Updated SYSTEM_PROMPT in chief_agent.py.
- [feat] Added v0 agent file `backend/factory/v0_agent.py`.
- [refactor] Added a check to ProductDetailView to prevent calling useProductRelationships if there's no product.
- [refactor] Updated SYSTEM_PROMPT in chief_agent.py.
- [feat] Added v0 agent file `backend/factory/v0_agent.py`.
- [refactor] Added a check to ProductDetailView to prevent calling useProductRelationships if there's no product.
- [refactor] Updated SYSTEM_PROMPT in chief_agent.py.
- [feat] Added v0 agent file `backend/factory/v0_agent.py`.
- [refactor] Added a check to ProductDetailView to prevent calling useProductRelationships if there's no product.
- [refactor] Updated SYSTEM_PROMPT in chief_agent.py.
- [feat] Added v0 agent file `backend/factory/v0_agent.py`.
- [refactor] Added a check to ProductDetailView to prevent calling useProductRelationships if there's no product.
- [refactor] Updated SYSTEM_PROMPT in chief_agent.py.
- [feat] Added v0 agent file `backend/factory/v0_agent.py`.
- [refactor] Added a check to ProductDetailView to prevent calling useProductRelationships if there's no product.
- [refactor] Updated SYSTEM_PROMPT in chief_agent.py.
- [feat] Added v0 agent file `backend/factory/v0_agent.py`.
- [refactor] Added a check to ProductDetailView to prevent calling useProductRelationships if there's no product.
- [refactor] Updated SYSTEM_PROMPT in chief_agent.py.
- [feat] Added v0 agent file `backend/factory/v0_agent.py`.
- [refactor] Added a check to ProductDetailView to prevent calling useProductRelationships if there's no product.
- [refactor] Updated SYSTEM_PROMPT in chief_agent.py.
- [feat] Added v0 agent file `backend/factory/v0_agent.py`.
- [refactor] Added a check to ProductDetailView to prevent calling useProductRelationships if there's no product.
- [refactor] Updated SYSTEM_PROMPT in chief_agent.py.
- [feat] Added v0 agent file `backend/factory/v0_agent.py`.
- [refactor] Added a check to ProductDetailView to prevent calling useProductRelationships if there's no product.
- [refactor] Updated SYSTEM_PROMPT in chief_agent.py.
- [feat] Added v0 agent file `backend/factory/v0_agent.py`.
- [refactor] Added a check to ProductDetailView to prevent calling useProductRelationships if there's no product.
- [refactor] Updated SYSTEM_PROMPT in chief_agent.py.
- [feat] Added v0 agent file `backend/factory/v0_agent.py`.
- [refactor] Added a check to ProductDetailView to prevent calling useProductRelationships if there's no product.
- [refactor] Updated SYSTEM_PROMPT in chief_agent.py.
- [feat] Added v0 agent file `backend/factory/v0_agent.py`.
- [refactor] Added a check to ProductDetailView to prevent calling useProductRelationships if there's no product.
- [refactor] Updated SYSTEM_PROMPT in chief_agent.py.
- [feat] Added v0 agent file `backend/factory/v0_agent.py`.
- [refactor] Added a check to ProductDetailView to prevent calling useProductRelationships if there's no product.
- [refactor] Updated SYSTEM_PROMPT in chief_agent.py.
- [feat] Added v0 agent file `backend/factory/v0_agent.py`.
- [refactor] Added a check to ProductDetailView to prevent calling useProductRelationships if there's no product.
- [refactor] Updated SYSTEM_PROMPT in chief_agent.py.
- [feat] Added v0 agent file `backend/factory/v0_agent.py`.
- [refactor] Added a check to ProductDetailView to prevent calling useProductRelationships if there's no product.
- [refactor] Updated SYSTEM_PROMPT in chief_agent.py.
- [feat] Added v0 agent file `backend/factory/v0_agent.py`.
- [refactor] Added a check to ProductDetailView to prevent calling useProductRelationships if there's no product.
- [refactor] Updated SYSTEM_PROMPT in chief_agent.py.
- [feat] Added v0 agent file `backend/factory/v0_agent.py`.
- [refactor] Added a check to ProductDetailView to prevent calling useProductRelationships if there's no product.
- [refactor] Updated SYSTEM_PROMPT in chief_agent.py.
- [feat] Added v0 agent file `backend/factory/v0_agent.py`.
- [refactor] Added a check to ProductDetailView to prevent calling useProductRelationships if there's no product.
- [refactor] Updated SYSTEM_PROMPT in chief_agent.py.
- [feat] Added v0 agent file `backend/factory/v0_agent.py`.
- [refactor] Added a check to ProductDetailView to prevent calling useProductRelationships if there's no product.
- [refactor] Updated SYSTEM_PROMPT in chief_agent.py.
- [feat] Added v0 agent file `backend/factory/v0_agent.py`.
- [refactor] Added a check to ProductDetailView to prevent calling useProductRelationships if there's no product.
- [refactor] Updated SYSTEM_PROMPT in chief_agent.py.
- [feat] Added v0 agent file `backend/factory/v0_agent.py`.
- [refactor] Added a check to ProductDetailView to prevent calling useProductRelationships if there's no product.
- [refactor] Updated SYSTEM_PROMPT in chief_agent.py.
- [feat] Added v0 agent file `backend/factory/v0_agent.py`.
- [refactor] Added a check to ProductDetailView to prevent calling useProductRelationships if there's no product.
- [refactor] Updated SYSTEM_PROMPT in chief_agent.py.
- [feat] Added v0 agent file `backend/factory/v0_agent.py`.
- [refactor] Added a check to ProductDetailView to prevent calling useProductRelationships if there's no product.
- [refactor] Updated SYSTEM_PROMPT in chief_agent.py.
- [feat] Added v0 agent file `backend/factory/v0_agent.py`.
- [refactor] Added a check to ProductDetailView to prevent calling useProductRelationships if there's no product.
- [refactor] Updated SYSTEM_PROMPT in chief_agent.py.
- [feat] Added v0 agent file `backend/factory/v0_agent.py`.
- [refactor] Added a check to ProductDetailView to prevent calling useProductRelationships if there's no product.
- [refactor] Updated SYSTEM_PROMPT in chief_agent.py.
- [feat] Added v0 agent file `backend/factory/v0_agent.py`.
- [refactor] Added a check to ProductDetailView to prevent calling useProductRelationships if there's no product.
- [refactor] Updated SYSTEM_PROMPT in chief_agent.py.
- [feat] Added v0 agent file `backend/factory/v0_agent.py`.
- [refactor] Added a check to ProductDetailView to prevent calling useProductRelationships if there's no product.
- [refactor] Updated SYSTEM_PROMPT in chief_agent.py.
- [feat] Added v0 agent file `backend/factory/v0_agent.py`.
- [refactor] Added a check to ProductDetailView to prevent calling useProductRelationships if there's no product.
- [refactor] Updated SYSTEM_PROMPT in chief_agent.py.
- [feat] Added v0 agent file `backend/factory/v0_agent.py`.
- [refactor] Added a check to ProductDetailView to prevent calling useProductRelationships if there's no product.
- [refactor] Updated SYSTEM_PROMPT in chief_agent.py.
- [feat] Added v0 agent file `backend/factory/v0_agent.py`.
- [refactor] Added a check to ProductDetailView to prevent calling useProductRelationships if there's no product.
- [refactor] Updated SYSTEM_PROMPT in chief_agent.py.
- [feat] Added v0 agent file `

## [v4.1] — 2026-02-19
## [v4.1]
- [feat] Added `v0_design` tool to `chief_agent.py`.
- [refactor] Updated `cmd_status` in `factory.py`.
- [feat] Added `cmd_v0_design` function to `factory.py`.

## [v4.1]
- [feat] Added result caching for visual QA.
- [feat] Added caching functions for visual QA.
- [refactor] Added `hashlib`, `json`, and `time` imports to `visual_qa.py`.
- [feat] Added a new spec file: `specs/interface/global_search_-_prioritize_exact_sku_matches.md`.
- [feat] Global search prioritizes exact SKU matches.
- [refactor] Updated `GlobalSearch.tsx` for efficient search result handling.
- [feat] Added JIT Intelligence integration to ProductDetailView.
- [feat] Added sourcing badges.
- [feat] Used ConductorCatalog for product details.
- [refactor] Updated imports in ProductDetailView.tsx.
- [feat] Added useRef to ProductDetailView.tsx.
- [feat] Added JITPhase and JITIntelligenceState to useJITIntelligence hook.
- [feat] Added useConductorCatalog hook.
- [feat] Added SourcingBadge component.
- [refactor] Updated RelationshipSection to handle product sources.
- [refactor] Updated styling and logic in ProductDetailView.tsx.
- [feat] Added logic to ProductDetailView to display information from conductor catalog.
- [refactor] Added a check to ProductDetailView to prevent calling useProductRelationships if there's no product.
- [refactor] Updated the SYSTEM_PROMPT in chief_agent.py.
- [feat] Added a new file `OrganizedCatalog.ts` with type definitions for brand catalog.
- [feat] Added spec for product tile image sourcing badges.
- [refactor] Removed optional Family and Relationship Inference logic in `OrganizedCatalog.ts`.
- [refactor] Return the `OrganizedCatalog` result directly in `OrganizedCatalog.ts`.
- [feat] Added a new API endpoint `/machines/{machine_id}/status` to fetch machine status.
- [feat] Implemented a FastAPI application `halilit_api/machines.py`.
- [feat] Added v0 agent file `backend/factory/v0_agent.py`.

## [v4.1] — 2026-02-19
## [v4.1]

- [feat] Added result caching for visual QA.
- [feat] Added caching functions for visual QA.
- [refactor] Added `hashlib`, `json`, and `time` imports to `visual_qa.py`.
- [feat] Added a new spec file: `specs/interface/global_search_-_prioritize_exact_sku_matches.md`.
- [feat] Global search prioritizes exact SKU matches.
- [refactor] Updated `GlobalSearch.tsx` for efficient search result handling.
- [feat] Added JIT Intelligence integration to ProductDetailView.
- [feat] Added sourcing badges.
- [feat] Used ConductorCatalog for product details.
- [refactor] Updated imports in ProductDetailView.tsx.
- [feat] Added useRef to ProductDetailView.tsx.
- [feat] Added JITPhase and JITIntelligenceState to useJITIntelligence hook.
- [feat] Added useConductorCatalog hook.
- [feat] Added SourcingBadge component.
- [refactor] Updated RelationshipSection to handle product sources.
- [refactor] Updated styling and logic in ProductDetailView.tsx.
- [feat] Added logic to ProductDetailView to display information from conductor catalog.
- [refactor] Added a check to ProductDetailView to prevent calling useProductRelationships if there's no product.
- [refactor] Updated the SYSTEM_PROMPT in chief_agent.py.
- [feat] Added a new file `OrganizedCatalog.ts` with type definitions for brand catalog.
- [feat] Added spec for product tile image sourcing badges.
- [refactor] Removed optional Family and Relationship Inference logic in `OrganizedCatalog.ts`.
- [refactor] Return the `OrganizedCatalog` result directly in `OrganizedCatalog.ts`.
- [feat] Added a new API endpoint `/machines/{machine_id}/status` to fetch machine status.
- [feat] Implemented a FastAPI application `halilit_api/machines.py`.
- [feat] Added v0 agent file `backend/factory/v0_agent.py`.

## [v4.1]

- [feat] Added `v0_design` tool to `chief_agent.py`.
- [refactor] Updated `cmd_status` in `factory.py`.
- [feat] Added `cmd_v0_design` function to `factory.py`.

## [v4.1] — 2026-02-19
## [v4.1]

- [feat] Added result caching for visual QA.
- [feat] Added caching functions for visual QA.
- [refactor] Added `hashlib`, `json`, and `time` imports to `visual_qa.py`.
- [feat] Added a new spec file: `specs/interface/global_search_-_prioritize_exact_sku_matches.md`.
- [feat] Global search prioritizes exact SKU matches.
- [refactor] Updated `GlobalSearch.tsx` for efficient search result handling.
- [feat] Added JIT Intelligence integration to ProductDetailView.
- [feat] Added sourcing badges.
- [feat] Used ConductorCatalog for product details.
- [refactor] Updated imports in ProductDetailView.tsx.
- [feat] Added useRef to ProductDetailView.tsx.
- [feat] Added JITPhase and JITIntelligenceState to useJITIntelligence hook.
- [feat] Added useConductorCatalog hook.
- [feat] Added SourcingBadge component.
- [refactor] Updated RelationshipSection to handle product sources.
- [refactor] Updated styling and logic in ProductDetailView.tsx.
- [feat] Added logic to ProductDetailView to display information from conductor catalog.
- [refactor] Added a check to ProductDetailView to prevent calling useProductRelationships if there's no product.
- [refactor] Updated the SYSTEM_PROMPT in chief_agent.py.
- [feat] Added a new file `OrganizedCatalog.ts` with type definitions for brand catalog.
- [feat] Added spec for product tile image sourcing badges.
- [refactor] Removed optional Family and Relationship Inference logic in `OrganizedCatalog.ts`.
- [refactor] Return the `OrganizedCatalog` result directly in `OrganizedCatalog.ts`.
- [feat] Added a new API endpoint `/machines/{machine_id}/status` to fetch machine status.
- [feat] Implemented a FastAPI application `halilit_api/machines.py`.
- [feat] Added v0 agent file `backend/factory/v0_agent.py`.

## [v4.1] — 2026-02-19
## v4.1

- [feat] Implemented result caching for visual QA.
- [feat] Added caching functions for visual QA.
- [refactor] Added `hashlib`, `json`, and `time` imports to `visual_qa.py`.
- [feat] Added a new spec file: `specs/interface/global_search_-_prioritize_exact_sku_matches.md`.
- [feat] Global search prioritizes exact SKU matches.
- [refactor] Updated `GlobalSearch.tsx` for efficient search result handling.
- [feat] Added JIT Intelligence integration to ProductDetailView.
- [feat] Added sourcing badges.
- [feat] Used ConductorCatalog for product details.
- [refactor] Updated imports in ProductDetailView.tsx.
- [feat] Added useRef to ProductDetailView.tsx.
- [feat] Added JITPhase and JITIntelligenceState to useJITIntelligence hook.
- [feat] Added useConductorCatalog hook.
- [feat] Added SourcingBadge component.
- [refactor] Updated RelationshipSection to handle product sources.
- [refactor] Updated styling and logic in ProductDetailView.tsx.
- [feat] Added logic to ProductDetailView to display information from conductor catalog.
- [refactor] Added a check to ProductDetailView to prevent calling useProductRelationships if there's no product.
- [refactor] Updated the SYSTEM_PROMPT in chief_agent.py.
- [feat] Added a new file `OrganizedCatalog.ts` with type definitions for brand catalog.
- [feat] Added spec for product tile image sourcing badges.
- [refactor] Removed optional Family and Relationship Inference logic in `OrganizedCatalog.ts`.
- [refactor] Return the `OrganizedCatalog` result directly in `OrganizedCatalog.ts`.
- [feat] Added a new API endpoint `/machines/{machine_id}/status` to fetch machine status.
- [feat] Implemented a FastAPI application `halilit_api/machines.py`.

## [v4.1] — 2026-02-19
## [v4.1]

- [feat] Implemented result caching for visual QA.
- [feat] Added caching functions for visual QA.
- [refactor] Added `hashlib`, `json`, and `time` imports to `visual_qa.py`.
- [feat] Added a new spec file: `specs/interface/global_search_-_prioritize_exact_sku_matches.md`.
- [feat] Global search prioritizes exact SKU matches.
- [refactor] Updated `GlobalSearch.tsx` for efficient search result handling.
- [feat] Added JIT Intelligence integration to ProductDetailView.
- [feat] Added sourcing badges.
- [feat] Used ConductorCatalog for product details.
- [refactor] Updated imports in ProductDetailView.tsx.
- [feat] Added useRef to ProductDetailView.tsx.
- [feat] Added JITPhase and JITIntelligenceState to useJITIntelligence hook.
- [feat] Added useConductorCatalog hook.
- [feat] Added SourcingBadge component.
- [refactor] Updated RelationshipSection to handle product sources.
- [refactor] Updated styling and logic in ProductDetailView.tsx.
- [feat] Added logic to ProductDetailView to display information from conductor catalog.
- [refactor] Added a check to ProductDetailView to prevent calling useProductRelationships if there's no product.
- [refactor] Updated the SYSTEM_PROMPT in chief_agent.py.
- [feat] Added a new file `OrganizedCatalog.ts` with type definitions for brand catalog.
- [feat] Added spec for product tile image sourcing badges.
- [refactor] Removed optional Family and Relationship Inference logic in `OrganizedCatalog.ts`.
- [refactor] Return the `OrganizedCatalog` result directly in `OrganizedCatalog.ts`.

## [v4.1]

- [feat] Implemented result caching for visual QA.
- [feat] Added caching functions for visual QA.

## [v4.1]

- [feat] Implemented result caching for visual QA.
- [feat] Added caching functions for visual QA.
- [refactor] Added `hashlib`, `json`, and `time` imports to `visual_qa.py`.
- [feat] Added a new spec file: `specs/interface/global_search_-_prioritize_exact_sku_matches.md`.
- [feat] Global search prioritizes exact SKU matches.
- [refactor] Updated `GlobalSearch.tsx` for efficient search result handling.
- [feat] Added JIT Intelligence integration to ProductDetailView.
- [feat] Added sourcing badges.
- [feat] Used ConductorCatalog for product details.
- [refactor] Updated imports in ProductDetailView.tsx.
- [feat] Added useRef to ProductDetailView.tsx.
- [feat] Added JITPhase and JITIntelligenceState to useJITIntelligence hook.
- [feat] Added useConductorCatalog hook.
- [feat] Added SourcingBadge component.
- [refactor] Updated RelationshipSection to handle product sources.
- [refactor] Updated styling and logic in ProductDetailView.tsx.
- [feat] Added logic to ProductDetailView to display information from conductor catalog.
- [refactor] Added a check to ProductDetailView to prevent calling useProductRelationships if there's no product.
- [refactor] Updated the SYSTEM_PROMPT in chief_agent.py.
- [feat] Added a new file `OrganizedCatalog.ts` with type definitions for brand catalog.
- [feat] Added spec for product tile image sourcing badges.
- [refactor] Removed optional Family and Relationship Inference logic in `OrganizedCatalog.ts`.
- [refactor] Return the `OrganizedCatalog` result directly in `OrganizedCatalog.ts`.

## [v4.1]

- [feat] Added a new API endpoint `/machines/{machine_id}/status` to fetch machine status.
- [feat] Implemented a FastAPI application `halilit_api/machines.py`.

## [v4.1]

- [feat] Implemented result caching for visual QA.
- [feat] Added caching functions for visual QA.
- [refactor] Added `hashlib`, `json`, and `time` imports to `visual_qa.py`.
- [feat] Added a new spec file: `specs/interface/global_search_-_prioritize_exact_sku_matches.md`.
- [feat] Global search prioritizes exact SKU matches.
- [refactor] Updated `GlobalSearch.tsx` for efficient search result handling.
- [feat] Added JIT Intelligence integration to ProductDetailView.
- [feat] Added sourcing badges.
- [feat] Used ConductorCatalog for product details.
- [refactor] Updated imports in ProductDetailView.tsx.
- [feat] Added useRef to ProductDetailView.tsx.
- [feat] Added JITPhase and JITIntelligenceState to useJITIntelligence hook.
- [feat] Added useConductorCatalog hook.
- [feat] Added SourcingBadge component.
- [refactor] Updated RelationshipSection to handle product sources.
- [refactor] Updated styling and logic in ProductDetailView.tsx.
- [feat] Added logic to ProductDetailView to display information from conductor catalog.
- [refactor] Added a check to ProductDetailView to prevent calling useProductRelationships if there's no product.
- [refactor] Updated the SYSTEM_PROMPT in chief_agent.py.
- [feat] Added a new file `OrganizedCatalog.ts` with type definitions for brand catalog.
- [feat] Added spec for product tile image sourcing badges.
- [refactor] Removed optional Family and Relationship Inference logic in `OrganizedCatalog.ts`.
- [refactor] Return the `OrganizedCatalog` result directly in `OrganizedCatalog.ts`.

## [v4.1] — 2026-02-19
## [v4.1] — 2026-02-19

- [feat] Implemented result caching for visual QA.
- [feat] Added caching functions for visual QA.
- [refactor] Added `hashlib`, `json`, and `time` imports to `visual_qa.py`.
- [feat] Added a new spec file: `specs/interface/global_search_-_prioritize_exact_sku_matches.md`.
- [feat] Global search prioritizes exact SKU matches.
- [refactor] Updated `GlobalSearch.tsx` for efficient search result handling.
- [feat] Added JIT Intelligence integration to ProductDetailView.
- [feat] Added sourcing badges.
- [feat] Used ConductorCatalog for product details.
- [refactor] Updated imports in ProductDetailView.tsx.
- [feat] Added useRef to ProductDetailView.tsx.
- [feat] Added JITPhase and JITIntelligenceState to useJITIntelligence hook.
- [feat] Added useConductorCatalog hook.
- [feat] Added SourcingBadge component.
- [refactor] Updated RelationshipSection to handle product sources.
- [refactor] Updated styling and logic in ProductDetailView.tsx.
- [feat] Added logic to ProductDetailView to display information from conductor catalog.
- [refactor] Added a check to ProductDetailView to prevent calling useProductRelationships if there's no product.
- [refactor] Updated the SYSTEM_PROMPT in chief_agent.py.
- [feat] Added a new file `OrganizedCatalog.ts` with type definitions for brand catalog.
- [feat] Added spec for product tile image sourcing badges.
- [refactor] Removed optional Family and Relationship Inference logic in `OrganizedCatalog.ts`.
- [refactor] Return the `OrganizedCatalog` result directly in `OrganizedCatalog.ts`.

## [v4.1] — 2026-02-19
- [feat] Implemented result caching for visual QA.
- [feat] Added caching functions for visual QA.
- [refactor] Added `hashlib`, `json`, and `time` imports to `visual_qa.py`.
- [feat] Added a new spec file: `specs/interface/global_search_-_prioritize_exact_sku_matches.md`.
- [feat] Global search prioritizes exact SKU matches.
- [refactor] Updated `GlobalSearch.tsx` for efficient search result handling.
- [feat] Added JIT Intelligence integration to ProductDetailView.
- [feat] Added sourcing badges.
- [feat] Used ConductorCatalog for product details.
- [refactor] Updated imports in ProductDetailView.tsx.
- [feat] Added useRef to ProductDetailView.tsx.
- [feat] Added JITPhase and JITIntelligenceState to useJITIntelligence hook.
- [feat] Added useConductorCatalog hook.
- [feat] Added SourcingBadge component.
- [refactor] Updated RelationshipSection to handle product sources.
- [refactor] Updated styling and logic in ProductDetailView.tsx.
- [feat] Added logic to ProductDetailView to display information from conductor catalog.
- [refactor] Added a check to ProductDetailView to prevent calling useProductRelationships if there's no product.
- [refactor] Updated the SYSTEM_PROMPT in chief_agent.py.
- [feat] Added a new file `OrganizedCatalog.ts` with type definitions for brand catalog.
- [feat] Added spec for product tile image sourcing badges.

## [v4.1] — 2026-02-19
- [feat] Implemented result caching for visual QA.
- [feat] Added caching functions for visual QA.
- [refactor] Added `hashlib`, `json`, and `time` imports to `visual_qa.py`.
- [feat] Added a new spec file: `specs/interface/global_search_-_prioritize_exact_sku_matches.md`.
- [feat] Global search prioritizes exact SKU matches.
- [refactor] Updated `GlobalSearch.tsx` for efficient search result handling.
- [feat] Added JIT Intelligence integration to ProductDetailView.
- [feat] Added sourcing badges.
- [feat] Used ConductorCatalog for product details.
- [refactor] Updated imports in ProductDetailView.tsx.
- [feat] Added useRef to ProductDetailView.tsx.
- [feat] Added JITPhase and JITIntelligenceState to useJITIntelligence hook.
- [feat] Added useConductorCatalog hook.
- [feat] Added SourcingBadge component.
- [refactor] Updated RelationshipSection to handle product sources.
- [refactor] Updated styling and logic in ProductDetailView.tsx.
- [feat] Added logic to ProductDetailView to display information from conductor catalog.
- [refactor] Added a check to ProductDetailView to prevent calling useProductRelationships if there's no product.
- [refactor] Updated the SYSTEM_PROMPT in chief_agent.py.
- [feat] Added a new file `OrganizedCatalog.ts` with type definitions for brand catalog.

## [v4.1] — 2026-02-19
## [v4.1]

### Visual QA
- [feat] Implemented result caching for visual QA.
- [feat] Added caching functions for visual QA.
- [refactor] Added `hashlib`, `json`, and `time` imports to `visual_qa.py`.

### Global Search
- [feat] Added a new spec file: `specs/interface/global_search_-_prioritize_exact_sku_matches.md`.
- [feat] Global search prioritizes exact SKU matches.
- [refactor] Updated `GlobalSearch.tsx` for efficient search result handling.

### Product Detail View
- [feat] Added JIT Intelligence integration to ProductDetailView.
- [feat] Added sourcing badges.
- [feat] Used ConductorCatalog for product details.
- [refactor] Updated imports in ProductDetailView.tsx.
- [feat] Added useRef to ProductDetailView.tsx.
- [feat] Added JITPhase and JITIntelligenceState to useJITIntelligence hook.
- [feat] Added useConductorCatalog hook.
- [feat] Added SourcingBadge component.
- [refactor] Updated RelationshipSection to handle product sources.
- [refactor] Updated styling and logic in ProductDetailView.tsx.
- [feat] Added logic to ProductDetailView to display information from conductor catalog.
- [refactor] Added a check to ProductDetailView to prevent calling useProductRelationships if there's no product.

### Backend Changes
- [refactor] Updated the SYSTEM_PROMPT in chief_agent.py.

## [v4.1] — 2026-02-19
## [v4.1]

### Visual QA
- [feat] Implemented result caching for visual QA.
- [feat] Added caching functions for visual QA.
- [refactor] Added `hashlib`, `json`, and `time` imports to `visual_qa.py`.

### Global Search
- [feat] Added a new spec file: `specs/interface/global_search_-_prioritize_exact_sku_matches.md`.
- [feat] Global search prioritizes exact SKU matches.
- [refactor] Updated `GlobalSearch.tsx` for efficient search result handling.

### Product Detail View
- [feat] Added JIT Intelligence integration to ProductDetailView.
- [feat] Added sourcing badges.
- [feat] Used ConductorCatalog for product details.
- [refactor] Updated imports in ProductDetailView.tsx.
- [feat] Added useRef to ProductDetailView.tsx.
- [feat] Added JITPhase and JITIntelligenceState to useJITIntelligence hook.
- [feat] Added useConductorCatalog hook.
- [feat] Added SourcingBadge component.
- [refactor] Updated RelationshipSection to handle product sources.
- [refactor] Updated styling and logic in ProductDetailView.tsx.
- [feat] Added logic to ProductDetailView to display information from conductor catalog.
- [refactor] Added a check to ProductDetailView to prevent calling useProductRelationships if there's no product.

### Backend Changes
- [refactor] Updated the SYSTEM_PROMPT in chief_agent.py.

## [v4.1] — 2026-02-19
## [v4.1]

### Visual QA
- [feat] Implemented result caching for visual QA.
- [feat] Added caching functions for visual QA.
- [refactor] Added `hashlib`, `json`, and `time` imports to `visual_qa.py`.

### Global Search
- [feat] Added a new spec file: `specs/interface/global_search_-_prioritize_exact_sku_matches.md`.
- [feat] Global search prioritizes exact SKU matches.
- [refactor] Updated `GlobalSearch.tsx` for efficient search result handling.

### Product Detail View
- [feat] Added JIT Intelligence integration to ProductDetailView.
- [feat] Added sourcing badges.
- [feat] Used ConductorCatalog for product details.
- [refactor] Updated imports in ProductDetailView.tsx.
- [feat] Added useRef to ProductDetailView.tsx.
- [feat] Added JITPhase and JITIntelligenceState to useJITIntelligence hook.
- [feat] Added useConductorCatalog hook.
- [feat] Added SourcingBadge component.
- [refactor] Updated RelationshipSection to handle product sources.
- [refactor] Updated styling and logic in ProductDetailView.tsx.
- [feat] Added logic to ProductDetailView to display information from conductor catalog.
- [refactor] Added a check to ProductDetailView to prevent calling useProductRelationships if there's no product.

### Backend Changes
- [refactor] Updated the SYSTEM_PROMPT in chief_agent.py.

## [v4.1] — 2026-02-19
## v4.1

- [feat] Implemented result caching for visual QA.
- [feat] Added caching functions for visual QA.
- [refactor] Added `hashlib`, `json`, and `time` imports to `visual_qa.py`.
- [feat] Added a new spec file: `specs/interface/global_search_-_prioritize_exact_sku_matches.md`.
- [feat] Global search prioritizes exact SKU matches.
- [refactor] Updated `GlobalSearch.tsx` for efficient search result handling.
- [feat] Added JIT Intelligence integration to ProductDetailView.
- [feat] Added sourcing badges.
- [feat] Used ConductorCatalog for product details.
- [refactor] Updated imports in ProductDetailView.tsx.
- [feat] Added useRef to ProductDetailView.tsx.
- [feat] Added JITPhase and JITIntelligenceState to useJITIntelligence hook.
- [feat] Added useConductorCatalog hook.
- [feat] Added SourcingBadge component.
- [refactor] Updated RelationshipSection to handle product sources.
- [refactor] Updated styling and logic in ProductDetailView.tsx.
- [feat] Added logic to ProductDetailView to display information from conductor catalog.
- [refactor] Added a check to ProductDetailView to prevent calling useProductRelationships if there's no product.

## Backend Changes
- [refactor] Updated the SYSTEM_PROMPT in chief_agent.py.

## [v4.1] — 2026-02-19
- [feat] Implemented result caching for visual QA to avoid re-running Playwright for the same URL+spec within TTL.
- [feat] Added `_vqa_cache_key`, `_vqa_cache_load`, `_vqa_cache_save`, `_vqa_cache_get`, and `_vqa_cache_set` functions for caching.
- [refactor] Added `hashlib`, `json`, and `time` imports to `visual_qa.py`.
- [feat] Added a new spec file: `specs/interface/global_search_-_prioritize_exact_sku_matches.md`.
- [feat] Global search results now prioritize exact SKU matches.
- [refactor] Updated `GlobalSearch.tsx` to handle search results more efficiently.
- [feat] Added JIT Intelligence integration to ProductDetailView.
- [feat] Added sourcing badges.
- [feat] Use ConductorCatalog for product details.
- [refactor] Updated imports in ProductDetailView.tsx.
- [feat] Added useRef to ProductDetailView.tsx
- [feat] Added JITPhase and JITIntelligenceState to useJITIntelligence hook.
- [feat] Added useConductorCatalog hook.
- [feat] Added SourcingBadge component.
- [refactor] Updated RelationshipSection to handle product sources.
- [refactor] Updated styling and logic in ProductDetailView.tsx.
- [feat] Added logic to ProductDetailView to retrieve and display information from conductor catalog.
- [refactor] Added a check to ProductDetailView to prevent calling useProductRelationships if there's no product.

## [v4.1] — 2026-02-19
## v4.1

- [feat] Implemented result caching for visual QA to avoid re-running Playwright for the same URL+spec within TTL.
- [feat] Added `_vqa_cache_key`, `_vqa_cache_load`, `_vqa_cache_save`, `_vqa_cache_get`, and `_vqa_cache_set` functions for caching.
- [refactor] Added `hashlib`, `json`, and `time` imports to `visual_qa.py`.
- [feat] Added a new spec file: `specs/interface/global_search_-_prioritize_exact_sku_matches.md`.
- [feat] Global search results now prioritize exact SKU matches.
- [refactor] Updated `GlobalSearch.tsx` to handle search results more efficiently.

## [v4.1] — 2026-02-19
## v4.1

- [feat] Implemented result caching for visual QA to avoid re-running Playwright for the same URL+spec within TTL.
- [feat] Added `_vqa_cache_key`, `_vqa_cache_load`, `_vqa_cache_save`, `_vqa_cache_get`, and `_vqa_cache_set` functions for caching.
- [refactor] Added `hashlib`, `json`, and `time` imports to `visual_qa.py`.
- [feat] Added a new spec file: `specs/interface/global_search_-_prioritize_exact_sku_matches.md`.

## [v4.1] — 2026-02-19
## v4.1

- [feat] Implemented result caching for visual QA to avoid re-running Playwright for the same URL+spec within TTL.
- [feat] Added `_vqa_cache_key`, `_vqa_cache_load`, `_vqa_cache_save`, `_vqa_cache_get`, and `_vqa_cache_set` functions for caching.
- [refactor] Added `hashlib`, `json`, and `time` imports to `visual_qa.py`.

## [v4.1] — 2026-02-19
- [feat] Implemented result caching for visual QA to avoid re-running Playwright for the same URL+spec within TTL.
- [feat] Added `_vqa_cache_key`, `_vqa_cache_load`, `_vqa_cache_save`, `_vqa_cache_get`, and `_vqa_cache_set` functions for caching.
- [refactor] Added `hashlib`, `json`, and `time` imports to `visual_qa.py`.

## [v4.1] — 2026-02-19
## v4.1

- [feat] Added tool routing in `run_agent_tool`.
- [feat] Implemented routing for 'build' tool, handling spec file paths and general rebuild commands.
- [feat] Implemented routing for 'implement' tool, using 'build' command with spec file path.
- [feat] Added routing for 'task_force' tool, including auto-generation of task IDs.
- [refactor] Added a docstring for `run_agent_tool` describing routing behavior.
- [style] Added an empty line for readability in `factory_supervisor.py`.
- [style] Imported `uuid` module locally in `run_agent_tool`.
- [fix] Fixed an issue with `task_force` where missing 'id' or 'goal' prevented execution and logged an error message.
- [docs] Updated `docs/ARCHITECTURE.md` with an architecture overview.
- [docs] Added new spec file `specs/interface/product_detail_-_ecosystem_tab.md`.
- [docs] Updated `docs/LEARNED_GUIDELINES.md` with new linting guideline.
- [feat] Added ProductTile React component.
- [feat] Added ProductDetailView React component.

## [v4.1] — 2026-02-19
## v4.1

- [feat] Added tool routing in `run_agent_tool`.
- [feat] Implemented routing for 'build' tool, handling spec file paths and general rebuild commands.
- [feat] Implemented routing for 'implement' tool, using 'build' command with spec file path.
- [feat] Added routing for 'task_force' tool, including auto-generation of task IDs.
- [refactor] Added a docstring for `run_agent_tool` describing routing behavior.
- [style] Added an empty line for readability in `factory_supervisor.py`.
- [style] Imported `uuid` module locally in `run_agent_tool`.
- [fix] Fixed an issue with `task_force` where missing 'id' or 'goal' prevented execution and logged an error message.
- [docs] Updated `docs/ARCHITECTURE.md` with an architecture overview.

## v4.1
- [docs] Added new spec file `specs/interface/product_detail_-_ecosystem_tab.md`.
- [docs] Updated `docs/LEARNED_GUIDELINES.md` with new linting guideline.

## [v4.1] — 2026-02-19
## [v4.1]

- [feat] Added tool routing in `run_agent_tool`.
- [feat] Implemented routing for 'build' tool, handling spec file paths and general rebuild commands.
- [feat] Implemented routing for 'implement' tool, using 'build' command with spec file path.
- [feat] Added routing for 'task_force' tool, including auto-generation of task IDs.
- [refactor] Added a docstring for `run_agent_tool` describing routing behavior.
- [style] Added an empty line for readability in `factory_supervisor.py`.
- [style] Imported `uuid` module locally in `run_agent_tool`.
- [fix] Fixed an issue with `task_force` where missing 'id' or 'goal' prevented execution and logged an error message.
- [docs] Updated `docs/ARCHITECTURE.md` with an architecture overview.

## [v4.1] — 2026-02-19
## [v4.1]

- [feat] Added tool routing in `run_agent_tool`.
- [feat] Implemented routing for 'build' tool, handling spec file paths and general rebuild commands.
- [feat] Implemented routing for 'implement' tool, using 'build' command with spec file path.
- [feat] Added routing for 'task_force' tool, including auto-generation of task IDs.
- [refactor] Added a docstring for `run_agent_tool` describing routing behavior.
- [style] Added an empty line for readability in `factory_supervisor.py`.
- [style] Imported `uuid` module locally in `run_agent_tool`.
- [fix] Fixed an issue with `task_force` where missing 'id' or 'goal' prevented execution and logged an error message.
- [docs] Updated `docs/ARCHITECTURE.md` with an architecture overview.

## [v4.1] — 2026-02-19
## v4.1

- [feat] Added tool routing in `run_agent_tool`.
- [feat] Implemented routing for 'build' tool, handling spec file paths and general rebuild commands.
- [feat] Implemented routing for 'implement' tool, using 'build' command with spec file path.
- [feat] Added routing for 'task_force' tool, including auto-generation of task IDs.
- [refactor] Added a docstring for `run_agent_tool` describing routing behavior.
- [style] Added an empty line for readability in `factory_supervisor.py`.
- [style] Imported `uuid` module locally in `run_agent_tool`.
- [fix] Fixed an issue with `task_force` where missing 'id' or 'goal' prevented execution and logged an error message.
- [docs] Updated `docs/ARCHITECTURE.md` with an architecture overview.

## [v4.1] — 2026-02-19
## [v4.1]

- [feat] Added tool routing in `run_agent_tool`.
- [feat] Implemented routing for 'build' tool, handling spec file paths and general rebuild commands.
- [feat] Implemented routing for 'implement' tool, using 'build' command with spec file path.
- [feat] Added routing for 'task_force' tool, including auto-generation of task IDs.
- [refactor] Added a docstring for `run_agent_tool` describing routing behavior.
- [style] Added an empty line for readability in `factory_supervisor.py`.
- [style] Imported `uuid` module locally in `run_agent_tool`.
- [fix] Fixed an issue with `task_force` where missing 'id' or 'goal' prevented execution and logged an error message.
- [docs] Updated `docs/ARCHITECTURE.md` with an architecture overview.

## [v4.1] — 2026-02-19
## v4.1

- [feat] Added tool routing in `run_agent_tool`.
- [feat] Implemented routing for 'build' tool, handling spec file paths and general rebuild commands.
- [feat] Implemented routing for 'implement' tool, using 'build' command with spec file path.
- [feat] Added routing for 'task_force' tool, including auto-generation of task IDs.
- [refactor] Added a docstring for `run_agent_tool` describing routing behavior.
- [style] Added an empty line for readability in `factory_supervisor.py`.
- [style] Imported `uuid` module locally in `run_agent_tool`.
- [fix] Fixed an issue with `task_force` where missing 'id' or 'goal' prevented execution and logged an error message.

## [v4.1] — 2026-02-19
## [v4.1]

- [feat] Added tool routing in `run_agent_tool`.
- [feat] Implemented routing for 'build' tool, handling spec file paths and general rebuild commands.
- [feat] Added routing for 'implement' tool, using 'build' command with spec file path.
- [feat] Implemented routing for 'task_force' tool, including auto-generation of task IDs.
- [refactor] Added a docstring for `run_agent_tool` describing routing behavior.
- [style] Added an empty line for readability in `factory_supervisor.py`.
- [style] Imported `uuid` module locally in `run_agent_tool`.
- [fix] Fixed an issue with `task_force` where missing 'id' or 'goal' prevented execution and logged an error message.
- [feat] Added tool routing in `run_agent_tool`.
- [feat] Implemented routing for 'build' tool, handling spec file paths and general rebuild commands.
- [feat] Implemented routing for 'implement' tool, using 'build' command with spec file path.
- [feat] Added tool routing in `run_agent_tool`.
- [feat] Added routing for 'build' tool, handling spec file paths and general rebuild commands.
- [feat] Implemented routing for 'implement' tool, using 'build' command with spec file path.
- [feat] Added tool routing in `run_agent_tool`.
- [feat] Implemented routing for 'build' tool, handling spec file paths and general rebuild commands.
- [feat] Implemented routing for 'implement' tool, using 'build' command with spec file path.
- [feat] Implemented routing for 'task_force' tool, including auto-generation of task IDs.
- [refactor] Added a docstring for `run_agent_tool` describing routing behavior.
- [style] Added an empty line for readability in `factory_supervisor.py`.
- [style] Imported `uuid` module locally in `run_agent_tool`.
- [fix] Fixed an issue with `task_force` where missing 'id' or 'goal' prevented execution and logged an error message.
- [feat] Added tool routing in `run_agent_tool`.
- [feat] Implemented routing for 'build' tool, handling spec file paths and general rebuild commands.
- [feat] Implemented routing for 'implement' tool, using 'build' command with spec file path.
- [feat] Added routing for 'task_force' tool, including auto-generation of task IDs.
- [refactor] Added a docstring for `run_agent_tool` describing routing behavior.
- [style] Added an empty line for readability in `factory_supervisor.py`.
- [style] Imported `uuid` module locally in `run_agent_tool`.
- [fix] Fixed an issue with `task_force` where missing 'id' or 'goal' prevented execution and logged an error message.
- [feat] Added tool routing in `run_agent_tool`.
- [feat] Implemented routing for 'build' tool, handling spec file paths and general rebuild commands.
- [feat] Implemented routing for 'implement' tool, using 'build' command with spec file path.
- [feat] Added routing for 'task_force' tool, including auto-generation of task IDs.
- [refactor] Added a docstring for `run_agent_tool` describing routing behavior.
- [style] Added an empty line for readability in `factory_supervisor.py`.
- [style] Imported `uuid` module locally in `run_agent_tool`.
- [fix] Fixed an issue with `task_force` where missing 'id' or 'goal' prevented execution and logged an error message.
- [feat] Added tool routing in `run_agent_tool`.
- [feat] Implemented routing for 'build' tool, handling spec file paths and general rebuild commands.
- [feat] Implemented routing for 'implement' tool, using 'build' command with spec file path.
- [feat] Added routing for 'task_force' tool, including auto-generation of task IDs.
- [refactor] Added a docstring for `run_agent_tool` describing routing behavior.
- [style] Added an empty line for readability in `factory_supervisor.py`.
- [style] Imported `uuid` module locally in `run_agent_tool`.
- [fix] Fixed an issue with `task_force` where missing 'id' or 'goal' prevented execution and logged an error message.
- [feat] Added tool routing in `run_agent_tool`.
- [feat] Implemented routing for 'build' tool, handling spec file paths and general rebuild commands.
- [feat] Implemented routing for 'implement' tool, using 'build' command with spec file path.
- [feat] Added tool routing in `run_agent_tool`.
- [feat] Implemented routing for 'build' tool, handling spec file paths and general rebuild commands.
- [feat] Implemented routing for 'implement' tool, using 'build' command with spec file path.
- [feat] Added tool routing in `run_agent_tool`.
- [feat] Implemented routing for 'build' tool, handling spec file paths and general rebuild commands.
- [feat] Implemented routing for 'implement' tool, using 'build' command with spec file path.
- [feat] Added tool routing in `run_agent_tool`.
- [feat] Implemented routing for 'build' tool, handling spec file paths and general rebuild commands.
- [feat] Implemented routing for 'implement' tool, using 'build' command with spec file path.
- [feat] Added tool routing in `run_agent_tool`.
- [feat] Implemented routing for 'build' tool, handling spec file paths and general rebuild commands.
- [feat] Implemented routing for 'implement' tool, using 'build' command with spec file path.
- [feat] Added routing for 'task_force' tool, including auto-generation of task IDs.
- [refactor] Added a docstring for `run_agent_tool` describing routing behavior.
- [style] Added an empty line for readability in `factory_supervisor.py`.
- [style] Imported `uuid` module locally in `run_agent_tool`.
- [fix] Fixed an issue with `task_force` where missing 'id' or 'goal' prevented execution and logged an error message.
- [feat] Added tool routing in `run_agent_tool`.
- [feat] Implemented routing for 'build' tool, handling spec file paths and general rebuild commands.
- [feat] Implemented routing for 'implement' tool, using 'build' command with spec file path.
- [feat] Added routing for 'task_force' tool, including auto-generation of task IDs.
- [refactor] Added a docstring for `run_agent_tool` describing routing behavior.
- [style] Added an empty line for readability in `factory_supervisor.py`.
- [style] Imported `uuid` module locally in `run_agent_tool`.
- [fix] Fixed an issue with `task_force` where missing 'id' or 'goal' prevented execution and logged an error message.
- [feat] Added tool routing in `run_agent_tool`.
- [feat] Implemented routing for 'build' tool, handling spec file paths and general rebuild commands.
- [feat] Implemented routing for 'implement' tool, using 'build' command with spec file path.
- [feat] Added routing for 'task_force' tool, including auto-generation of task IDs.
- [refactor] Added a docstring for `run_agent_tool` describing routing behavior.
- [style] Added an empty line for readability in `factory_supervisor.py`.
- [style] Imported `uuid` module locally in `run_agent_tool`.
- [fix] Fixed an issue with `task_force` where missing 'id' or 'goal' prevented execution and logged an error message.
- [feat] Added tool routing in `run_agent_tool`.
- [feat] Implemented routing for 'build' tool, handling spec file paths and general rebuild commands.
- [feat] Implemented routing for 'implement' tool, using 'build' command with spec file path.
- [feat] Added routing for 'task_force' tool, including auto-generation of task IDs.
- [refactor] Added a docstring for `run_agent_tool` describing routing behavior.
- [style] Added an empty line for readability in `factory_supervisor.py`.
- [style] Imported `uuid` module locally in `run_agent_tool`.
- [fix] Fixed an issue with `task_force` where missing 'id' or 'goal' prevented execution and logged an error message.
- [feat] Added tool routing in `run_agent_tool`.
- [feat] Implemented routing for 'build' tool, handling spec file paths and general rebuild commands.
- [feat] Implemented routing for 'implement' tool, using 'build' command with spec file path.
- [feat] Added tool routing in `run_agent_tool`.
- [feat] Implemented routing for 'build' tool, handling spec file paths and general rebuild commands.
- [feat] Implemented routing for 'implement' tool, using 'build' command with spec file path.
- [feat] Added tool routing in `run_agent_tool`.
- [feat] Implemented routing for 'build' tool, handling spec file paths and general rebuild commands.
- [feat] Implemented routing for 'implement' tool, using 'build' command with spec file path.
- [feat] Added tool routing in `run_agent_tool`.
- [feat] Implemented routing for 'build' tool, handling spec file paths and general rebuild commands.
- [feat] Implemented routing for 'implement' tool, using 'build' command with spec file path.
- [feat] Added tool routing in `run_agent_tool`.
- [feat] Implemented routing for 'build' tool, handling spec file paths and general rebuild commands.
- [feat] Implemented routing for 'implement' tool, using 'build' command with spec file path.
- [feat] Added tool routing in `run_agent_tool`.
- [feat] Implemented routing for 'build' tool, handling spec file paths and general rebuild commands.
- [feat] Implemented routing for 'implement' tool, using 'build' command with spec file path.
- [feat] Added tool routing in `run_agent_tool`.
- [feat] Implemented routing for 'build' tool, handling spec file paths and general rebuild commands.
- [feat] Implemented routing for 'implement' tool, using 'build' command with spec file path.
- [feat] Added tool routing in `run_agent_tool`.
- [feat] Implemented routing for 'build' tool, handling spec file paths and general rebuild commands.
- [feat] Implemented routing for 'implement' tool, using 'build' command with spec file path.
- [feat] Added tool routing in `run_agent_tool`.
- [feat] Implemented routing for 'build' tool, handling spec file paths and general rebuild commands.
- [feat] Implemented routing for 'implement' tool, using 'build' command with spec file path.
- [feat] Added routing for 'task_force' tool, including auto-generation of task IDs.
- [refactor] Added a docstring for `run_agent_tool` describing routing behavior.
- [style] Added an empty line for readability in `factory_supervisor.py`.
- [style] Imported `uuid` module locally in `run_agent_tool`.
- [fix] Fixed an issue with `task_force` where missing 'id' or 'goal' prevented execution and logged an error message.
- [feat] Added tool routing in `run_agent_tool`.
- [feat] Implemented routing for 'build' tool, handling spec file paths and general rebuild commands.
- [feat] Implemented routing for 'implement' tool, using 'build' command with spec file path.
- [feat] Added routing for 'task_force' tool, including auto-generation of task IDs.
- [refactor] Added a docstring for `run_agent_tool` describing routing behavior.
- [style] Added an empty line for readability in `factory_supervisor.py`.
- [style] Imported `uuid` module locally in `run_agent_tool`.
- [fix] Fixed an issue with `task_force` where missing 'id' or 'goal' prevented execution and logged an error message.
- [feat] Added tool routing in `run_agent_tool`.
- [feat] Implemented routing for 'build' tool, handling spec file paths and general rebuild commands.
- [feat] Implemented routing for 'implement' tool, using 'build' command with spec file path.
- [feat] Added routing for 'task_force' tool, including auto-generation of task IDs.
- [refactor] Added a docstring for `run_agent_tool` describing routing behavior.
- [style] Added an empty line for readability in `factory_supervisor.py`.
- [style] Imported `uuid` module locally in `run_agent_tool`.
- [fix] Fixed an issue with `task_force` where missing 'id' or 'goal' prevented execution and logged an error message.
- [feat] Added tool routing in `run_agent_tool`.
- [feat] Implemented routing for 'build' tool, handling spec file paths and general rebuild commands.
- [feat] Implemented routing for 'implement' tool, using 'build' command with spec file path.
- [feat] Added routing for 'task_force' tool, including auto-generation of task IDs.
- [refactor] Added a docstring for `run_agent_tool` describing routing behavior.
- [style] Added an empty line for readability in `factory_supervisor.py`.
- [style] Imported `uuid` module locally in `run_agent_tool`.
- [fix] Fixed an issue with `task_force` where missing 'id' or 'goal' prevented execution and logged an error message.
- [feat] Added tool routing in `run_agent_tool`.
- [feat] Implemented routing for 'build' tool, handling spec file paths and general rebuild commands.
- [feat] Implemented routing for 'implement' tool, using 'build' command with spec file path.
- [feat] Added routing for 'task_force' tool, including auto-generation of task IDs.
- [refactor] Added a docstring for `run_agent_tool` describing routing behavior.
- [style] Added an empty line for readability in `factory_supervisor.py`.
- [style] Imported `uuid` module locally in `run_agent_tool`.
- [fix] Fixed an issue with `task_force` where missing 'id' or 'goal' prevented execution and logged an error message.
- [feat] Added tool routing in `run_agent_tool`.
- [feat] Implemented routing for 'build' tool, handling spec file paths and general rebuild commands.
- [feat] Implemented routing for 'implement' tool, using 'build' command with spec file path.
- [feat] Added routing for 'task_force' tool, including auto-generation of task IDs.
- [refactor] Added a docstring for `run_agent_tool` describing routing behavior.
- [style] Added an empty line for readability in `factory_supervisor.py`.
- [style] Imported `uuid` module locally in `run_agent_tool`.
- [fix] Fixed an issue with `task_force` where missing 'id' or 'goal' prevented execution and logged an error message.
- [feat] Added tool routing in `run_agent_tool`.
- [feat] Implemented routing for 'build' tool, handling spec file paths and general rebuild commands.
- [feat] Implemented routing for 'implement' tool, using 'build' command with spec file path.
- [feat] Added routing for 'task_force' tool, including auto-generation of task IDs.
- [refactor] Added a docstring for `run_agent_tool` describing routing behavior.
- [style] Added an empty line for readability in `factory_supervisor.py`.
- [style] Imported `uuid` module locally in `run_agent_tool`.
- [fix] Fixed an issue with `task_force` where missing 'id' or 'goal' prevented execution and logged an error message.
- [feat] Added tool routing in `run_agent_tool`.
- [feat] Implemented routing for 'build' tool, handling spec file paths and general rebuild commands.
- [feat] Implemented routing for 'implement' tool, using 'build' command with spec file path.
- [feat] Added routing for 'task_force' tool, including auto-generation of task IDs.
- [refactor] Added a docstring for `run_agent_tool` describing routing behavior.
- [style] Added an empty line for readability in `factory_supervisor.py`.
- [style] Imported `uuid` module locally in `run_agent_tool`.
- [fix] Fixed an issue with `task_force` where missing 'id' or 'goal' prevented execution and logged an error message.
- [feat] Added tool routing in `run_agent_tool`.
- [feat] Implemented routing for 'build' tool, handling spec file paths and general rebuild commands.
- [feat] Implemented routing for 'implement' tool, using 'build' command with spec file path.
- [feat] Added routing for 'task_force' tool, including auto-generation of task IDs.
- [refactor] Added a docstring for `run_agent_tool` describing routing behavior.
- [style] Added an empty line for readability in `factory_supervisor.py`.
- [style] Imported `uuid` module locally in `run_agent_tool`.
- [fix] Fixed an issue with `task_force` where missing 'id' or 'goal' prevented execution and logged an error message.
- [feat] Added tool routing in `run_agent_tool`.
- [feat] Implemented routing for 'build' tool, handling spec file paths and general rebuild commands.
- [feat] Implemented routing for 'implement' tool, using 'build' command with spec file path.
- [feat] Added routing for 'task_force' tool, including auto-generation of task IDs.
- [refactor] Added a docstring for `run_agent_tool` describing routing behavior.
- [style] Added an empty line for readability in `factory_supervisor.py`.
- [style] Imported `uuid` module locally in `run_agent_tool`.
- [fix] Fixed an issue with `task_force` where missing 'id' or 'goal' prevented execution and logged an error message.
- [feat] Added tool routing in `run_agent_tool`.
- [feat] Implemented routing for 'build' tool, handling spec file paths and general rebuild commands.
- [feat] Implemented routing for 'implement' tool, using 'build' command with spec file path.
- [feat] Added routing for 'task_force' tool, including auto-generation of task IDs.
- [refactor] Added a docstring for `run_agent_tool` describing routing behavior.
- [style] Added an empty line for readability in `factory_supervisor.py`.
- [style] Imported `uuid` module locally in `run_agent_tool`.
- [fix] Fixed an issue with `task_force` where missing 'id' or 'goal' prevented execution and logged an error message.
- [feat] Added tool routing in `run_agent_tool`.
- [feat] Implemented routing for 'build' tool, handling spec file paths and general rebuild commands.
- [feat] Implemented routing for 'implement' tool, using 'build' command with spec file path.
- [feat] Added routing for 'task_force' tool, including auto-generation of task IDs.
- [refactor] Added a docstring for `run_agent_tool` describing routing behavior.
- [style] Added an empty line for readability in `factory_supervisor.py`.
- [style] Imported `uuid` module locally in `run_agent_tool`.
- [fix] Fixed an issue with `task_force` where missing 'id' or 'goal' prevented execution and logged an error message.
- [feat] Added tool routing in `run_agent_tool`.
- [feat] Implemented routing for 'build' tool, handling spec file paths and general rebuild commands.
- [feat] Implemented routing for 'implement' tool, using 'build' command with spec file path.
- [feat] Added routing for 'task_force' tool, including auto-generation of task IDs.
- [refactor] Added a docstring for `run_agent_tool` describing routing behavior.
- [style] Added an empty line for readability in `factory_supervisor.py`.
- [style] Imported `uuid` module locally in `run_agent_tool`.
- [fix] Fixed an issue with `task_force` where missing 'id' or 'goal' prevented execution and logged an error message.
- [feat] Added tool routing in `run_agent_tool`.
- [feat] Implemented routing for 'build' tool, handling spec file paths and general rebuild commands.
- [feat] Implemented routing for 'implement' tool, using 'build' command with spec file path.
- [feat] Added routing for 'task_force' tool, including auto-generation of task IDs.
- [refactor] Added a docstring for `run_agent_tool` describing routing behavior.
- [style] Added an empty line for readability in `factory_supervisor.py`.
- [style] Imported `uuid` module locally in `run_agent_tool`.
- [fix] Fixed an issue with `task_force` where missing 'id' or 'goal' prevented execution and logged an error message.
- [feat] Added tool routing in `run_agent_tool`.
- [feat] Implemented routing for 'build' tool, handling spec file paths and general rebuild commands.
- [feat] Implemented routing for 'implement' tool, using 'build' command with spec file path.
- [feat] Added routing for 'task_force' tool, including auto-generation of task IDs.
- [refactor] Added a docstring for `run_agent_tool` describing routing behavior.
- [style] Added an empty line for readability in `factory_supervisor.py`.
- [style] Imported `uuid` module locally in `run_agent_tool`.
- [fix] Fixed an issue with `task_force` where missing 'id' or 'goal' prevented execution and logged an error message.
- [feat] Added tool routing in `run_agent_tool`.
- [feat] Implemented routing for 'build' tool, handling spec file paths and general rebuild commands.
- [feat] Implemented routing for 'implement' tool, using 'build' command with spec file path.
- [feat] Added routing for 'task_force' tool, including auto-generation of task IDs.
- [refactor] Added a docstring for `run_agent_tool` describing routing behavior.
- [style] Added an empty line for readability in `factory_supervisor.py`.
- [style] Imported `uuid` module locally in `run_agent_tool`.
- [fix] Fixed an issue with `task_force` where missing 'id' or 'goal' prevented execution and logged an error message.
- [feat] Added tool routing in `run_agent_tool`.
- [feat] Implemented routing for 'build' tool, handling spec file paths and general rebuild commands.
- [feat] Implemented routing for 'implement' tool, using 'build' command with spec file path.
- [feat] Added routing for 'task_force' tool, including auto-generation of task IDs.
- [refactor] Added a docstring for `run_agent_tool` describing routing behavior.
- [style] Added an empty line for readability in `factory_supervisor.py`.
- [style] Imported `uuid` module locally in `run_agent_tool`.
- [fix] Fixed an issue with `task_force` where missing 'id' or 'goal' prevented execution and logged an error message.
- [feat] Added tool routing in `run_agent_tool`.
- [feat] Implemented routing for 'build' tool, handling spec file paths and general rebuild commands.
- [feat] Implemented routing for 'implement' tool, using 'build' command with spec file path.
- [feat] Added routing for 'task_force' tool, including auto-generation of task IDs.
- [refactor] Added a docstring for `run_agent_tool` describing routing behavior.
- [style] Added an empty line for readability in `factory_supervisor.py`.
- [style] Imported `uuid` module locally in `run_agent_tool`.
- [fix] Fixed an issue with `task_force` where missing 'id' or 'goal' prevented execution and logged an error message.
- [feat] Added tool routing in `run_agent_tool`.
- [feat] Implemented routing for 'build' tool, handling spec file paths and general rebuild commands.
- [feat] Implemented routing for 'implement' tool, using 'build' command with spec file path.
- [feat] Added routing for 'task_force' tool, including auto-generation of task IDs.
- [refactor] Added a docstring for `run_agent_tool` describing routing behavior.
- [style] Added an empty line for readability in `factory_supervisor.py`.
- [style] Imported `uuid` module locally in `run_agent_tool`.
- [fix] Fixed an issue with `task_force` where missing 'id' or 'goal' prevented execution and logged an error message.
- [feat] Added tool routing in `run_agent_tool`.
- [feat] Implemented routing for 'build' tool, handling spec file paths and general rebuild commands.
- [feat] Implemented routing for 'implement' tool, using 'build' command with spec file path.
- [feat] Added routing for 'task_force' tool, including auto-generation of task IDs.
- [refactor] Added a docstring for `run_agent_tool` describing routing behavior.
- [style] Added an empty line for readability in `factory_supervisor.py`.
- [style] Imported `uuid` module locally in `run_agent_tool`.
- [fix] Fixed an issue with `task_force` where missing 'id' or 'goal' prevented execution and logged an error message.
- [feat] Added tool routing in `run_agent_tool`.
- [feat] Implemented routing for 'build' tool, handling spec file paths and general rebuild commands.
- [feat] Implemented routing for 'implement' tool, using 'build' command with spec file path.
- [feat] Added routing for 'task_force' tool, including auto-generation of task IDs.
- [refactor] Added a docstring for `run_agent_tool` describing routing behavior.
- [style] Added an empty line for readability in `factory_supervisor.py`.
- [style] Imported `uuid` module locally in `run_agent_tool`.
- [fix] Fixed an issue with `task_force` where missing 'id' or 'goal' prevented execution and logged an error message.
- [feat] Added tool routing in `run_agent_tool`.
- [feat] Implemented routing for 'build' tool, handling spec file paths and general rebuild commands.
- [feat] Implemented routing for 'implement' tool, using 'build' command with spec file path.
- [feat] Added routing for 'task_force' tool, including auto-generation of task IDs.
- [refactor] Added a docstring for `run_agent_tool` describing routing behavior.
- [style] Added an empty line for readability in `factory_supervisor.py`.
- [style] Imported `uuid` module locally in `run_agent_tool`.
- [fix] Fixed an issue with `task_force` where missing 'id' or 'goal' prevented execution and logged an error message.
- [feat] Added tool routing in `run_agent_tool`.
- [feat] Implemented routing for 'build' tool, handling spec file paths and general rebuild commands.
- [feat] Implemented routing for 'implement' tool, using 'build' command with spec file path.
- [feat] Added routing for 'task_force' tool, including auto-generation of task IDs.
- [refactor] Added a docstring for `run_agent_tool` describing routing behavior.
- [style] Added an empty line for readability in `factory_supervisor.py`.
- [style] Imported `uuid` module locally in `run_agent_tool`.
- [fix] Fixed an issue with `task_force` where missing 'id' or 'goal' prevented execution and logged an error message.
- [feat] Added tool routing in `run_agent_tool`.
- [feat] Implemented routing for 'build' tool, handling spec file paths and general rebuild commands.
- [feat] Implemented routing for 'implement' tool, using 'build' command with spec file path.
- [feat] Added routing for 'task_force' tool, including auto-generation of task IDs.
- [refactor] Added a docstring for `run_agent_tool` describing routing behavior.
- [style] Added an empty line for readability in `factory_supervisor.py`.
- [style] Imported `uuid` module locally in `run_agent_tool`.
- [fix] Fixed an issue with `task_force` where missing 'id' or 'goal' prevented execution and logged an error message.
- [feat] Added tool routing in `run_agent_tool`.
- [feat] Implemented routing for 'build' tool, handling spec file paths and general rebuild commands.
- [feat] Implemented routing for 'implement' tool, using 'build' command with spec file path.
- [feat] Added routing for 'task_force' tool, including auto-generation of task IDs.
- [refactor] Added a docstring for `run_agent_tool` describing routing behavior.
- [style] Added an empty line for readability in `factory_supervisor.py`.
- [style] Imported `uuid` module locally in `run_agent_tool`.
- [fix] Fixed an issue with `task_force` where missing 'id' or 'goal' prevented execution and logged an error message.
- [feat] Added tool routing in `run_agent_tool`.
- [feat] Implemented routing for 'build' tool, handling spec file paths and general rebuild commands.
- [feat] Implemented routing for 'implement' tool, using 'build' command with spec file path.
- [feat] Added routing for 'task_force' tool, including auto-generation of task IDs.
- [refactor] Added a docstring for `run_agent_tool` describing routing behavior.
- [style] Added an empty line for readability in `factory_supervisor.py`.
- [style] Imported `uuid` module locally in `run_agent_tool`.
- [fix] Fixed an issue with `task_force` where missing 'id' or 'goal' prevented execution and logged an error message.
- [feat] Added tool routing in `run_agent_tool`.
- [feat] Implemented routing for 'build' tool, handling spec file paths and general rebuild commands.
- [feat] Implemented routing for 'implement' tool, using 'build' command with spec file path.
- [feat] Added routing for 'task_force' tool, including auto-generation of task IDs.
- [refactor] Added a docstring for `run_agent_tool` describing routing behavior.
- [style] Added an empty line for readability in `factory_supervisor.py`.
- [style] Imported `uuid` module locally in `run_agent_tool`.
- [fix] Fixed an issue with `task_force` where missing 'id' or 'goal' prevented execution and logged an error message.
- [feat] Added tool routing in `run_agent_tool`.
- [feat] Implemented routing for 'build' tool, handling spec file paths and general rebuild commands.
- [feat] Implemented routing for 'implement' tool, using 'build' command with spec file path.
- [feat] Added routing for 'task_force' tool, including auto-generation of task IDs.
- [refactor] Added a docstring for `run_agent_tool` describing routing behavior.
- [style] Added an empty line for readability in `factory_supervisor.py`.
- [style] Imported `uuid` module locally in `run_agent_tool`.
- [fix] Fixed an issue with `task_force` where missing 'id' or 'goal' prevented execution and logged an error message.
- [feat] Added tool routing in `run_agent_tool`.
- [feat] Implemented routing for 'build' tool, handling spec file paths and general rebuild commands.
- [feat] Implemented routing for 'implement' tool, using 'build' command with spec file path.
- [feat] Added routing for 'task_force' tool, including auto-generation of task IDs.
- [refactor] Added a docstring for `run_agent_tool` describing routing behavior.
- [style] Added an empty line for readability in `factory_supervisor.py`.
- [style] Imported `uuid` module locally in `run_agent_tool`.
- [fix] Fixed an issue with `task_force` where missing 'id' or 'goal' prevented execution and logged an error message.
- [feat] Added tool routing in `run_agent_tool`.
- [feat] Implemented routing for 'build' tool, handling spec file paths and general rebuild commands.
- [feat] Implemented routing for 'implement' tool, using 'build' command with spec file path.
- [feat] Added routing for 'task_force' tool, including auto-generation of task IDs.
- [refactor] Added a docstring for `run_agent_tool` describing routing behavior.
- [style] Added an empty line for readability in `factory_supervisor.py`.
- [style] Imported `uuid` module locally in `run_agent_tool`.
- [fix] Fixed an issue with `task_force` where missing 'id' or 'goal' prevented execution and logged an error message.
- [feat] Added tool routing in `run_agent_tool`.
- [feat] Implemented routing for 'build' tool, handling spec file paths and general rebuild commands.
- [feat] Implemented routing for 'implement' tool, using 'build' command with spec file path.
- [feat] Added routing for 'task_force' tool, including auto-generation of task IDs.
- [refactor] Added a docstring for `run_agent_tool` describing routing behavior.
- [style] Added an empty line for readability in `factory_supervisor.py`.
- [style] Imported `uuid` module locally in `run_agent_tool`.
- [fix] Fixed an issue with `task_force` where missing 'id' or 'goal' prevented execution and logged an error message.
- [feat] Added tool routing in `run_agent_tool`.
- [feat] Implemented routing for 'build' tool, handling spec file paths and general rebuild commands.
- [feat] Implemented routing for 'implement' tool, using 'build' command with spec file path.
- [feat] Added routing for 'task_force' tool, including auto-generation of task IDs.
- [refactor] Added a docstring for `run_agent_tool` describing routing behavior.
- [style] Added an empty line for readability in `factory_supervisor.py`.
- [style] Imported `uuid` module locally in `run_agent_tool`.
- [fix] Fixed an issue with `task_force` where missing 'id' or 'goal' prevented execution and logged an error message.
- [feat] Added tool routing in `run_agent_tool`.
- [feat] Implemented routing for 'build' tool, handling spec file paths and general rebuild commands.
- [feat] Implemented

## [v4.1] — 2026-02-19
## [v4.1]

- [feat] Added tool routing in `run_agent_tool`.
- [feat] Implemented routing for 'build' tool, handling spec file paths and general rebuild commands.
- [feat] Added routing for 'implement' tool, using 'build' command with spec file path.
- [feat] Implemented routing for 'task_force' tool, including auto-generation of task IDs.
- [refactor] Added a docstring for `run_agent_tool` describing routing behavior.
- [style] Added an empty line for readability in `factory_supervisor.py`.
- [style] Imported `uuid` module locally in `run_agent_tool`.
- [fix] Fixed an issue with `task_force` where missing 'id' or 'goal' prevented execution and logged an error message.

## [v4.1] — 2026-02-19
## [v4.1]

- [feat] Added tool routing in `run_agent_tool`.
- [feat] Implemented routing for 'build' tool, handling spec file paths and general rebuild commands.
- [feat] Added routing for 'implement' tool, using 'build' command with spec file path.
- [feat] Implemented routing for 'task_force' tool, including auto-generation of task IDs.
- [refactor] Added a docstring for `run_agent_tool` describing routing behavior.
- [style] Added an empty line for readability in `factory_supervisor.py`.
- [style] Imported `uuid` module locally in `run_agent_tool`.
- [fix] Fixed an issue with `task_force` where missing 'id' or 'goal' prevented execution and logged an error message.

## [v4.1] — 2026-02-19
- [feat] Added tool routing in `run_agent_tool`.
- [feat] Implemented routing for 'build' tool, handling spec file paths and general rebuild commands.
- [feat] Added routing for 'implement' tool, using 'build' command with spec file path.
- [feat] Implemented routing for 'task_force' tool, including auto-generation of task IDs.
- [refactor] Added a docstring for `run_agent_tool` describing routing behavior.
- [style] Added an empty line for readability in `factory_supervisor.py`.
- [style] Imported `uuid` module locally in `run_agent_tool`.
- [fix] Fixed an issue with `task_force` where missing 'id' or 'goal' prevented execution and logged an error message.

## [v4.1] — 2026-02-19
### Documentation Updates

-   [feat] Updated architecture documentation to reflect current application features.
-   [feat] Added descriptions for ingestion status.
-   [feat] Added descriptions for product card visual cues.
-   [refactor] Improved description of `useConductorCatalog` hook.
-   [refactor] Enhanced `useJITIntelligence` description to include returned data.
-   [refactor] Added backend API endpoint descriptions.
-   [refactor] Minor wording adjustments and clarifications throughout the document.

# Changelog

