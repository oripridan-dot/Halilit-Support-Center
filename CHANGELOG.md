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

