# ⚙️ 02_BACKEND_PIPELINE.md

**Role:** Offline Data Generation
**Execution:** `python3 forge_backbone.py`

## 🏭 The Factory Structure
The backend is strictly for offline data generation. It contains:

### 🧠 Core Generators
- `backend/analyze_products_for_categories.py`
- `backend/config/__init__.py`
- `backend/config/brand_maps.py`
- `backend/core/__init__.py`
- `backend/core/config.py`
- `backend/daily_update.py`
- `backend/forge_backbone.py`
- `backend/generate_category_thumbnails.py`
- `backend/generate_final_category_thumbnails.py`
- `backend/generate_flagship_thumbnails.py`
- `backend/generate_frontend_json.py`
- `backend/generate_spectrum_brand_map.py`
- `backend/heartbeat.py`
- `backend/mass_ingest_protocol.py`
- `backend/refine_skeleton.py`
- `backend/regenerate_frontend.py`
- `backend/run_genesis.py`
- `backend/run_single_brand.py`
- `backend/thumbnail_pipeline.py`
- `backend/update_manifests.py`

### 🤖 Services & Scrapers
- `backend/services/ai_pipeline.py`
- `backend/services/boss_scraper.py`
- `backend/services/catalog_manager.py`
- `backend/services/catalog_verifier.py`
- `backend/services/frontend_normalizer.py`
- `backend/services/genesis_builder.py`
- `backend/services/global_radar.py`
- `backend/services/halilit_brand_registry.py`
- `backend/services/halilit_client.py`
- `backend/services/halilit_direct_scraper.py`
- `backend/services/local_blueprint_loader.py`
- `backend/services/moog_scraper.py`
- `backend/services/nord_scraper.py`
- `backend/services/official_brand_base.py`
- `backend/services/parsers/__init__.py`
- `backend/services/parsers/cable_parser.py`
- `backend/services/relationship_engine.py`
- `backend/services/roland_scraper.py`
- `backend/services/scraper_enhancements.py`
- `backend/services/super_explorer.py`
- `backend/services/unified_ingestor.py`
- `backend/services/visual_extractor.py`
- `backend/services/visual_factory.py`

### 📦 Data Models
- `backend/models/__init__.py`
- `backend/models/brand_taxonomy.py`
- `backend/models/category_consolidator.py`
- `backend/models/product_hierarchy.py`
- `backend/models/taxonomy_registry.py`

## 📄 Published Production Catalogs
These files are the ONLY source of truth for the frontend:
- `-eaw-eastern-acoustic-works-.json`
- `accessories.json`
- `adam-audio.json`
- `adams.json`
- `akai-professional.json`
- `allen-heath.json`
- `ampeg.json`
- `amphion.json`
- `antigua.json`
- `asm.json`
- `austrian-audio.json`
- `bespeco.json`
- `bohemian-ukuleles-guitars-basses.json`
- `boss.json`
- `breedlove-guitars.json`
- `cordoba-guitars.json`
- `dixon.json`
- `drumdots.json`
- `drums-percussion.json`
- `dynaudio.json`
- `eaw-eastern-acoustic-works.json`
- `eden.json`
- `encore.json`
- `esp.json`
- `eve-audio.json`
- `expressive-e.json`
- `foxgear-guitar-effects-and-pedals.json`
- `fusion.json`
- `fzone.json`
- `gon-bops-percussion.json`
- `guild.json`
- `guitars-bass.json`
- `headliner-la-equipment-stands-.json`
- `headliner-la-equipment-stands.json`
- `headrush-fx.json`
- `heritage-audio.json`
- `hiwatt.json`
- `index.json`
- `innovative-percussion.json`
- `jasmine-guitars.json`
- `keys-production.json`
- `krk-systems.json`
- `lag-guitars.json`
- `live-dj.json`
- `lynx.json`
- `m-audio.json`
- `mackie.json`
- `maestro-guitar-pedals-and-effects.json`
- `magma.json`
- `marimba-one.json`
- `maton-guitars.json`
- `maybach.json`
- `medeli.json`
- `mjc-ironworks.json`
- `montarbo.json`
- `moog.json`
- `nord.json`
- `oberheim.json`
- `on-stage.json`
- `oscar-schmidt-acoustic-guitars-.json`
- `oscar-schmidt-acoustic-guitars.json`
- `paiste-cymbals.json`
- `pearl.json`
- `perri-s-leathers.json`
- `presonus.json`
- `rapier-33-electric-guitars.json`
- `rcf.json`
- `remo.json`
- `rhythm-tech.json`
- `rogers.json`
- `roland-commercial.json`
- `roland.json`
- `santos-martinez.json`
- `show.json`
- `solar-guitars.json`
- `spector.json`
- `steinberg-.json`
- `steinberg.json`
- `studio-logic.json`
- `studio-recording.json`
- `system_manifest.json`
- `taxonomy.json`
- `tombo.json`
- `topp-pro.json`
- `turkish.json`
- `universal-audio.json`
- `v-moda.json`
- `vintage.json`
- `warm-audio.json`
- `washburn.json`
- `xotic.json`
- `xvive.json`

## ⚠️ Rules
- The backend is **NOT** deployed.
- `main.py` is for DEV validation only.
- Frontend MUST read from JSON files, NEVER from localhost API.
