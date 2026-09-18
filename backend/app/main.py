from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles


STATIC_DIR = Path(__file__).resolve().parent.parent / "static"

app = FastAPI(title="Project Management MVP")

if (STATIC_DIR / "_next").is_dir():
    app.mount("/_next", StaticFiles(directory=STATIC_DIR / "_next"), name="next-static")


@app.get("/api/hello")
def hello() -> dict[str, str]:
    return {"message": "Hello from the Project Management API"}


@app.get("/{path:path}", response_class=FileResponse)
def static_page(path: str = "") -> FileResponse:
    requested_path = (STATIC_DIR / path).resolve()
    if requested_path.is_file() and STATIC_DIR.resolve() in requested_path.parents:
        return FileResponse(requested_path)
    return FileResponse(STATIC_DIR / "index.html")
