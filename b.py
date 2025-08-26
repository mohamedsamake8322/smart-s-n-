import os
import json
import pickle

# -----------------------
# CONFIGURATION
# -----------------------
JSON_FOLDER = r"C:\Downloads\Agronomie"
OUTPUT_DIR = "prepared_chunks_json"
MIN_WORDS = 50

# -----------------------
# FORMATAGE DU TEXTE
# -----------------------
def format_product(name, data):
    lines = [f"Produit : {name}"]
    lines.append(f"Type : {data.get('type', 'N/A')}")
    lines.append(f"Formulation : {data.get('formulation', 'N/A')}")

    compo = data.get("composition_g_per_l", {})
    if compo:
        compo_str = ", ".join([f"{k}: {v} g/L" for k, v in compo.items()])
        lines.append(f"Composition : {compo_str}")

    tech = data.get("technologie")
    if tech:
        lines.append(f"Technologie : {tech}")

    avantages = data.get("avantages", [])
    if avantages:
        lines.append("Avantages : " + "; ".join(avantages))

    return "\n".join(lines)

def is_chunk_useful(text):
    return len(text.split()) >= MIN_WORDS

# -----------------------
# EXTRACTION
# -----------------------
def extract_chunks_from_json(json_folder):
    json_files = [f for f in os.listdir(json_folder) if f.endswith(".json")]
    print(f"[INFO] {len(json_files)} fichiers JSON trouvés dans {json_folder}")

    all_chunks = []
    all_metadata = []

    for file_name in json_files:
        file_path = os.path.join(json_folder, file_name)
        with open(file_path, "r", encoding="utf-8") as f:
            try:
                data = json.load(f)
            except Exception as e:
                print(f"[ERROR] Erreur de lecture {file_name} : {e}")
                continue

        for entry in data:
            for product_name, product_data in entry.items():
                if not isinstance(product_data, dict):
                    print(f"[SKIP] Produit ignoré (non structuré) : {product_name}")
            continue  # Ignore les entrées non structurées

        chunk = format_product(product_name, product_data)
        if is_chunk_useful(chunk):
            all_chunks.append(chunk)
            all_metadata.append({
                "source": file_name,
                "chunk_id": chunk_id,
                "length": len(chunk.split()),
                "preview": chunk[:100] + "...",
                "type": "json"
            })
            chunk_id += 1


        print(f"[INFO] {file_name} : {chunk_id} chunks extraits\n")

    return all_chunks, all_metadata

# -----------------------
# SAUVEGARDE
# -----------------------
def save_chunks(chunks, metadata, output_dir=OUTPUT_DIR):
    os.makedirs(output_dir, exist_ok=True)
    with open(os.path.join(output_dir, "texts_cleaned_json.pkl"), "wb") as f:
        pickle.dump(chunks, f)
    with open(os.path.join(output_dir, "metadata_cleaned_json.pkl"), "wb") as f:
        pickle.dump(metadata, f)
    print(f"[SUCCESS] {len(chunks)} chunks JSON sauvegardés dans {output_dir}")

# -----------------------
# MAIN
# -----------------------
if __name__ == "__main__":
    print("[START] Extraction intelligente des JSON...\n")
    chunks, metadata = extract_chunks_from_json(JSON_FOLDER)
    save_chunks(chunks, metadata)
    print("[DONE] Tous les chunks JSON sont prêts pour l'indexation.")
