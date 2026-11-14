import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent
BACKEND_PATH = PROJECT_ROOT / "backend"
sys.path.insert(0, str(BACKEND_PATH))

from main import app

app.frontend(
    "/",
    directory=str(PROJECT_ROOT / "frontend" / "dist"),
    fallback="index.html",
)
