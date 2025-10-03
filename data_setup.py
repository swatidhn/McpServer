import os
from typing import List

"""Create a simple local vector store persisted to disk.

This avoids depending on Chroma and its migration path. The store files created
under `vectordb/` are:
- documents.json (list of {id,text,meta})
- embeddings.npy (numpy array of shape [n, d])
- vectorizer.pkl (pickled TfidfVectorizer)

The `mcp_server.py` expects this layout.
"""

from typing import List
import os
import json
import pickle
from sklearn.feature_extraction.text import TfidfVectorizer
import numpy as np

DB_DIR = os.path.join(os.path.dirname(__file__), "vectordb")

QUOTES = [
    {"id": "q1", "text": "The only limit to our realization of tomorrow is our doubts of today.", "meta": {"author": "Franklin D. Roosevelt"}},
    {"id": "q2", "text": "In the end, we will remember not the words of our enemies, but the silence of our friends.", "meta": {"author": "Martin Luther King Jr."}},
    {"id": "q3", "text": "Life is what happens when you're busy making other plans.", "meta": {"author": "John Lennon"}},
    {"id": "q4", "text": "Do not go where the path may lead, go instead where there is no path and leave a trail.", "meta": {"author": "Ralph Waldo Emerson"}},
]


class SimpleTFIDFEmbedder:
    def __init__(self, texts: List[str]):
        self.vectorizer = TfidfVectorizer()
        self.vectorizer.fit(texts)

    def embed(self, texts: List[str]) -> List[List[float]]:
        mat = self.vectorizer.transform(texts)
        # convert to dense floats
        return mat.toarray().tolist()


def setup_db():
    os.makedirs(DB_DIR, exist_ok=True)

    texts = [q["text"] for q in QUOTES]
    embedder = SimpleTFIDFEmbedder(texts)
    embeddings = np.array(embedder.embed(texts), dtype=np.float32)

    # Save documents
    docs = [{"id": q["id"], "text": q["text"], "meta": q.get("meta", {})} for q in QUOTES]
    with open(os.path.join(DB_DIR, "documents.json"), "w", encoding="utf8") as f:
        json.dump(docs, f, ensure_ascii=False, indent=2)

    # Save embeddings and pickled vectorizer
    np.save(os.path.join(DB_DIR, "embeddings.npy"), embeddings)
    with open(os.path.join(DB_DIR, "vectorizer.pkl"), "wb") as f:
        pickle.dump(embedder.vectorizer, f)

    print(f"Created simple vector store with {len(docs)} quotes at {DB_DIR}")


if __name__ == "__main__":
    setup_db()
 