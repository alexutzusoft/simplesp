from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from typing import List, Optional
from src.ssp_engine import SSPEngine
import uvicorn
import os

app = FastAPI(title="Simple SP (Sentence Prediction)")
engine = SSPEngine()

# Static files for the UI
static_dir = os.path.join(os.path.dirname(__file__), "static")
if not os.path.exists(static_dir):
    os.makedirs(static_dir)

class PredictionRequest(BaseModel):
    text: str
    limit: Optional[int] = 1

class PredictionResponse(BaseModel):
    predictions: List[str]

@app.post("/predict", response_model=PredictionResponse)
async def predict(req: PredictionRequest):
    # Pass limit to engine. If limit is 0 or very high, engine handles it.
    results = engine.predict(req.text, limit=req.limit)
    return PredictionResponse(predictions=results)

@app.get("/stats")
async def stats():
    engine.refresh_if_needed()
    return {
        "sentences": len(engine.corpus),
        "files": len([f for f in os.listdir(engine.data_dir) if f.endswith((".txt", ".py"))])
    }

# For serving index.html
@app.get("/", response_class=HTMLResponse)
async def read_index():
    with open(os.path.join(static_dir, "index.html"), "r", encoding="utf-8") as f:
        return f.read()

# Serve other static files
app.mount("/static", StaticFiles(directory=static_dir), name="static")

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
