import csv

# Définir les chemins d'entrée et de sortie
input_file = r"C:\Users\moham\Music\2\Production_Crops_Livestock_E_All_Data_(Normalized).csv"
output_file = r"C:\Users\moham\Music\2\Production_Crops_Livestock_Afrique.csv"

# Liste des codes FAO des pays africains (les codes commencent par "'")
african_country_codes = {
    "'012", "'024", "'072", "'204", "'854", "'108", "'120", "'140", "'148", "'174",
    "'178", "'180", "'226", "'232", "'231", "'262", "'818", "'732", "'266", "'270",
    "'288", "'324", "'624", "'324", "'384", "'404", "'426", "'430", "'434", "'450",
    "'454", "'466", "'478", "'480", "'175", "'504", "'508", "'516", "'562", "'566",
    "'638", "'646", "'678", "'686", "'694", "'706", "'728", "'729", "'748", "'768"
}

# Ouvrir les fichiers d'entrée et de sortie
with open(input_file, 'r', encoding='utf-8') as infile, \
     open(output_file, 'w', newline='', encoding='utf-8') as outfile:

    reader = csv.reader(infile)
    writer = csv.writer(outfile)

    # Écrire l'en-tête (si le fichier en a un)
    header = next(reader)
    writer.writerow(header)

    # Filtrer les lignes
    for row in reader:
        if len(row) > 1 and row[1] in african_country_codes:
            writer.writerow(row)

print("Filtrage terminé. Les données africaines ont été sauvegardées dans:", output_file)
