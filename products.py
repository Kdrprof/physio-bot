"""
PhysioAssist Product Recommendations
Amazon Affiliate links will be added via profphysio.com pages
Currently: product names only (compliant)
"""

import os

AFFILIATE_ID = os.getenv("AMAZON_AFFILIATE_ID", "profphysio-20")
SITE_URL = "https://profphysio.com"

# ── PRODUCT DATABASE ──────────────────────────────
# Structure: condition_key → list of products
# URL will point to profphysio.com review page (Amazon compliant)
# When profphysio.com pages are ready, set HAS_SITE_PAGES = True

HAS_SITE_PAGES = False  # Set True when profphysio.com pages are ready

PRODUCTS = {
    "cervical": [
        {
            "name_en": "Massage Gun (Theragun Prime)",
            "name_ar": "\u062c\u0647\u0627\u0632 \u0645\u0633\u0627\u062c \u0639\u0636\u0644\u064a (Theragun Prime)",
            "reason_en": "Evidence-based myofascial release for cervical muscle tension. Most clinically recommended percussion device.",
            "reason_ar": "\u062a\u062d\u0631\u064a\u0631 \u0639\u0636\u0644\u064a \u0645\u062f\u0639\u0648\u0645 \u0628\u0627\u0644\u0623\u062f\u0644\u0629 \u0644\u0644\u062a\u0648\u062a\u0631 \u0627\u0644\u0639\u0636\u0644\u064a \u0644\u0644\u0631\u0642\u0628\u0629.",
            "asin": "B09BVBF52N",
            "page_slug": "best-massage-guns-for-neck-pain",
            "price_range": "$199-250",
        },
        {
            "name_en": "Cervical Pillow (Contour Memory Foam)",
            "name_ar": "\u0648\u0633\u0627\u062f\u0629 \u0631\u0642\u0628\u064a\u0629 \u0637\u0628\u064a\u0629",
            "reason_en": "Maintains cervical lordosis during sleep. Reduces morning stiffness significantly per RCT evidence.",
            "reason_ar": "\u062a\u062d\u0627\u0641\u0638 \u0639\u0644\u0649 \u0627\u0646\u062d\u0646\u0627\u0621 \u0627\u0644\u0631\u0642\u0628\u0629 \u0623\u062b\u0646\u0627\u0621 \u0627\u0644\u0646\u0648\u0645.",
            "asin": "B07PVLPDWB",
            "page_slug": "best-cervical-pillows",
            "price_range": "$30-60",
        },
        {
            "name_en": "Portable TENS Unit",
            "name_ar": "\u062c\u0647\u0627\u0632 TENS \u0645\u062d\u0645\u0648\u0644",
            "reason_en": "NICE-recommended for cervicogenic pain. Non-pharmacological pain relief via electrical nerve stimulation.",
            "reason_ar": "\u0645\u0648\u0635\u0649 \u0628\u0647 \u0645\u0646 NICE \u0644\u062a\u062e\u0641\u064a\u0641 \u0622\u0644\u0627\u0645 \u0627\u0644\u0631\u0642\u0628\u0629.",
            "asin": "B01N1CDSPY",
            "page_slug": "best-tens-units-neck-pain",
            "price_range": "$25-50",
        },
    ],
    "lumbar": [
        {
            "name_en": "Massage Gun (RENPHO R3 - Budget)",
            "name_ar": "\u062c\u0647\u0627\u0632 \u0645\u0633\u0627\u062c (RENPHO R3)",
            "reason_en": "Percussion therapy reduces lower back muscle spasm. Budget-friendly with clinical-grade results.",
            "reason_ar": "\u064a\u062e\u0641\u0641 \u062a\u0634\u0646\u062c \u0639\u0636\u0644\u0627\u062a \u0623\u0633\u0641\u0644 \u0627\u0644\u0638\u0647\u0631 \u0628\u0641\u0639\u0627\u0644\u064a\u0629.",
            "asin": "B09B3RXTB4",
            "page_slug": "best-massage-guns-for-back-pain",
            "price_range": "$50-80",
        },
        {
            "name_en": "Lumbar Support Cushion",
            "name_ar": "\u062f\u0639\u0627\u0645\u0629 \u0623\u0633\u0641\u0644 \u0627\u0644\u0638\u0647\u0631",
            "reason_en": "Maintains lumbar lordosis during sitting. Reduces intradiscal pressure by up to 40%.",
            "reason_ar": "\u062a\u0642\u0644\u0644 \u0636\u063a\u0637 \u0627\u0644\u0623\u0642\u0631\u0627\u0635 \u0623\u062b\u0646\u0627\u0621 \u0627\u0644\u062c\u0644\u0648\u0633.",
            "asin": "B07DRFZ9ZW",
            "page_slug": "best-lumbar-support-cushions",
            "price_range": "$25-45",
        },
        {
            "name_en": "TENS Unit for Back Pain",
            "name_ar": "\u062c\u0647\u0627\u0632 TENS \u0644\u0622\u0644\u0627\u0645 \u0627\u0644\u0638\u0647\u0631",
            "reason_en": "NICE 2021 recommends TENS as first-line non-pharmacological treatment for chronic LBP.",
            "reason_ar": "\u0645\u0648\u0635\u0649 \u0628\u0647 \u0628\u062f\u0631\u062c\u0629 \u0623\u0648\u0644\u0649 \u0644\u0622\u0644\u0627\u0645 \u0627\u0644\u0638\u0647\u0631 \u0627\u0644\u0645\u0632\u0645\u0646\u0629.",
            "asin": "B01N1CDSPY",
            "page_slug": "best-tens-units-back-pain",
            "price_range": "$25-50",
        },
        {
            "name_en": "Heating Pad (Large)",
            "name_ar": "\u0648\u0633\u0627\u062f\u0629 \u062a\u062f\u0641\u0626\u0629 \u0643\u0628\u064a\u0631\u0629",
            "reason_en": "Moist heat before exercises reduces muscle stiffness. Cochrane evidence for LBP.",
            "reason_ar": "\u0627\u0644\u062d\u0631\u0627\u0631\u0629 \u0642\u0628\u0644 \u0627\u0644\u062a\u0645\u0627\u0631\u064a\u0646 \u062a\u0642\u0644\u0644 \u0627\u0644\u062a\u064a\u0628\u0633.",
            "asin": "B00IYMBV6K",
            "page_slug": "best-heating-pads-back-pain",
            "price_range": "$25-40",
        },
    ],
    "shoulder": [
        {
            "name_en": "Massage Gun (Theragun Prime)",
            "name_ar": "\u062c\u0647\u0627\u0632 \u0645\u0633\u0627\u062c (Theragun Prime)",
            "reason_en": "Percussion therapy for rotator cuff and deltoid tension. Use before stretching exercises.",
            "reason_ar": "\u0645\u0641\u064a\u062f \u0644\u0644\u0643\u0641\u0629 \u0627\u0644\u0645\u062f\u0648\u0631\u0629 \u0648\u062a\u0634\u0646\u062c \u0627\u0644\u0643\u062a\u0641.",
            "asin": "B09BVBF52N",
            "page_slug": "best-massage-guns-shoulder-pain",
            "price_range": "$199-250",
        },
        {
            "name_en": "Resistance Bands Set",
            "name_ar": "\u0623\u0634\u0631\u0637\u0629 \u0645\u0637\u0627\u0637\u064a\u0629 \u0645\u0642\u0627\u0648\u0645\u0629",
            "reason_en": "Essential for rotator cuff strengthening. APTA-recommended for subacromial impingement.",
            "reason_ar": "\u0636\u0631\u0648\u0631\u064a\u0629 \u0644\u062a\u0642\u0648\u064a\u0629 \u0639\u0636\u0644\u0627\u062a \u0627\u0644\u0643\u0641\u0629 \u0627\u0644\u0645\u062f\u0648\u0631\u0629.",
            "asin": "B01AVDVHTI",
            "page_slug": "best-resistance-bands-shoulder",
            "price_range": "$15-30",
        },
        {
            "name_en": "Heating Pad",
            "name_ar": "\u0648\u0633\u0627\u062f\u0629 \u062a\u062f\u0641\u0626\u0629",
            "reason_en": "Pre-exercise heat for frozen shoulder increases capsule extensibility.",
            "reason_ar": "\u0627\u0644\u062d\u0631\u0627\u0631\u0629 \u0642\u0628\u0644 \u062a\u0645\u0627\u0631\u064a\u0646 \u0627\u0644\u0643\u062a\u0641 \u0627\u0644\u0645\u062a\u062c\u0645\u062f.",
            "asin": "B00IYMBV6K",
            "page_slug": "best-heating-pads-shoulder",
            "price_range": "$25-40",
        },
    ],
    "knee": [
        {
            "name_en": "Massage Gun (RENPHO R3)",
            "name_ar": "\u062c\u0647\u0627\u0632 \u0645\u0633\u0627\u062c (RENPHO R3)",
            "reason_en": "Quad and hamstring release before knee exercises reduces pain during rehabilitation.",
            "reason_ar": "\u062a\u062d\u0631\u064a\u0631 \u0639\u0636\u0644\u0627\u062a \u0627\u0644\u0641\u062e\u0630 \u064a\u062e\u0641\u0641 \u0622\u0644\u0627\u0645 \u0627\u0644\u0631\u0643\u0628\u0629.",
            "asin": "B09B3RXTB4",
            "page_slug": "best-massage-guns-knee-pain",
            "price_range": "$50-80",
        },
        {
            "name_en": "Knee Compression Sleeve",
            "name_ar": "\u0643\u0645\u0627\u0645\u0629 \u0636\u063a\u0637 \u0644\u0644\u0631\u0643\u0628\u0629",
            "reason_en": "Improves proprioception and reduces swelling. Evidence-based for OA and PFPS.",
            "reason_ar": "\u062a\u062d\u0633\u0646 \u062d\u0633 \u0627\u0644\u062a\u0648\u0627\u0632\u0646 \u0648\u062a\u0642\u0644\u0644 \u0627\u0644\u062a\u0648\u0631\u0645.",
            "asin": "B00J1EVNIG",
            "page_slug": "best-knee-sleeves",
            "price_range": "$15-30",
        },
        {
            "name_en": "Foam Roller",
            "name_ar": "\u0623\u0633\u0637\u0648\u0627\u0646\u0629 \u0631\u063a\u0648\u064a\u0629 (Foam Roller)",
            "reason_en": "IT Band and quad myofascial release. NSCA-recommended for knee pain management.",
            "reason_ar": "\u062a\u062d\u0631\u064a\u0631 \u0631\u0628\u0627\u0637 IT Band \u0648\u0639\u0636\u0644\u0627\u062a \u0627\u0644\u0641\u062e\u0630.",
            "asin": "B00BHKYP82",
            "page_slug": "best-foam-rollers",
            "price_range": "$20-35",
        },
    ],
    "ankle_foot": [
        {
            "name_en": "Ankle Brace (Lace-up)",
            "name_ar": "\u062f\u0639\u0627\u0645\u0629 \u0643\u0627\u062d\u0644",
            "reason_en": "Proprioceptive support post-sprain. Reduces re-injury risk by 56% per systematic review.",
            "reason_ar": "\u062a\u0642\u0644\u0644 \u062e\u0637\u0631 \u0625\u0639\u0627\u062f\u0629 \u0627\u0644\u0625\u0635\u0627\u0628\u0629 \u0628\u0639\u062f \u0627\u0644\u0648\u062b\u064a.",
            "asin": "B000G35QRO",
            "page_slug": "best-ankle-braces",
            "price_range": "$20-35",
        },
        {
            "name_en": "Plantar Fasciitis Socks (Night Splint)",
            "name_ar": "\u062c\u0648\u0627\u0631\u0628 \u0637\u0628\u064a\u0629 \u0644\u0627\u0644\u062a\u0647\u0627\u0628 \u0627\u0644\u0644\u0641\u0627\u0641\u0629",
            "reason_en": "Night splint effect maintains dorsiflexion. Reduces morning heel pain significantly.",
            "reason_ar": "\u062a\u062d\u0627\u0641\u0638 \u0639\u0644\u0649 \u062a\u0645\u062f\u062f \u0648\u062a\u0631 \u0623\u0643\u064a\u0644\u064a\u0633 \u0623\u062b\u0646\u0627\u0621 \u0627\u0644\u0646\u0648\u0645.",
            "asin": "B00BWDANCU",
            "page_slug": "best-plantar-fasciitis-socks",
            "price_range": "$15-25",
        },
    ],
    "elbow": [
        {
            "name_en": "Tennis Elbow Brace",
            "name_ar": "\u062d\u0632\u0627\u0645 \u0643\u0648\u0639 \u0627\u0644\u062a\u0646\u0633",
            "reason_en": "Counter-force brace reduces tendon load by 30%. First-line recommendation for lateral epicondylalgia.",
            "reason_ar": "\u064a\u0642\u0644\u0644 \u0627\u0644\u062d\u0645\u0644 \u0639\u0644\u0649 \u0648\u062a\u0631 \u0643\u0648\u0639 \u0627\u0644\u062a\u0646\u0633.",
            "asin": "B00Q9EB7UQ",
            "page_slug": "best-tennis-elbow-braces",
            "price_range": "$15-25",
        },
        {
            "name_en": "Massage Gun (RENPHO R3)",
            "name_ar": "\u062c\u0647\u0627\u0632 \u0645\u0633\u0627\u062c",
            "reason_en": "Forearm extensor percussion reduces tendinopathy pain before eccentric exercises.",
            "reason_ar": "\u064a\u062e\u0641\u0641 \u0622\u0644\u0627\u0645 \u0648\u062a\u0631 \u0627\u0644\u0633\u0627\u0639\u062f \u0642\u0628\u0644 \u0627\u0644\u062a\u0645\u0627\u0631\u064a\u0646.",
            "asin": "B09B3RXTB4",
            "page_slug": "best-massage-guns-elbow-pain",
            "price_range": "$50-80",
        },
    ],
    "hip": [
        {
            "name_en": "Massage Gun (Theragun Prime)",
            "name_ar": "\u062c\u0647\u0627\u0632 \u0645\u0633\u0627\u062c",
            "reason_en": "Gluteal and piriformis percussion reduces hip pain and improves range of motion.",
            "reason_ar": "\u062a\u062d\u0631\u064a\u0631 \u0639\u0636\u0644\u0627\u062a \u0627\u0644\u0648\u0631\u0643 \u0648\u062a\u062d\u0633\u064a\u0646 \u0645\u062f\u0649 \u0627\u0644\u062d\u0631\u0643\u0629.",
            "asin": "B09BVBF52N",
            "page_slug": "best-massage-guns-hip-pain",
            "price_range": "$199-250",
        },
        {
            "name_en": "Resistance Bands Set",
            "name_ar": "\u0623\u0634\u0631\u0637\u0629 \u0645\u0642\u0627\u0648\u0645\u0629",
            "reason_en": "Hip abductor strengthening - essential for hip OA and trochanteric bursitis.",
            "reason_ar": "\u062a\u0642\u0648\u064a\u0629 \u0639\u0636\u0644\u0627\u062a \u0645\u0628\u0639\u062f\u0627\u062a \u0627\u0644\u0648\u0631\u0643.",
            "asin": "B01AVDVHTI",
            "page_slug": "best-resistance-bands-hip",
            "price_range": "$15-30",
        },
    ],
    "general": [
        {
            "name_en": "Massage Gun (Theragun Prime) - Top Recommended",
            "name_ar": "\u062c\u0647\u0627\u0632 \u0645\u0633\u0627\u062c (Theragun Prime) - \u0627\u0644\u0623\u0643\u062b\u0631 \u062a\u0648\u0635\u064a\u0629",
            "reason_en": "Used by physiotherapists worldwide. Clinically proven for myofascial pain, muscle tension, and recovery.",
            "reason_ar": "\u0645\u0633\u062a\u062e\u062f\u0645 \u0645\u0646 \u0623\u062e\u0635\u0627\u0626\u064a\u064a \u0627\u0644\u0639\u0644\u0627\u062c \u0627\u0644\u0637\u0628\u064a\u0639\u064a \u062d\u0648\u0644 \u0627\u0644\u0639\u0627\u0644\u0645.",
            "asin": "B09BVBF52N",
            "page_slug": "best-massage-guns-physical-therapy",
            "price_range": "$199-250",
        },
    ],
}


def get_products(body_region: str, lang: str = "en") -> list:
    """Get product recommendations for a body region."""
    region_map = {
        "neck / head": "cervical", "Neck / Head": "cervical",
        "\u0627\u0644\u0631\u0642\u0628\u0629 \u0648\u0627\u0644\u0631\u0623\u0633": "cervical",
        "shoulder": "shoulder", "Shoulder": "shoulder",
        "\u0627\u0644\u0643\u062a\u0641": "shoulder",
        "lower back / pelvis": "lumbar", "Lower Back / Pelvis": "lumbar",
        "\u0623\u0633\u0641\u0644 \u0627\u0644\u0638\u0647\u0631": "lumbar",
        "knee": "knee", "Knee": "knee",
        "\u0627\u0644\u0631\u0643\u0628\u0629": "knee",
        "ankle / foot": "ankle_foot", "Ankle / Foot": "ankle_foot",
        "\u0627\u0644\u0643\u0627\u062d\u0644 \u0648\u0627\u0644\u0642\u062f\u0645": "ankle_foot",
        "elbow / forearm": "elbow", "Elbow / Forearm": "elbow",
        "\u0627\u0644\u0643\u0648\u0639 \u0648\u0627\u0644\u0633\u0627\u0639\u062f": "elbow",
        "hip / thigh": "hip", "Hip / Thigh": "hip",
        "\u0627\u0644\u0648\u0631\u0643 \u0648\u0627\u0644\u0641\u062e\u0630": "hip",
    }

    key = region_map.get(body_region, "general")
    products = PRODUCTS.get(key, PRODUCTS["general"])

    result = []
    for p in products[:3]:  # Max 3 products per report
        name  = p["name_ar"]  if lang == "ar" else p["name_en"]
        reason = p["reason_ar"] if lang == "ar" else p["reason_en"]

        if HAS_SITE_PAGES:
            link = f"{SITE_URL}/{p['page_slug']}/?tag={AFFILIATE_ID}"
            link_text = f"[{name}]({link})"
        else:
            # No link yet — just the name
            link_text = name

        result.append({
            "name": name,
            "reason": reason,
            "link_text": link_text,
            "price_range": p["price_range"],
            "has_link": HAS_SITE_PAGES,
        })
    return result


def format_products_for_report(body_region: str, lang: str) -> str:
    """Format product recommendations as text for AI prompt."""
    products = get_products(body_region, lang)
    if not products:
        return ""

    lines = []
    for p in products:
        if lang == "ar":
            lines.append(
                f"- {p['name']} ({p['price_range']}): {p['reason']}"
            )
        else:
            lines.append(
                f"- {p['name']} ({p['price_range']}): {p['reason']}"
            )
    return "\n".join(lines)
