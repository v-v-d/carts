from pathlib import Path

from fastapi import Request
from fastapi.templating import Jinja2Templates


templates_path = Path(__file__).parent.parent / "views"
templates = Jinja2Templates(directory=str(templates_path))


async def index(request: Request) -> templates.TemplateResponse:
    return templates.TemplateResponse(name="layouts/application.html", context={"request": request})
