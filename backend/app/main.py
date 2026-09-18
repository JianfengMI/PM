from pathlib import Path

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from backend.app.auth import get_current_user
from backend.app.datastore import Board, JsonDataStore, UserRecord


STATIC_DIR = Path(__file__).resolve().parent.parent / "static"

app = FastAPI(title="Project Management MVP")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:3000", "http://localhost:3000"],
    allow_credentials=False,
    allow_methods=["GET", "PUT"],
    allow_headers=["Authorization", "Content-Type"],
)

if (STATIC_DIR / "_next").is_dir():
    app.mount("/_next", StaticFiles(directory=STATIC_DIR / "_next"), name="next-static")


@app.get("/api/hello")
def hello() -> dict[str, str]:
    return {"message": "Hello from the Project Management API"}


def get_datastore() -> JsonDataStore:
    return JsonDataStore()


@app.get("/api/board", response_model=Board)
def read_board(
    user: UserRecord = Depends(get_current_user),
) -> Board:
    return user.board


@app.put("/api/board", response_model=Board)
def update_board(
    board: Board,
    user: UserRecord = Depends(get_current_user),
    datastore: JsonDataStore = Depends(get_datastore),
) -> Board:
    try:
        Board.validate_consistency(board)
        return datastore.update_board(user.id, board)
    except (KeyError, ValueError) as error:
        raise HTTPException(
            status_code=422,
            detail="Invalid board",
        ) from error


@app.get("/api/users/{user_id}/board", response_model=Board)
def read_user_board(
    user_id: str,
    user: UserRecord = Depends(get_current_user),
    datastore: JsonDataStore = Depends(get_datastore),
) -> Board:
    if user_id != user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")
    try:
        return datastore.get_user(user_id).board
    except KeyError as error:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found") from error


@app.put("/api/users/{user_id}/board", response_model=Board)
def update_user_board(
    user_id: str,
    board: Board,
    user: UserRecord = Depends(get_current_user),
    datastore: JsonDataStore = Depends(get_datastore),
) -> Board:
    if user_id != user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")
    try:
        Board.validate_consistency(board)
        return datastore.update_board(user_id, board)
    except (KeyError, ValueError) as error:
        raise HTTPException(
            status_code=422,
            detail="Invalid board",
        ) from error


@app.get("/{path:path}", response_class=FileResponse)
def static_page(path: str = "") -> FileResponse:
    requested_path = (STATIC_DIR / path).resolve()
    if requested_path.is_file() and STATIC_DIR.resolve() in requested_path.parents:
        return FileResponse(requested_path)
    return FileResponse(STATIC_DIR / "index.html")
