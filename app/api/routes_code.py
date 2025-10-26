# app/api/routes_code.py
import os
import uuid
import shutil
import tempfile
import subprocess
from typing import List, Optional
from pathlib import Path

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel

# Router
router = APIRouter()

# Workspace: all file operations are constrained to this directory.
BASE_DIR = Path(__file__).resolve().parents[2]  # up two levels to 'app'
WORKSPACE = BASE_DIR / "workspace"
WORKSPACE.mkdir(parents=True, exist_ok=True)


# ---------- Pydantic models ----------
class FileCreate(BaseModel):
    filename: str  # relative filename, e.g., "hello.py" or "dir/script.py"
    content: str


class FileUpdate(BaseModel):
    content: str


class RunResult(BaseModel):
    stdout: str
    stderr: str
    returncode: int
    timed_out: bool = False


# ---------- Helpers ----------
def _resolve_safe_path(rel_path: str) -> Path:
    """
    Resolve a user-supplied relative path to an absolute Path inside WORKSPACE.
    Prevents path traversal attacks by ensuring the final path is contained in WORKSPACE.
    """
    requested = (WORKSPACE / rel_path).resolve()
    try:
        requested.relative_to(WORKSPACE.resolve())
    except Exception:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid filename/path")
    return requested


def _ensure_parent_dir(path: Path):
    if not path.parent.exists():
        path.parent.mkdir(parents=True, exist_ok=True)


# ---------- File endpoints ----------
@router.get("/files", response_model=List[str])
def list_files():
    """Return list of files under workspace (relative paths)."""
    files = []
    for root, _, filenames in os.walk(WORKSPACE):
        for f in filenames:
            full = Path(root) / f
            rel = full.relative_to(WORKSPACE)
            files.append(str(rel))
    return files


@router.get("/files/{file_path:path}")
def read_file(file_path: str):
    """Read file contents. `file_path` is relative to workspace."""
    path = _resolve_safe_path(file_path)
    if not path.exists() or not path.is_file():
        raise HTTPException(status_code=404, detail="File not found")
    return {"filename": str(path.relative_to(WORKSPACE)), "content": path.read_text(encoding="utf-8")}


@router.post("/files", status_code=status.HTTP_201_CREATED)
def create_file(payload: FileCreate):
    """
    Create a new file. If file exists, return 409 (conflict) to avoid accidental overwrite.
    Use update endpoint to modify.
    """
    path = _resolve_safe_path(payload.filename)
    if path.exists():
        raise HTTPException(status_code=409, detail="File already exists")
    _ensure_parent_dir(path)
    path.write_text(payload.content, encoding="utf-8")
    return {"filename": str(path.relative_to(WORKSPACE)), "detail": "created"}


@router.put("/files/{file_path:path}")
def update_file(file_path: str, payload: FileUpdate):
    """Create or overwrite the file at path with provided content."""
    path = _resolve_safe_path(file_path)
    _ensure_parent_dir(path)
    path.write_text(payload.content, encoding="utf-8")
    return {"filename": str(path.relative_to(WORKSPACE)), "detail": "written"}


@router.delete("/files/{file_path:path}")
def delete_file(file_path: str):
    path = _resolve_safe_path(file_path)
    if not path.exists():
        raise HTTPException(status_code=404, detail="File not found")
    path.unlink()
    # if empty parent directories remain, optionally remove them (here we keep them)
    return {"filename": str(path.relative_to(WORKSPACE)), "detail": "deleted"}


# ---------- Code execution (cautious) ----------
def _run_python_file_safely(file_path: Path, timeout_seconds: int = 5) -> RunResult:
    """
    Run a python file in a temporary isolated working directory.
    NOTE: This is NOT a full sandbox. For production, run inside a container or use
    a dedicated sandbox service. Here we:
      - copy the file to a temp dir
      - run `python <file>` with subprocess and a timeout
      - limit runtime with timeout and return captured stdout/stderr
    """
    # create temporary dir per run, copy the user's file
    temp_dir = Path(tempfile.mkdtemp(prefix="run_workspace_"))
    try:
        # copy only that file (preserve relative filename)
        target = temp_dir / file_path.name
        shutil.copy2(file_path, target)

        # Build command. Use the same Python interpreter running this process.
        cmd = [shutil.which("python") or "python", str(target)]

        try:
            proc = subprocess.run(
                cmd,
                cwd=str(temp_dir),
                capture_output=True,
                text=True,
                timeout=timeout_seconds,
            )
            return RunResult(stdout=proc.stdout, stderr=proc.stderr, returncode=proc.returncode, timed_out=False)
        except subprocess.TimeoutExpired as te:
            # best-effort: attempt to kill and return partial output
            return RunResult(stdout=te.stdout or "", stderr=(te.stderr or "") + "\nProcess timed out", returncode=124, timed_out=True)
    finally:
        # cleanup
        try:
            shutil.rmtree(temp_dir)
        except Exception:
            pass


@router.post("/run/{file_path:path}", response_model=RunResult)
def run_file(file_path: str, timeout: Optional[int] = 5):
    """
    Execute a python file stored in the workspace.
    Query param `timeout` (seconds) controls max execution time (default=5s).
    Security notes:
      - This endpoint executes arbitrary python code. Only use in trusted/local environments.
      - For production, containerize runs, use OS resource limits, drop privileges, or use a sandbox service.
    """
    path = _resolve_safe_path(file_path)
    if not path.exists() or not path.is_file():
        raise HTTPException(status_code=404, detail="File not found")

    # Disallow running files that don't have a .py extension by default
    if path.suffix != ".py":
        raise HTTPException(status_code=400, detail="Only python (.py) files can be executed via this endpoint")

    result = _run_python_file_safely(path, timeout_seconds=timeout)
    return result
