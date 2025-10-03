MCP Server (minimal)

This workspace contains a minimal example of:

- a Chroma-backed vector DB (stored in `vectordb/`) populated with a few quotes
- a small FastAPI server (`mcp_server.py`) exposing two endpoints:
  - GET /quotes/search?q=...&k=...  — semantic search over stored quotes
  - POST /breathing/suggest  — returns a breathing exercise plan

Quick start (Windows PowerShell):

1. Create a virtual env and install deps:

```powershell
python -m venv .venv; .\.venv\Scripts\Activate.ps1; pip install -r requirements.txt
```

2. Populate the DB:

```powershell
python data_setup.py
```

3. Run the server:

```powershell
python mcp_server.py
```

4. Try endpoints (examples):

GET quote search

```powershell
curl "http://127.0.0.1:8000/quotes/search?q=doubts&k=3"
```

POST breathing suggestion

```powershell
curl -X POST "http://127.0.0.1:8000/breathing/suggest" -H "Content-Type: application/json" -d '{"duration_seconds":60,"pattern":"box"}'
```
