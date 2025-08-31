import os
import re
import logging
from PyPDF2 import PdfReader
from vector_store import VectorStore

logging.basicConfig(level=logging.INFO)
store = VectorStore()

# 🔍 Détection automatique des métadonnées enrichies
def auto_tag_chunk(chunk: str) -> dict:
    tags = {}

    # Cultures
    crops = ["maïs", "sorgho", "riz", "arachide", "mil", "fonio", "niébé", "manioc"]
    for crop in crops:
        if re.search(rf"\b{crop}\b", chunk.lower()):
            tags["crop"] = crop
            break

    # Stades
    stages = {
        "végétatif": ["croissance végétative", "développement foliaire", "phase végétative"],
        "floraison": ["floraison", "apparition des fleurs", "début floraison"],
        "maturation": ["maturation", "remplissage des grains", "phase finale", "maturité"]
    }
    for stage, keywords in stages.items():
        if any(k in chunk.lower() for k in keywords):
            tags["stage"] = stage
            break

    # Régions
    regions = ["Mali", "Burkina Faso", "zone sahélienne", "Afrique de l’Ouest", "Niger", "Sénégal"]
    for region in regions:
        if region.lower() in chunk.lower():
            tags["region"] = region
            break

    # Thèmes
    themes = {
        "fertilisation": ["engrais", "fertilisation", "apport nutritif"],
        "irrigation": ["irrigation", "eau", "arrosage"],
        "protection phytosanitaire": ["maladie", "ravageur", "traitement", "fongicide", "insecticide"],
        "semis": ["semis", "plantation", "mise en terre"],
        "récolte": ["récolte", "moisson", "cueillette"]
    }
    for theme, keywords in themes.items():
        if any(k in chunk.lower() for k in keywords):
            tags["theme"] = theme
            break

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
                logging.warning(f"⚠️ Aucun contenu extrait de {filename}")
                continue

            # Nettoyage basique
            content = re.sub(r'\s+', ' ', content)

            # Chunking par phrases (via VectorStore)
            chunks = store._chunk_by_sentences(content)

            for i, chunk in enumerate(chunks):
                if len(chunk.split()) < 30:
                    logging.debug(f"⏭️ Chunk trop court ignoré ({len(chunk.split())} mots)")
                    continue

                metadata = auto_tag_chunk(chunk)
                store.add_document(filename=filename, content=chunk, metadata=metadata)

            logging.info(f"✅ {len(chunks)} chunks traités pour {filename}")

# 📂 Dossier contenant les PDF agronomiques
pdf_folder = "C:\\Downloads\\Agriculture"
process_pdf_folder(pdf_folder)
