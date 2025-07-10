from fastapi import FastAPI, Request, Response
from fastapi.templating import Jinja2Templates
from .language_manager import get_user_language, set_user_language
from .translation import SUPPORTED_LANGUAGES

app = FastAPI()
templates = Jinja2Templates(directory="../templates")

@app.middleware("http")
async def language_middleware(request: Request, call_next):
    response = await call_next(request)
    if "lang" in request.query_params:
        set_user_language(response, request.query_params["lang"])
    return response

@app.post("/set-language")
async def change_language(request: Request, response: Response, lang: str):
    set_user_language(response, lang)
    return {"status": "Language updated"}
