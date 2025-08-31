import os
import openai
from vector_store import VectorStore

# 🔐 Charger la clé API depuis l'environnement
openai.api_key = os.getenv("OPENAI_API_KEY")

# 📂 Charger la base vectorielle sauvegardée
store = VectorStore()
store.load_store("vector_store.pkl")

# 🔍 Question à poser
query = "Quelle est l’origine du palmier à huile et où est-il cultivé ?"
print(f"\n🔎 Question : {query}")

# 🔎 Recherche sémantique
results = store.search(query, limit=5)

if not results:
    print("❌ Aucun chunk pertinent trouvé.")
    exit()

# 🧠 Construction du contexte à injecter dans GPT
context = "\n\n".join([f"- {r['content'].strip()}" for r in results])

# 🧾 Prompt structuré
prompt = f"""
Tu es un assistant agronomique expert. Voici des extraits de documents techniques :

{context}

En te basant uniquement sur ces extraits, réponds à la question suivante de façon claire, pédagogique et synthétique :

Question : {query}
Réponse :
"""

# 🧠 Appel à GPT
response = openai.ChatCompletion.create(
    model="gpt-4",
    messages=[{"role": "user", "content": prompt}],
    temperature=0.3
)

# 📊 Affichage de la réponse
print("\n🧠 Réponse générée :\n")
print(response['choices'][0]['message']['content'].strip())
