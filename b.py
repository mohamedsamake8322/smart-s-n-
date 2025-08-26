import os
import faiss
import pickle
from PyPDF2 import PdfReader
from sentence_transformers import SentenceTransformer
import numpy as np

# -----------------------
# CONFIGURATION
# -----------------------
PDF_FOLDER = r"C:\Downloads\Agronomie"
OUTPUT_DIR = "vector_store"
CHUNK_SIZE = 500  # ~500 tokens approximatif (environ 400-500 mots)
EMBEDDING_MODEL = "all-MiniLM-L6-v2"  # Modèle rapide et efficace

# -----------------------
# 1. EXTRACTION DU TEXTE DES PDF
# -----------------------
def extract_text_from_pdfs(pdf_folder):
    documents = []
    pdf_files = [f for f in os.listdir(pdf_folder) if f.endswith(".pdf")]
    print(f"[INFO] {len(pdf_files)} PDF trouvés dans {pdf_folder}")

    for file_name in pdf_files:
        pdf_path = os.path.join(pdf_folder, file_name)
        print(f"[INFO] Lecture du PDF : {file_name}")
        reader = PdfReader(pdf_path)
        text = ""
        for page_num, page in enumerate(reader.pages):
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
            print(f"   - Page {page_num+1}/{len(reader.pages)} extraite")
        documents.append((file_name, text))
        print(f"[INFO] PDF {file_name} : {len(text.split())} mots extraits")

    print(f"[INFO] Extraction terminée : {len(documents)} documents chargés.\n")
    return documents

# -----------------------
# 2. SEGMENTATION EN CHUNKS (~500 tokens)
# -----------------------
def chunk_text(text, chunk_size=CHUNK_SIZE):
    words = text.split()
    return [" ".join(words[i:i+chunk_size]) for i in range(0, len(words), chunk_size)]

# -----------------------
# 3. CRÉATION DE LA BASE VECTORIELLE (FAISS)
# -----------------------
def create_vector_store(documents, model_name=EMBEDDING_MODEL):
    print(f"[INFO] Chargement du modèle d'embedding : {model_name}")
    model = SentenceTransformer(model_name)

    texts = []
    metadata = []

    for doc_name, doc_text in documents:
        chunks = chunk_text(doc_text)
        print(f"[INFO] {doc_name} découpé en {len(chunks)} chunks")
        for i, chunk in enumerate(chunks):
            texts.append(chunk)
            metadata.append({"source": doc_name, "chunk_id": i})

    print(f"[INFO] Total de {len(texts)} chunks à encoder.")

    embeddings = model.encode(texts, show_progress_bar=True, convert_to_numpy=True)
    dim = embeddings.shape[1]
    print(f"[INFO] Embeddings générés. Dimension : {dim}")

    index = faiss.IndexFlatL2(dim)
    index.add(embeddings)
    print(f"[INFO] Index FAISS créé avec {index.ntotal} vecteurs.\n")

    return index, texts, metadata

# -----------------------
# 4. SAUVEGARDE DE LA BASE
# -----------------------
def save_vector_store(index, texts, metadata, output_dir=OUTPUT_DIR):
    os.makedirs(output_dir, exist_ok=True)
    faiss.write_index(index, os.path.join(output_dir, "faiss_index.bin"))
    with open(os.path.join(output_dir, "texts.pkl"), "wb") as f:
        pickle.dump(texts, f)
    with open(os.path.join(output_dir, "metadata.pkl"), "wb") as f:
        pickle.dump(metadata, f)
    print(f"[INFO] Base vectorielle sauvegardée dans : {output_dir}\n")

# -----------------------
# 5. MAIN
# -----------------------
if __name__ == "__main__":
    print("[START] Début du traitement des PDF...\n")
    docs = extract_text_from_pdfs(PDF_FOLDER)
    index, texts, metadata = create_vector_store(docs)
    save_vector_store(index, texts, metadata)
    print("[SUCCESS] Index vectoriel créé et sauvegardé avec succès.")
