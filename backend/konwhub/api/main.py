import uvicorn

from konwhub.api.app import create_app

app = create_app()


def main() -> None:
    uvicorn.run("konwhub.api.main:app", host="0.0.0.0", port=8000)
