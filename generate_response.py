from vector_store import VectorStore
import openai  # ou autre API GPT que tu utilises

store = VectorStore()
store.load_store("vector_store.pkl")

query = "Quelle est l’origine du palmier à huile et où est-il cultivé ?"
results = store.search(query)

context = "\n".join([r['content'] for r in results])

prompt = f"""
Voici des extraits de documents agronomiques :
{context}

Question : {query}
Réponse pédagogique et adaptée :
"""

# Appel à GPT (exemple avec OpenAI)
response = openai.ChatCompletion.create(
    model="gpt-4",
    messages=[{"role": "user", "content": prompt}]
)

print("🧠 Réponse générée :")
print(response['choices'][0]['message']['content'])
