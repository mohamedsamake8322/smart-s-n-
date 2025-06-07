import os
import fitz  # 🚀 PyMuPDF for extracting images

def extract_images_from_pdf(pdf_path, output_folder="extracted_images/"):
    """Extracts all images from a PDF and saves them in a folder."""
    
    # 🔹 Check if the PDF file exists
    if not os.path.exists(pdf_path):
        print(f"⚠️ Warning: The file {pdf_path} was not found. Skipping extraction.")
        return  # Quitte proprement la fonction sans erreur

    # 🔹 Create the folder for storing extracted images
    os.makedirs(output_folder, exist_ok=True)

    # 🔹 Open the PDF
    doc = fitz.open(pdf_path)
    
    image_count = 0  # ✅ Counter for extracted images

    # 🔹 Extract images from each page
    for i, page in enumerate(doc):
        images = page.get_images(full=True)
        
        for img_index, img in enumerate(images):
            xref = img[0]  # Unique image ID
            pix = fitz.Pixmap(doc, xref)
            
            # 🔹 Save the extracted image
            image_path = os.path.join(output_folder, f"image_{i+1}_{img_index+1}.png")
            pix.save(image_path)
            
            image_count += 1
            print(f"✅ Image extracted and saved: {image_path}")

    doc.close()
    
    print(f"🚀 Extraction complete! {image_count} images extracted.")

# 🔹 Test the function
if __name__ == "__main__":
    extract_images_from_pdf("example.pdf")
