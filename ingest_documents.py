import os
from PyPDF2 import PdfReader
from vector_store import VectorStore
import logging

logging.basicConfig(level=logging.INFO)
store = VectorStore()

# 🔍 Détection automatique des métadonnées
def auto_tag_chunk(chunk: str) -> dict:
    tags = {}

    # Cultures
    crops = ["maïs", "sorgho", "riz", "arachide", "mil", "fonio"]
    for crop in crops:
        if crop in chunk.lower():
            tags["crop"] = crop
            break

    # Stades
    stages = {
        "végétatif": ["croissance végétative", "développement foliaire"],
        "floraison": ["floraison", "apparition des fleurs"],
        "maturation": ["maturation", "remplissage des grains", "phase finale"]
    }
    for stage, keywords in stages.items():
        if any(k in chunk.lower() for k in keywords):
            tags["stage"] = stage
            break

    # Régions
    regions = ["Mali", "Burkina Faso", "zone sahélienne", "Afrique de l’Ouest"]
    for region in regions:
        if region.lower() in chunk.lower():
            tags["region"] = region
            break

    # Thèmes
    if "engrais" in chunk.lower() or "fertilisation" in chunk.lower():
        tags["theme"] = "fertilisation"
    elif "irrigation" in chunk.lower():
        tags["theme"] = "irrigation"
    elif "maladie" in chunk.lower() or "ravageur" in chunk.lower():
        tags["theme"] = "protection phytosanitaire"
    elif "semis" in chunk.lower():
        tags["theme"] = "semis"
    elif "récolte" in chunk.lower():
        tags["theme"] = "récolte"

    return tags

# 📚 Extraction du texte depuis un PDF
def extract_text_from_pdf(pdf_path: str) -> str:
    try:
        reader = PdfReader(pdf_path)
        text = ""
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
        return text.strip()
    except Exception as e:
        logging.error(f"Erreur lecture PDF {pdf_path}: {e}")
        return ""

# 🚀 Traitement de tous les PDF du dossier
def process_pdf_folder(folder_path: str):
    for filename in os.listdir(folder_path):
        if filename.lower().endswith(".pdf"):
            full_path = os.path.join(folder_path, filename)
            logging.info(f"📄 Traitement du fichier : {filename}")
            content = extract_text_from_pdf(full_path)

            if not content:
                continue

            # Chunking par phrases (via VectorStore)
            chunks = store._chunk_by_sentences(content)

            for chunk in chunks:
                metadata = auto_tag_chunk(chunk)
                store.add_document(filename=filename, content=chunk, metadata=metadata)

# 📂 Dossier contenant les PDF agronomiques
pdf_folder = "C:\\Downloads\\Agriculture"
process_pdf_folder(pdf_folder)
