import os
import fitz  # 🚀 PyMuPDF for extracting images
import logging

# ✅ Configuration du logger
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

def extract_images_from_pdf(pdf_path, output_folder="extracted_images/", image_format="png"):
    """Extrait toutes les images d'un PDF et les enregistre au format choisi."""

    # 🔹 Vérifier si le fichier PDF existe
    if not os.path.exists(pdf_path):
        logger.error(f"⚠️ Erreur : Le fichier {pdf_path} est introuvable.")
        return  

    # 🔹 Créer le dossier pour les images extraites s'il n'existe pas
    os.makedirs(output_folder, exist_ok=True)

    # 🔹 Ouvrir le PDF
    doc = fitz.open(pdf_path)
    image_count = 0  # ✅ Compteur d'images extraites

    # 🔹 Extraire les images de chaque page
    for i, page in enumerate(doc):
        images = page.get_images(full=True)

        for img_index, img in enumerate(images):
            xref = img[0]  # ID unique de l’image
            pix = fitz.Pixmap(doc, xref)

            # 🔹 Sauvegarder l’image extraite avec le format choisi
            image_path = os.path.join(output_folder, f"image_{i+1}_{img_index+1}.{image_format}")
            pix.save(image_path)

            image_count += 1
            logger.info(f"✅ Image extraite et sauvegardée : {image_path}")

    doc.close()
    
    logger.info(f"🚀 Extraction terminée ! {image_count} images enregistrées.")

# 🔥 Interface dynamique pour l’utilisateur
if __name__ == "__main__":
    pdf_path = input("📂 Entrez le chemin du fichier PDF à analyser : ")
    output_folder = input("📁 Dossier de stockage des images (extracted_images/) : ") or "extracted_images/"
    image_format = input("🖼 Format d'image (png, jpg, bmp...) : ") or "png"

    extract_images_from_pdf(pdf_path, output_folder, image_format)