import os
import json
from pathlib import Path

# Paths
REFINERY_DATA = Path(__file__).resolve().parent.parent / "data" / "refinery"
OFFICIAL = REFINERY_DATA / "1_official_ingest"
COMMERCIAL = REFINERY_DATA / "2_commercial_enrich"
CONTEXT = REFINERY_DATA / "3_context_validator"

# The "Diamond" Standard Data for 6 Brands
DATABASE = {
    "adam-audio": {
        "id": "a7v",
        "official": {
            "manufacturer_sku": "ADAM-A7V",
            "official_name": "Adam Audio A7V Active 2-Way Monitor",
            "official_page": "https://adam-audio.com/a7v",
            "specs": {
                "woofer_size_inch": 7.0,
                "tweeter_type": "X-ART Ribbon",
                "frequency_response_low_hz": 41,
                "frequency_response_high_hz": 42000,
                "power_total_watts": 130,
                "dimensions": "200 x 290 x 245 mm",
                "weight_kg": 11.5
            },
            "media_assets": {
                "manual": "https://adam-audio.com/manuals/a7v.pdf",
                "image_front": "https://adam-audio.com/images/a7v-front.jpg",
                "image_detail": "https://adam-audio.com/images/a7v-back.jpg"
            }
        },
        "commercial": {
            "price": 3100,
            "stock_status": "IN_STOCK",
            "delivery_time": "Immediate"
        },
        "context": {
            "verified_sources": [
                {"source": "Sound On Sound",
                    "url": "https://sos.com/reviews/adam-a7v", "date": "2024-06"},
                {"source": "Mix Magazine",
                    "url": "https://mix.com/reviews/adam-a7v", "date": "2024-03"}
            ],
            "pros": [
                "Excellent stereo imaging with wide sweet spot",
                "Transparent mid-range perfect for mixing",
                "Rotatable waveguide for room adaptation",
                "Class-leading transient response"
            ],
            "cons": [
                "Rear port requires careful placement away from walls",
                "Higher price point for the class"
            ],
            "recurring_issues": [],
            "expert_tips": [
                "Pair with quality bass management for optimal translation",
                "Use Sonarworks integration for flat response in untreated rooms"
            ]
        }
    },
    "amphion": {
        "id": "one18",
        "official": {
            "manufacturer_sku": "AMPH-ONE18",
            "official_name": "Amphion One18 Passive 3-Way Monitor",
            "official_page": "https://amphion.fi/one18",
            "specs": {
                "woofer_size_inch": 8.0,
                "midrange_type": "Custom cone driver",
                "tweeter_type": "25mm silk dome",
                "frequency_response_low_hz": 35,
                "frequency_response_high_hz": 22000,
                "impedance_ohms": 4,
                "sensitivity_db": 89,
                "dimensions": "240 x 430 x 280 mm",
                "weight_kg": 24
            },
            "media_assets": {
                "manual": "https://amphion.fi/docs/one18-manual.pdf",
                "image_front": "https://amphion.fi/images/one18.jpg"
            }
        },
        "commercial": {
            "price": 12500,
            "stock_status": "IN_STOCK",
            "delivery_time": "Special Order (4-6 weeks)"
        },
        "context": {
            "verified_sources": [
                {"source": "Gearspace Forum",
                    "url": "https://gearspace.com/amphion", "date": "2024-01"},
                {"source": "TapeOp Magazine",
                    "url": "https://tapeop.com/reviews/amphion", "date": "2023-11"}
            ],
            "pros": [
                "Incredible translation across playback systems",
                "Natural phase coherence in the midrange",
                "Professional-grade build quality",
                "Exceptional reliability in commercial studios"
            ],
            "cons": [
                "Requires external amplification (passive design)",
                "Very expensive investment"
            ],
            "recurring_issues": [],
            "expert_tips": [
                "Match with high-quality 50W+ amplifier for best results",
                "Place on dedicated monitor stands for optimal isolation"
            ]
        }
    },
    "warm-audio": {
        "id": "wa-87",
        "official": {
            "manufacturer_sku": "WA-87r2",
            "official_name": "Warm Audio WA-87 R2 Condenser Microphone",
            "official_page": "https://warmaudio.com/wa-87",
            "specs": {
                "type": "Large-diaphragm Condenser",
                "diaphragm_size_mm": 32,
                "polar_pattern": "Cardioid / Omnidirectional / Figure-8 (switchable)",
                "frequency_response_low_hz": 20,
                "frequency_response_high_hz": 20000,
                "sensitivity_db": 28,
                "max_spl_db": 140,
                "impedance_ohms": 200,
                "weight_g": 435
            },
            "media_assets": {
                "manual": "https://warmaudio.com/docs/wa-87-manual.pdf",
                "image_front": "https://warmaudio.com/images/wa-87-front.jpg",
                "polar_patterns": "https://warmaudio.com/images/wa-87-polar.pdf"
            }
        },
        "commercial": {
            "price": 2400,
            "stock_status": "IN_STOCK",
            "delivery_time": "Next Day"
        },
        "context": {
            "verified_sources": [
                {"source": "Sound On Sound",
                    "url": "https://sos.com/warm-audio-wa87", "date": "2024-05"},
                {"source": "RecordingHacks",
                    "url": "https://recordinghacks.com/wa87-review", "date": "2024-02"}
            ],
            "pros": [
                "Warm vintage tone perfect for vocals",
                "Excellent high SPL handling for loud sources",
                "Multi-pattern design adds versatility",
                "Outstanding value for price"
            ],
            "cons": [
                "Requires phantom power supply",
                "Build quality not at vintage tube mic level"
            ],
            "recurring_issues": [],
            "expert_tips": [
                "Pair with quality preamp to get the best from the circuitry",
                "Use shock mount to minimize vibration transfer"
            ]
        }
    },
    "bespeco": {
        "id": "ms11",
        "official": {
            "manufacturer_sku": "MS11",
            "official_name": "Bespeco MS11 Professional Boom Stand",
            "official_page": "https://bespeco.it/ms11",
            "specs": {
                "material": "Heavy-duty steel tubing",
                "height_min_cm": 65,
                "height_max_cm": 200,
                "weight_kg": 2.8,
                "base_diameter_cm": 58,
                "boom_reach_cm": 90,
                "load_capacity_kg": 5,
                "finish": "Black powder-coated"
            },
            "media_assets": {
                "manual": "https://bespeco.it/docs/ms11-manual.pdf",
                "image_front": "https://bespeco.it/images/ms11.jpg"
            }
        },
        "commercial": {
            "price": 150,
            "stock_status": "IN_STOCK",
            "delivery_time": "Immediate"
        },
        "context": {
            "verified_sources": [
                {"source": "Sweetwater Reviews",
                    "url": "https://sweetwater.com/bespeco-ms11", "date": "2024-04"},
                {"source": "Thomann Community",
                    "url": "https://thomann.de/bespeco-ms11", "date": "2024-03"}
            ],
            "pros": [
                "Extremely sturdy construction",
                "Smooth boom arm movement",
                "Good height range for all applications",
                "Excellent value for money"
            ],
            "cons": [
                "Heavy to transport",
                "Takes up floor space"
            ],
            "recurring_issues": [],
            "expert_tips": [
                "Add counterweight for maximum stability with large condensers",
                "Use with boom arm adapter for best ergonomics"
            ]
        }
    },
    "drumdots": {
        "id": "original-dots",
        "official": {
            "manufacturer_sku": "DD-ORG",
            "official_name": "Drumdots Original Dampening Pads",
            "official_page": "https://drumdot.com",
            "specs": {
                "material": "V-Tem silicone blend",
                "diameter_inches": 2.4,
                "thickness_mm": 3,
                "quantity_per_pack": 4,
                "color": "Black",
                "reusable": True,
                "residue_free": True
            },
            "media_assets": {
                "manual": "https://drumdot.com/docs/guide.pdf",
                "image_front": "https://drumdot.com/images/drumdots.jpg"
            }
        },
        "commercial": {
            "price": 60,
            "stock_status": "IN_STOCK",
            "delivery_time": "Immediate"
        },
        "context": {
            "verified_sources": [
                {"source": "Drum Magazine",
                    "url": "https://drummagazine.com/drumdots", "date": "2024-02"},
                {"source": "Modern Drummer",
                    "url": "https://moderndummer.com/drumdots-review", "date": "2023-12"}
            ],
            "pros": [
                "Does not leave residue or damage drum heads",
                "Fully reusable - lasts for years",
                "Precise tone control",
                "Fits any drum size"
            ],
            "cons": [
                "Need to experiment for perfect tone",
                "Small pads require careful placement"
            ],
            "recurring_issues": [],
            "expert_tips": [
                "Start with one dot per drum side for subtle effect",
                "Experiment with placement distance from edge"
            ]
        }
    },
    "fzone": {
        "id": "ft-15",
        "official": {
            "manufacturer_sku": "FT-15",
            "official_name": "Fzone FT-15 Clip Tuner",
            "official_page": "https://fzone.cn",
            "specs": {
                "type": "Chromatic clip tuner",
                "frequency_range_hz": "30-4000",
                "calibration_range_hz": "410-480",
                "battery_type": "CR2032",
                "battery_life_hours": 100,
                "accuracy_cents": 1,
                "display": "LED",
                "weight_g": 30,
                "rotation": "360 degree swivel"
            },
            "media_assets": {
                "manual": "https://fzone.cn/docs/ft15-manual.pdf",
                "image_front": "https://fzone.cn/images/ft-15.jpg"
            }
        },
        "commercial": {
            "price": 45,
            "stock_status": "IN_STOCK",
            "delivery_time": "Immediate"
        },
        "context": {
            "verified_sources": [
                {"source": "Amazon Verified",
                    "url": "https://amazon.com/fzone-ft15", "date": "2024-01"},
                {"source": "Audio Community Forum",
                    "url": "https://audioforums.com/fzone-ft15", "date": "2023-10"}
            ],
            "pros": [
                "Bright LED display visible in all conditions",
                "Fast and accurate tracking",
                "Durable construction",
                "Battery lasts over 100 hours"
            ],
            "cons": [
                "Accuracy limited to 1 cent",
                "Not ideal for very low frequencies"
            ],
            "recurring_issues": [],
            "expert_tips": [
                "Position tuner for clear LED visibility",
                "Use gentle clip pressure to avoid damaging headstocks"
            ]
        }
    }
}


def seed():
    print("🌱 Seeding Diamond Data for 6 Brands...")

    for brand, data in DATABASE.items():
        base_1 = OFFICIAL / brand
        base_2 = COMMERCIAL / brand
        base_3 = CONTEXT / brand

        for p in [base_1, base_2, base_3]:
            p.mkdir(parents=True, exist_ok=True)

        pid = data["id"]

        # Write Official
        with open(base_1 / f"{pid}.json", "w") as f:
            json.dump(data["official"], f, indent=2)

        # Write Commercial
        with open(base_2 / f"{pid}.json", "w") as f:
            json.dump(data["commercial"], f, indent=2)

        # Write Context
        with open(base_3 / f"{pid}.json", "w") as f:
            json.dump(data["context"], f, indent=2)

        print(f"   ✅ {brand} -> {pid} planted.")


if __name__ == "__main__":
    seed()
