from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from shared.cors import add_cors

STATIC = Path(__file__).resolve().parent / "static"

app = FastAPI(title="CreatorLoop UI", version="0.1.0")
add_cors(app)
app.mount("/static", StaticFiles(directory=STATIC), name="static")


@app.get("/health")
def health() -> dict:
    return {"service": "ui_client", "status": "ok"}


@app.get("/")
def index() -> FileResponse:
    return FileResponse(STATIC / "index.html")
