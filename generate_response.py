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
messages = [
    {
        "role": "system",
        "content": "Tu es un assistant agronomique expert. Réponds de façon claire, pédagogique et synthétique en te basant uniquement sur les extraits fournis."
    },
    {
        "role": "user",
        "content": f"""
Voici des extraits de documents techniques :

{context}

Question : {query}
Réponse :
"""
    }
]

# 🧠 Appel à GPT (nouvelle syntaxe)
response = openai.chat.completions.create(
    model="gpt-4",
    messages=messages,
    temperature=0.3
)

# 📊 Affichage de la réponse
print("\n🧠 Réponse générée :\n")
print(response.choices[0].message.content.strip())
