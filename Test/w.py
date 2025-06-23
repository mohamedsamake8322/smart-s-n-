# 🧾 Script Python — Extraction de texte depuis un PDF
import fitz  # PyMuPDF
import json

def extraire_texte_pdf(pdf_path):
    doc = fitz.open(pdf_path)
    contenu = ""
    for page in doc:
        contenu += page.get_text()
    return contenu

# Exemple d’utilisation :
texte = extraire_texte_pdf(r"C:\Users\moham\Desktop\1\Tomato_Disease.pdf")


# Sauvegarde brute du texte
with open("contenu_pdf.txt", "w", encoding="utf-8") as f:
    f.write(texte)

print("✅ Texte extrait et enregistré dans 'contenu_pdf.txt'")
