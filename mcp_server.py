import os
from typing import List, Optional
from fastapi import FastAPI, Query
from pydantic import BaseModel
import json
import pickle
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer

DB_DIR = os.path.join(os.path.dirname(__file__), "vectordb")
app = FastAPI(title="MCP Server - Quotes, Breathing, Affirmations, Journaling")

# ----------------------------
# Data models
# ----------------------------
class QuoteResult(BaseModel):
    id: str
    text: str
    author: Optional[str] = None
    score: Optional[float] = None

class BreathExerciseRequest(BaseModel):
    duration_seconds: int = 60
    pattern: Optional[str] = "box"

# ----------------------------
# Load vector store
# ----------------------------
def load_store():
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
    a_norm = a / (np.linalg.norm(a, axis=1, keepdims=True) + 1e-10)
    b_norm = b / (np.linalg.norm(b, axis=1, keepdims=True) + 1e-10)
    return np.dot(a_norm, b_norm.T)

@app.on_event("startup")
def startup_event():
    global documents, embeddings, embedder
    documents, embeddings, embedder = load_store()

# ----------------------------
# Quotes endpoint
# ----------------------------
@app.get("/quotes/search", response_model=List[QuoteResult])
def search_quotes(q: Optional[str] = Query(None, min_length=1), k: int = Query(5, ge=1, le=20)):
    if not q:
        import random
        doc = random.choice(documents)
        return [QuoteResult(
            id=doc.get("id"),
            text=doc.get("text"),
            author=doc.get("meta", {}).get("author"),
            score=1.0
        )]

    q_emb = embedder.transform([q]).toarray()
    sims = cosine_similarity(q_emb, embeddings)[0]
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

# ----------------------------
# Breathing exercises
# ----------------------------
@app.post("/breathing/suggest")
def suggest_breathing(req: BreathExerciseRequest):
    patterns = {
        "box": ["inhale 4s", "hold 4s", "exhale 4s", "hold 4s"],
        "4-7-8": ["inhale 4s", "hold 7s", "exhale 8s"],
        "coherent": ["inhale 5s", "exhale 5s"],
    }
    chosen = patterns.get(req.pattern, patterns['box'])
    avg_cycle = sum(int(s.split()[1].replace('s','')) for s in chosen) / len(chosen)
    cycles = max(1, int(req.duration_seconds / avg_cycle))

    plan = []
    for _ in range(cycles):
        for step in chosen:
            plan.append(step)

    return {"duration_seconds": req.duration_seconds, "pattern": req.pattern, "steps": plan}

# ----------------------------
# Affirmations
# ----------------------------
AFFIRMATIONS = [
    "I am worthy of love and happiness.",
    "I trust myself and my intuition.",
    "I am capable of overcoming any challenge.",
    "I choose to focus on the positive today.",
    "I am proud of who I am becoming."
]

@app.get("/affirmations")
def get_affirmations(count: int = 3):
    import random
    return {"affirmations": random.sample(AFFIRMATIONS, min(count, len(AFFIRMATIONS)))}

# ----------------------------
# Journal prompts
# ----------------------------
JOURNAL_PROMPTS = [
    "What are three things you are grateful for today?",
    "Write about a recent challenge and how you overcame it.",
    "Describe a moment that made you smile this week.",
    "What is one intention you want to set for tomorrow?",
    "Reflect on a habit you want to improve and why."
]

@app.get("/journal/prompt")
def get_journal_prompt():
    import random
    return {"prompt": random.choice(JOURNAL_PROMPTS)}

# ----------------------------
# Run locally
# ----------------------------
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("mcp_server:app", host="127.0.0.1", port=8000, reload=True)
