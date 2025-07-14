import fitz  # PyMuPDF
import pandas as pd
import re

def extract_text_from_pdf(pdf_path):
    doc = fitz.open(pdf_path)
    text = ""
    for page in doc:
        text += page.get_text()
    return text

def parse_fertilizer_prices(text):
    lines = text.split("\n")
    data = []
    for line in lines:
        if re.search(r"(Urea|NPK|DAP|MOP)", line):
            match = re.findall(r"([A-Za-z\s]+)\s+(Urea|NPK|DAP|MOP)\s+(\d+\.?\d*)", line)
            for m in match:
                data.append({
                    "Country": m[0].strip(),
                    "Product": m[1],
                    "Price": float(m[2])
                })
    return pd.DataFrame(data)

def export_to_csv(df, out_path="data/fertilizer/fertilizer_prices.csv"):
    df.to_csv(out_path, index=False)

# 🧪 Exemple d'utilisation
text = extract_text_from_pdf("data/fertilizer/FertilizerWatch_July2025.pdf")
df_prices = parse_fertilizer_prices(text)
export_to_csv(df_prices)
print(df_prices.head())
