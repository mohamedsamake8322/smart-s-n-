import os
import fitz  # 🚀 PyMuPDF for extracting images

def extract_images_from_pdf(pdf_path, output_folder="extracted_images/"):
    """Extracts all images from a user-selected PDF and saves them in a folder."""
    
    # 🔹 Vérifier si le fichier PDF existe
    if not os.path.exists(pdf_path):
        print(f"⚠️ Erreur : Le fichier {pdf_path} est introuvable. Veuillez sélectionner un PDF valide.")
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
            
            # 🔹 Sauvegarder l’image extraite
            image_path = os.path.join(output_folder, f"image_{i+1}_{img_index+1}.png")
            pix.save(image_path)
            
            image_count += 1
            print(f"✅ Image extraite et sauvegardée : {image_path}")

    doc.close()
    
    print(f"🚀 Extraction terminée ! {image_count} images extraites.")

# 🔹 Exécution dynamique sans exemple statique
if __name__ == "__main__":
    pdf_path = input("📂 Entrez le chemin du fichier PDF à analyser : ")
    extract_images_from_pdf(pdf_path)
