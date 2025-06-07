import os
from gimpfu import *
from gimpfu import LAYER_MODE_NORMAL

def extract_images_from_pdf(image, drawable):
    """Sépare et enregistre les images extraites d'un PDF importé dans GIMP."""
    
    if not drawable:
        raise ValueError("🚨 Erreur : Aucun calque actif pour la copie d'image.")

    width, height = image.width, image.height
    num_images = 3  # Ajuste selon le nombre d’images à extraire

    single_image_width = width // num_images  # Division automatique
    single_image_height = height  # Hauteur constante

    save_directory = "C:\Boua\images"  # 📌 Modifie selon ton projet
    os.makedirs(save_directory, exist_ok=True)

    for i in range(num_images):
        x_offset = i * single_image_width
        
        # 🔹 Créer une nouvelle image pour l'extraction
        new_image = pdb.gimp_image_new(single_image_width, single_image_height, image.base_type)
        new_layer = pdb.gimp_layer_new(new_image, single_image_width, single_image_height, image.base_type, f"Image_{i+1}", 100, LAYER_MODE_NORMAL)
        pdb.gimp_image_add_layer(new_image, new_layer, 0)

        # 🔹 Copier et coller la partie sélectionnée
        pdb.gimp_edit_copy(drawable)
        new_drawable = pdb.gimp_image_get_active_drawable(new_image)
        pdb.gimp_edit_paste(new_drawable, True)

        # 🔹 Sauvegarde de l'image extraite
        save_path = os.path.join(save_directory, f"image_{i+1}.png")
        pdb.gimp_file_save(new_image, new_drawable, save_path, "")
        pdb.gimp_image_delete(new_image)

        print(f"✅ Image extraite et sauvegardée : {save_path}")

register(
    "python_fu_extract_images",
    "Extraction automatique des images",
    "Sépare les images d'une page PDF importée",
    "Toi", "Libre", "2025",
    "<Image>/Filters/Automatisation/Extraire Images",
    "RGB*, GRAY*",
    [],
    [],
    extract_images_from_pdf)

main()
