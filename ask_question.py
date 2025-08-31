from vector_store import VectorStore

# Initialiser la base vectorielle
store = VectorStore()

# 🔍 Question à poser
query = "Quelle est l’origine du palmier à huile et où est-il cultivé ?"

# 🔎 Recherche sémantique
results = store.search(query)

# 📊 Affichage des résultats
if not results:
    print("❌ Aucun résultat pertinent trouvé.")
else:
    for r in results:
        print(f"\n📄 Fichier : {r['filename']} (score: {r['similarity']:.2f})")
        print(f"🧠 Contenu : {r['content']}")
        print(f"🏷️ Métadonnées : {r['metadata']}")
