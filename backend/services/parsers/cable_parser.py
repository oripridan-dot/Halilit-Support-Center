import re

def normalize_connector(text):
    if not text:
        return "Unknown"
    text = text.lower()
    
    # XLR Logic
    if "xlr" in text:
        if "female" in text: return "XLR-Female"
        if "male" in text: return "XLR-Male"
        return "XLR-Male" # Default generic 

    # TRS / Stereo
    if "trs" in text or "stereo jack" in text or "balanced phone" in text: return "TRS-1/4"
    if "stereo" in text and ("1/4" in text or "phone" in text): return "TRS-1/4"
    
    # TS / Mono
    if "ts" in text or "mono jack" in text: return "TS-1/4"
    if "phone jack" in text: return "TS-1/4" # Ambiguous, usually TS
    if "1/4-inch" in text and "mono" in text: return "TS-1/4"
    
    # Generic 1/4 (Assume TS if not specified, unless context implies otherwise)
    if "1/4-inch" in text or "1/4\"" in text:
         if "stereo" in text: return "TRS-1/4"
         return "TS-1/4"

    # RCA
    if "rca" in text or "phono" in text: return "RCA"
    
    # DB25
    if "db25" in text or "d-sub" in text: return "DB25"
    
    # USB
    if "usb-c" in text or "usb type-c" in text: return "USB-C"
    if "usb-a" in text: return "USB-A"
    if "usb-b" in text: return "USB-B"
    if "micro-usb" in text: return "Micro-USB"
    
    # Mini Jack / 3.5mm
    if "3.5mm" in text or "mini jack" in text or "1/8-inch" in text or "mini-phone" in text:
        if "stereo" in text or "trs" in text: return "TRS-3.5mm"
        return "TS-3.5mm"
        
    # MIDI
    if "midi" in text and "din" in text: return "MIDI-DIN"
    if "midi" in text: return "MIDI-DIN"

    return "Unknown"

def extract_connectivity(name, description=""):
    """
    Extracts ConnectivityDNA from product name/desc using regex strategies.
    Strategies:
    1. Split name (XLR to TRS)
    2. Regex search in description "X to Y"
    3. Infer from Product Category names (e.g. "Instrument Cable" -> TS-TS)
    """
    if not name:
        return None
        
    name_clean = name.lower()
    desc_clean = description.lower() if description else ""
    full_text = f"{name_clean} {desc_clean}" # Search everything
    
    # 1. Determine Type
    type_ = 'cable' # Default
    if "adapter" in name_clean: type_ = 'adapter'
    elif "interface" in name_clean: type_ = 'interface'
    elif "controller" in name_clean: type_ = 'controller'
    elif "headphone" in name_clean: type_ = 'headphones'
    
    conn_a = "Unknown"
    conn_b = "Unknown"
    
    # STRATEGY 1: Explicit Split in Name
    splitter_regex = r"\s+(?:to|->|-|/)\s+"
    parts = re.split(splitter_regex, name_clean)
    
    if len(parts) >= 2:
        c1 = normalize_connector(parts[0])
        c2 = normalize_connector(parts[1])
        if c1 != "Unknown" and c2 != "Unknown":
            conn_a, conn_b = c1, c2

    # STRATEGY 2: Regex Hunt in Full Text
    # Look for "X to Y" patterns where X and Y are connectors
    if conn_a == "Unknown" or conn_b == "Unknown":
        # Broad pattern to capture connector phrases
        # e.g. "1/4-inch stereo phone" -> matches
        connector_terms = r"(xlr|trs|ts|rca|db25|usb-[abc]|1/4-inch|1/4\"|1/8-inch|3\.5mm|midi|phone jack|stereo jack|mono jack|minijack|mini jack)"
        
        regex = rf"({connector_terms}[^,.\n]*?)\s+(?:to|->|-|into)\s+({connector_terms}[^,.\n]*)"
        
        match = re.search(regex, full_text)
        if match:
            # Normalize the captured phrase (e.g. "1/4-inch stereo female")
            c1 = normalize_connector(match.group(1))
            c2 = normalize_connector(match.group(2))
            
            if c1 != "Unknown" and c2 != "Unknown":
                conn_a, conn_b = c1, c2

    # STRATEGY 3: Inference from Product Type Names (The "Universal DNA" Logic)
    if conn_a == "Unknown" and conn_b == "Unknown":
        if "instrument cable" in full_text or "1/4-inch connector" in full_text:
            # Instrument cables are typically unbalanced TS connections
            conn_a = "TS-1/4"
            conn_b = "TS-1/4"
        elif "midi cable" in full_text or "midi" in full_text and ("din" in full_text or "5-pin" in full_text):
            conn_a = "MIDI-DIN"
            conn_b = "MIDI-DIN"
        elif "microphone cable" in full_text or "mic cable" in full_text:
            conn_a = "XLR-Male"
            conn_b = "XLR-Female"
        elif "pedal cable" in full_text or "patch cable" in full_text:
            # Usually TS patch cables
            conn_a = "TS-1/4"
            conn_b = "TS-1/4"
        elif "speaker cable" in full_text or "speakon" in full_text:
            conn_a = "Speakon"
            conn_b = "Speakon"
        elif "usb" in name_clean: # Keep USB name check as description mentions USB meant for other things often
            conn_a = "USB-A" # Assumption
            if "usb-c" in full_text: conn_b = "USB-C"
            elif "micro-usb" in full_text: conn_b = "Micro-USB"
            elif "usb-b" in full_text: conn_b = "USB-B"
            else: conn_b = "USB-B" # Common for instruments

    if conn_a == "Unknown" and conn_b == "Unknown":
        return None

    # 3. Determine Signal Type
    signal_type = "Unbalanced"
    if "balanced" in full_text: 
        signal_type = "Balanced"
    elif "aes/ebu" in full_text or "aes" in full_text: 
        signal_type = "AES/EBU"
    elif "dante" in full_text: 
        signal_type = "Dante"
    elif "midi" in full_text: 
        signal_type = "MIDI"
    else:
        balanced_connectors = ["XLR-Male", "XLR-Female", "TRS-1/4", "DB25", "USB-C", "USB-A", "USB-B"]
        if conn_a in balanced_connectors and conn_b in balanced_connectors:
            signal_type = "Balanced"

    # 4. Length extraction
    length_meters = None
    # "3 m" or "3m"
    length_match = re.search(r'(\d+(?:\.\d+)?)\s*m\b', full_text) 
    if length_match:
        try:
            length_meters = float(length_match.group(1))
        except:
            pass
    
    # "10 ft" -> meters
    if not length_meters:
        ft_match = re.search(r'(\d+(?:\.\d+)?)\s*ft', full_text)
        if ft_match:
            try:
                ft = float(ft_match.group(1))
                length_meters = round(ft * 0.3048, 2)
            except:
                pass
                
    return {
        "type": type_,
        "connector_a": conn_a,
        "connector_b": conn_b,
        "signal_type": signal_type,
        "length_meters": length_meters
    }

def calculate_tier(price, description):
    score = 0
    desc = description.lower() if description else ""
    grade_factors = []
    
    # 1. Technology Scoring
    if "gold" in desc: 
        score += 2
        grade_factors.append("Gold Plated")
    if "oxygen free" in desc or "ofc" in desc: 
        score += 2
        grade_factors.append("Oxygen Free Copper")
    if "balanced" in desc: 
        score += 3
        grade_factors.append("Balanced")
    if "hand-soldered" in desc: 
        score += 2
        grade_factors.append("Hand-soldered")
    if "braided" in desc or "shield" in desc:
        score += 1
        
    # 2. Price Scoring (Dynamic Tiers)
    if price > 100: score += 5
    elif price > 40: score += 3
    
    # 3. Assign Tier
    level = "Entry"
    target_audience = "Student"
    
    if score >= 8: 
        level = "Elite"
        target_audience = "Broadcast"
    elif score >= 4: 
        level = "Pro"
        target_audience = "Studio"
        
    return {
        "level": level,
        "grade_factors": grade_factors,
        "target_audience": target_audience
    }
