# extract_fertilizer_sections.py

import fitz  # PyMuPDF
import re
import json

# Définir les sections pertinentes selon ton projet
RELEVANT_SECTIONS = [
    "Climate and agro-ecological zones",
    "Crop production",
    "Plant nutrient supply",
    "Fertilizer use by crop",
    "Fertilizer recommendations",
    "Price trends",
    "Annex",  # Pour recommandations spécifiques (ex : canne à sucre)
]

def clean_text(text):
    return re.sub(r"\s+", " ", text.strip())

def extract_key_sections(pdf_path: str, output_path="fertilizer_sections.json"):
    doc = fitz.open(pdf_path)
    extracted = {}

    current_section = None
    for page in doc:
        text = page.get_text()
        for section in RELEVANT_SECTIONS:
            if section.lower() in text.lower():
                current_section = section
                if section not in extracted:
                    extracted[section] = ""

        if current_section:
            extracted[current_section] += "\n" + text

    # Nettoyage & export
    extracted_clean = {
        section: clean_text(content)
        for section, content in extracted.items()
    }

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(extracted_clean, f, indent=2, ensure_ascii=False)

    print(f"✅ Fichier exporté : {output_path}")

# Utilisation
if __name__ == "__main__":
    extract_key_sections("fertilizer_use_south_africa.pdf")
