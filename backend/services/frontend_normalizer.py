from typing import List, Dict, Any
import os

class FrontendNormalizer:
    
    @staticmethod
    def normalize_product(product: Dict[str, Any]) -> Dict[str, Any]:
        """
        Transforms Backend Product -> Premium Frontend Payload
        """
        # --- Helper to safely get deep values ---
        def get_val(obj, path, default=None):
            try:
                for key in path.split('.'):
                    obj = obj.get(key, {})
                return obj if obj else default
            except:
                return default

        # 1. Core Identity
        p_id = product.get('id')
        brand = product.get('brand', 'Unknown').upper()
        # Prefer "Official" name, fallback to commercial
        name = (get_val(product, 'official_knowledge.name') or 
                get_val(product, 'commercial.name') or 
                product.get('name') or "Unknown Model")

        # 2. Smart Categorization (Tribe)
        tribe_id = product.get('tribe_id') or product.get('category', 'general').lower()

        # 3. Rich Content Extraction
        description = get_val(product, 'official_knowledge.description') or product.get('description', '')
        
        # --- NEW: Document Extraction (PDFs) ---
        downloads = []
        raw_manuals = get_val(product, 'official_knowledge.official_manuals') or []
        # If it's a simple list of strings
        if isinstance(raw_manuals, list):
            for m in raw_manuals:
                if isinstance(m, str) and m.lower().endswith('.pdf'):
                    downloads.append({"title": "User Manual", "url": m})
                elif isinstance(m, dict):
                    downloads.append(m)

        # 4. Intelligence (Filters & Tags)
        # We generate tags that the frontend uses for the 1176 buttons
        tags = FrontendNormalizer._generate_smart_tags(name, description, tribe_id)

        # 5. Visuals (High Res Priority)
        image_url = "/assets/placeholders/no-img.png"
        media_thumb = get_val(product, 'media.thumbnail')
        official_img = get_val(product, 'official_knowledge.image_url')
        
        if official_img: 
            image_url = official_img
        elif media_thumb and "placeholder" not in media_thumb:
            image_url = media_thumb

        # 6. Pricing (The Halilit Connection)
        price = get_val(product, 'commercial.price') or get_val(product, 'pricing.regular_price') or 0

        return {
            "id": p_id,
            "brand": brand,
            "name": name,
            "sku": get_val(product, 'commercial.sku') or "N/A",
            "price": price,
            "status": "ACTIVE",
            "tribe_id": tribe_id,
            
            # THE BRAIN: Tags for filtering
            "tags": tags, 
            
            # Content
            "description": description,
            "specs_preview": FrontendNormalizer._generate_preview_specs(product, tribe_id),
            "downloads": downloads, # <--- NEW: Docs for the UI
            
            # Visuals
            "image_url": image_url,
            "logo_url": f"/assets/logos/{brand.lower().replace(' ', '-')}_logo.png"
        }

    @staticmethod
    def _generate_smart_tags(name: str, desc: str, cat: str) -> List[str]:
        """Scans text to apply intelligent filter tags."""
        tags = set()
        text = (str(name) + " " + str(desc)).lower()
        
        # --- Universal Tags ---
        if "usb" in text: tags.add("USB")
        if "bluetooth" in text: tags.add("Bluetooth")
        
        # --- Category Specific ---
        if "keys" in cat: # keys-production
            if "analog" in text: tags.add("Analog")
            if "digital" in text: tags.add("Digital")
            if "synth" in text: tags.add("Synthesizer")
            if "stage piano" in text: tags.add("Stage Piano")
            if "weighted" in text: tags.add("Weighted Keys")
            
        elif "drums" in cat: # drums-percussion
            if "electronic" in text: tags.add("Electronic")
            if "acoustic" in text: tags.add("Acoustic")
            if "snare" in text: tags.add("Snare")
            if "mesh" in text: tags.add("Mesh Head")

        elif "guitars" in cat: # guitars-bass
            if "electric" in text: tags.add("Electric")
            if "acoustic" in text: tags.add("Acoustic")
            if "bass" in text: tags.add("Bass")
            if "pedal" in text: tags.add("Pedals")
            if "amp" in text: tags.add("Amps")

        elif "studio" in cat: # studio-recording
            if "monitor" in text: tags.add("Monitors")
            if "interface" in text: tags.add("Audio Interface")
            if "condenser" in text: tags.add("Condenser Mic")
            if "dynamic" in text: tags.add("Dynamic Mic")
            
        elif "live" in cat or "dj" in cat: # live-dj
            if "mixer" in text: tags.add("Mixer")
            if "monitor" in text: tags.add("Stage Monitor")
            if "pa" in text: tags.add("PA System")
            if "controller" in text: tags.add("DJ Controller")

        return sorted(list(tags))

    @staticmethod
    def _generate_preview_specs(product, category):
        # Returns [ {"key": "Type", "val": "Analog"}, ... ]
        specs = []
        raw = product.get('official_knowledge', {}).get('specs', {})
        if not raw: return []
        
        # Simple extraction of top 3 items
        count = 0
        for k, v in raw.items():
            if count >= 3: break
            if isinstance(v, (str, int, float)) and len(str(v)) < 20:
                specs.append({"key": k.upper(), "val": str(v)})
                count += 1
        return specs
