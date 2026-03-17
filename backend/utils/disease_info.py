"""
Disease Information Database
============================
Contains detailed information, descriptions, and precautions
for all 7 skin disease classes from the HAM10000 dataset.
"""

# Comprehensive disease information dictionary
DISEASE_INFO = {
    "Actinic Keratoses": {
        "short_code": "akiec",
        "full_name": "Actinic Keratoses and Intraepithelial Carcinoma (Bowen's Disease)",
        "description": (
            "Actinic keratoses are rough, scaly patches on the skin caused by years of "
            "sun exposure. They are considered pre-cancerous and can potentially develop "
            "into squamous cell carcinoma if left untreated. Bowen's disease is a very "
            "early form of skin cancer that appears as a red, scaly patch on the skin."
        ),
        "severity": "Moderate to High",
        "precautions": [
            "Consult a dermatologist immediately for proper diagnosis",
            "Avoid prolonged sun exposure and use SPF 50+ sunscreen",
            "Wear protective clothing and wide-brimmed hats outdoors",
            "Regular skin examinations every 6-12 months",
            "Do not attempt to self-treat or remove lesions",
            "Follow up with biopsy if recommended by your doctor"
        ]
    },
    "Basal Cell Carcinoma": {
        "short_code": "bcc",
        "full_name": "Basal Cell Carcinoma",
        "description": (
            "Basal cell carcinoma (BCC) is the most common form of skin cancer. "
            "It arises from the basal cells in the epidermis. While it rarely spreads "
            "to other parts of the body, it can cause significant local tissue damage "
            "if not treated. It commonly appears as a pearly or waxy bump, or a flat, "
            "flesh-colored or brown scar-like lesion."
        ),
        "severity": "High",
        "precautions": [
            "Seek immediate medical consultation with a dermatologist",
            "Surgical removal may be necessary — discuss options with your doctor",
            "Apply broad-spectrum SPF 50+ sunscreen daily",
            "Avoid tanning beds and direct sunlight during peak hours (10am-4pm)",
            "Perform monthly self-examinations of your skin",
            "Schedule regular follow-up appointments after treatment"
        ]
    },
    "Benign Keratosis": {
        "short_code": "bkl",
        "full_name": "Benign Keratosis (Seborrheic Keratosis, Solar Lentigo, Lichen Planus)",
        "description": (
            "Benign keratoses are non-cancerous skin growths that include seborrheic "
            "keratoses, solar lentigines (age spots), and lichen planus-like keratoses. "
            "They are usually harmless and appear as brown, black, or tan growths on the "
            "skin. They may look concerning but generally do not require treatment."
        ),
        "severity": "Low",
        "precautions": [
            "Generally harmless — no urgent treatment needed",
            "Consult a dermatologist to confirm the diagnosis",
            "Monitor for any changes in size, color, or shape",
            "Do not scratch or irritate the affected area",
            "Use gentle skincare products on affected areas",
            "Removal is optional and usually for cosmetic reasons only"
        ]
    },
    "Dermatofibroma": {
        "short_code": "df",
        "full_name": "Dermatofibroma",
        "description": (
            "Dermatofibroma is a common, benign skin growth that usually appears on "
            "the lower legs. It feels like a hard lump under the skin and may be pink, "
            "brown, or red. These growths are harmless and are often caused by minor "
            "injuries such as insect bites or small puncture wounds."
        ),
        "severity": "Low",
        "precautions": [
            "Usually no treatment is required",
            "Consult a dermatologist if the lesion grows or changes",
            "Avoid picking or scratching at the growth",
            "Surgical removal is an option if it causes discomfort",
            "Monitor for any unusual changes (bleeding, rapid growth)",
            "Use sunscreen to prevent darkening of the area"
        ]
    },
    "Melanoma": {
        "short_code": "mel",
        "full_name": "Melanoma",
        "description": (
            "Melanoma is the most dangerous and aggressive type of skin cancer. "
            "It develops from melanocytes (pigment-producing cells) and can spread "
            "rapidly to other organs if not caught early. Early detection is critical "
            "for successful treatment. Follow the ABCDE rule: Asymmetry, Border "
            "irregularity, Color variation, Diameter >6mm, and Evolving size/shape."
        ),
        "severity": "Critical",
        "precautions": [
            "URGENT: Seek immediate medical attention from a dermatologist or oncologist",
            "Do NOT delay — early detection dramatically improves survival rates",
            "A biopsy will be necessary to confirm diagnosis and determine stage",
            "Avoid sun exposure and use maximum protection (SPF 50+)",
            "Do not attempt to remove or treat the lesion yourself",
            "Follow the ABCDE rule for monitoring other moles",
            "Regular full-body skin examinations are essential",
            "Discuss treatment options with your oncology team immediately"
        ]
    },
    "Melanocytic Nevi": {
        "short_code": "nv",
        "full_name": "Melanocytic Nevi (Moles)",
        "description": (
            "Melanocytic nevi, commonly known as moles, are benign growths of "
            "melanocytes. They can be flat or raised, and range in color from pink "
            "to dark brown. Most people have 10-40 moles. While generally harmless, "
            "some moles can develop into melanoma, so monitoring is important."
        ),
        "severity": "Low",
        "precautions": [
            "Generally harmless — routine monitoring is usually sufficient",
            "Use the ABCDE rule to watch for suspicious changes",
            "Schedule annual skin check-ups with a dermatologist",
            "Protect moles from excessive sun exposure",
            "Consult a doctor if a mole changes in size, shape, or color",
            "Photograph moles periodically to track any changes over time"
        ]
    },
    "Vascular Lesions": {
        "short_code": "vasc",
        "full_name": "Vascular Lesions (Angiomas, Angiokeratomas, Pyogenic Granulomas, Hemorrhage)",
        "description": (
            "Vascular lesions are abnormalities of blood vessels in or under the skin. "
            "They include angiomas (benign blood vessel tumors), angiokeratomas "
            "(small dark spots), pyogenic granulomas (rapidly growing red bumps), "
            "and hemorrhagic conditions. Most are benign but some may require treatment."
        ),
        "severity": "Low to Moderate",
        "precautions": [
            "Consult a dermatologist for proper diagnosis and classification",
            "Avoid trauma to the affected area to prevent bleeding",
            "Do not attempt to remove vascular lesions yourself",
            "Treatment options include laser therapy, cryotherapy, or surgical removal",
            "Monitor for any rapid changes in size or frequent bleeding",
            "Keep the area clean and protected from irritation"
        ]
    }
}


def get_disease_info(disease_name: str) -> dict:
    """
    Get complete information about a skin disease.
    
    Args:
        disease_name: Name of the disease (must match CLASS_NAMES)
    
    Returns:
        Dictionary with disease details, or default info if not found
    """
    return DISEASE_INFO.get(disease_name, {
        "full_name": disease_name,
        "description": "No detailed information available for this condition.",
        "severity": "Unknown",
        "precautions": [
            "Consult a dermatologist for proper diagnosis",
            "Do not self-diagnose or self-treat"
        ]
    })
