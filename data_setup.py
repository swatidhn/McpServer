import os
import json
import pickle
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from typing import List

DB_DIR = os.path.join(os.path.dirname(__file__), "vectordb")

# ---------------- Quotes ----------------
QUOTES = [
    {"id": "q1", "text": "The only limit to our realization of tomorrow is our doubts of today.", "meta": {"author": "Franklin D. Roosevelt"}},
    {"id": "q2", "text": "In the end, we will remember not the words of our enemies, but the silence of our friends.", "meta": {"author": "Martin Luther King Jr."}},
]

# ---------------- Wellness ----------------
WELLNESS = [
    {"id": "g1", "text": "Today I am grateful for my family.", "type": "gratitude"},
    {"id": "m1", "text": "I meditated for 10 minutes and felt calm.", "type": "meditation"},
    {"id": "mo1", "text": "I felt anxious in the morning but improved after breathing.", "type": "mood"},
]

# ---------------- Journal ----------------
JOURNAL_ENTRIES = [
    {"id": "j1", "text": "Reflecting on my day, I realized I handled challenges well.", "type": "journal"},
    {"id": "j2", "text": "I am grateful for the small moments of joy today.", "type": "journal"},
    {"id": "j3", "text": "I want to improve my focus during work hours tomorrow.", "type": "journal"},
]

# ---------------- TF-IDF Embedder ----------------
class SimpleTFIDFEmbedder:
    def __init__(self, texts: List[str]):
        self.vectorizer = TfidfVectorizer()
        self.vectorizer.fit(texts)

    def embed(self, texts: List[str]) -> List[List[float]]:
        mat = self.vectorizer.transform(texts)
        return mat.toarray().tolist()


def create_store():
    os.makedirs(DB_DIR, exist_ok=True)

    # --- Quotes ---
    quote_texts = [q["text"] for q in QUOTES]
    quote_embedder = SimpleTFIDFEmbedder(quote_texts)
    quote_embeddings = np.array(quote_embedder.embed(quote_texts), dtype=np.float32)
    with open(os.path.join(DB_DIR, "documents_documents.json"), "w", encoding="utf8") as f:
        json.dump(QUOTES, f, ensure_ascii=False, indent=2)
    np.save(os.path.join(DB_DIR, "documents_embeddings.npy"), quote_embeddings)
    with open(os.path.join(DB_DIR, "documents_vectorizer.pkl"), "wb") as f:
        pickle.dump(quote_embedder.vectorizer, f)

    # --- Wellness ---
    wellness_texts = [w["text"] for w in WELLNESS]
    wellness_embedder = SimpleTFIDFEmbedder(wellness_texts)
    wellness_embeddings = np.array(wellness_embedder.embed(wellness_texts), dtype=np.float32)
    with open(os.path.join(DB_DIR, "wellness_documents.json"), "w", encoding="utf8") as f:
        json.dump(WELLNESS, f, ensure_ascii=False, indent=2)
    np.save(os.path.join(DB_DIR, "wellness_embeddings.npy"), wellness_embeddings)
    with open(os.path.join(DB_DIR, "wellness_vectorizer.pkl"), "wb") as f:
        pickle.dump(wellness_embedder.vectorizer, f)

    # --- Journal ---
    journal_texts = [j["text"] for j in JOURNAL_ENTRIES]
    journal_embedder = SimpleTFIDFEmbedder(journal_texts)
    journal_embeddings = np.array(journal_embedder.embed(journal_texts), dtype=np.float32)
    with open(os.path.join(DB_DIR, "journal_documents.json"), "w", encoding="utf8") as f:
        json.dump(JOURNAL_ENTRIES, f, ensure_ascii=False, indent=2)
    np.save(os.path.join(DB_DIR, "journal_embeddings.npy"), journal_embeddings)
    with open(os.path.join(DB_DIR, "journal_vectorizer.pkl"), "wb") as f:
        pickle.dump(journal_embedder.vectorizer, f)

    print(f"✅ Vector stores created at {DB_DIR} with:")
    print(f"   - {len(QUOTES)} quotes")
    print(f"   - {len(WELLNESS)} wellness entries")
    print(f"   - {len(JOURNAL_ENTRIES)} journal entries")


if __name__ == "__main__":
    create_store()
