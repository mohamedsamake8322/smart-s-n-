import os
import pandas as pd

# 📁 Dossier contenant les fichiers CSV
folder_path = r"C:\Users\moham\Music\Moh"

# 📊 Dictionnaire pour stocker les colonnes par fichier
schema_dict = {}

# 🔍 Parcours des fichiers
for filename in os.listdir(folder_path):
    if filename.endswith(".csv"):
        file_path = os.path.join(folder_path, filename)
        try:
            df = pd.read_csv(file_path, nrows=5)  # Lecture rapide
            schema_dict[filename] = list(df.columns)
        except Exception as e:
            schema_dict[filename] = [f"Erreur de lecture: {e}"]

# 📋 Analyse des colonnes
all_columns = set()
for cols in schema_dict.values():
    if isinstance(cols, list):
        all_columns.update(cols)

# 🧠 Rapport fusion
report_lines = []
report_lines.append("🧾 Rapport de colonnes pour fusion\n")
report_lines.append(f"📁 Dossier analysé : {folder_path}\n")
report_lines.append("📦 Colonnes par fichier :\n")

for file, cols in schema_dict.items():
    report_lines.append(f"\n➡️ {file} :")
    if isinstance(cols, list):
        for col in cols:
            report_lines.append(f"   - {col}")
    else:
        report_lines.append(f"   ⚠️ {cols}")

report_lines.append("\n🧮 Colonnes totales détectées :")
for col in sorted(all_columns):
    report_lines.append(f" - {col}")

# 📝 Sauvegarde du rapport
report_path = os.path.join(folder_path, "fusion_schema_report.txt")
with open(report_path, "w", encoding="utf-8") as f:
    f.write("\n".join(report_lines))

print(f"✅ Rapport généré : {report_path}")
