import os
from typing import List, Optional

from fastapi import FastAPI, Query
from pydantic import BaseModel
import os
import json
import pickle
from typing import List, Optional
from sklearn.feature_extraction.text import TfidfVectorizer
import numpy as np

DB_DIR = os.path.join(os.path.dirname(__file__), "vectordb")

app = FastAPI(title="MCP Server - Quotes & Breathing")


class QuoteResult(BaseModel):
    id: str
    text: str
    author: Optional[str] = None
    score: Optional[float] = None


def load_store():
    # documents.json, embeddings.npy, vectorizer.pkl
    docs_path = os.path.join(DB_DIR, "documents.json")
    emb_path = os.path.join(DB_DIR, "embeddings.npy")
    vec_path = os.path.join(DB_DIR, "vectorizer.pkl")

    if not os.path.exists(docs_path) or not os.path.exists(emb_path) or not os.path.exists(vec_path):
        raise RuntimeError("Vector store not found. Run data_setup.py to create it.")

    with open(docs_path, "r", encoding="utf8") as f:
        documents = json.load(f)

    embeddings = np.load(emb_path)
    with open(vec_path, "rb") as f:
        vectorizer = pickle.load(f)

    return documents, embeddings, vectorizer


def cosine_similarity(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    # a: [m, d], b: [n, d] -> [m, n]
    a_norm = a / (np.linalg.norm(a, axis=1, keepdims=True) + 1e-10)
    b_norm = b / (np.linalg.norm(b, axis=1, keepdims=True) + 1e-10)
    return np.dot(a_norm, b_norm.T)


@app.on_event("startup")
def startup_event():
    global documents, embeddings, embedder
    documents, embeddings, embedder = load_store()


@app.get("/quotes/search", response_model=List[QuoteResult])
def search_quotes(q: Optional[str] = Query(None, min_length=1), k: int = Query(5, ge=1, le=20)):
    """
    Search stored quotes by semantic similarity to the query using TF-IDF + cosine.
    If no query is provided, return a random quote.
    """
    if not q:
        # fallback to random
        import random
        idx = random.randint(0, len(documents) - 1)
        doc = documents[idx]
        return [QuoteResult(
            id=doc.get("id"),
            text=doc.get("text"),
            author=doc.get("meta", {}).get("author"),
            score=1.0
        )]

    q_emb = embedder.transform([q]).toarray()
    sims = cosine_similarity(q_emb, embeddings)[0]  # [n]
    top_idx = np.argsort(-sims)[:k]

    out: List[QuoteResult] = []
    for idx in top_idx:
        doc = documents[idx]
        score = float(sims[idx])
        out.append(QuoteResult(
            id=doc.get("id"),
            text=doc.get("text"),
            author=doc.get("meta", {}).get("author"),
            score=score
        ))
    return out

class BreathExerciseRequest(BaseModel):
    duration_seconds: int = 60
    pattern: Optional[str] = "box"  # box, 4-7-8, coherent


@app.post("/breathing/suggest")
def suggest_breathing(req: BreathExerciseRequest):
    """Return a breathing exercise plan given duration and a named pattern."""
    patterns = {
        "box": ["inhale 4s", "hold 4s", "exhale 4s", "hold 4s"],
        "4-7-8": ["inhale 4s", "hold 7s", "exhale 8s"],
        "coherent": ["inhale 5s", "exhale 5s"],
    }
    chosen = patterns.get(req.pattern, patterns['box'])
    # compute how many cycles fit
    avg_cycle = sum(int(s.split()[1].replace('s','')) for s in chosen) / len(chosen)
    cycles = max(1, int(req.duration_seconds / (avg_cycle)))

    plan = []
    for i in range(cycles):
        for step in chosen:
            plan.append(step)

    return {"duration_seconds": req.duration_seconds, "pattern": req.pattern, "steps": plan}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("mcp_server:app", host="127.0.0.1", port=8000, reload=True)
