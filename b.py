import joblib

# 🔹 Charger le modèle et le vectorizer
model, vectorizer, texts = joblib.load("voice_assistant_model.pkl")

# 🔹 Exemple de question à tester
query = "Comment fertiliser le maïs ?"

# 🔹 Transformer la requête en vecteur TF-IDF
query_vec = vectorizer.transform([query])

# 🔹 Trouver les 3 blocs les plus proches
distances, indices = model.kneighbors(query_vec)

print(f"Question : {query}\n")
for rank, idx in enumerate(indices[0]):
    print(f"--- Résultat {rank+1} ---")
    print(f"Distance : {distances[0][rank]:.4f}")
    print(texts[idx][:500], "...")  # Affiche les 500 premiers caractères du texte
    print()
