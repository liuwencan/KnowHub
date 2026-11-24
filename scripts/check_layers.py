"""Fail CI if domain imports transport, provider, or persistence frameworks."""
from pathlib import Path

for path in Path("backend/konwhub/domain").rglob("*.py"):
    text = path.read_text(encoding="utf-8")
    forbidden = ["fastapi", "langchain", "sqlalchemy", "redis", "celery"]
    found = [name for name in forbidden if name in text.lower()]
    if found:
        raise SystemExit(f"{path} crosses layer boundary: {', '.join(found)}")

print("layer checks passed")
