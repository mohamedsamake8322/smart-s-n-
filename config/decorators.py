from functools import wraps
from ..config import translate_text, get_user_language

def translate_page(template_name):
    def decorator(view_func):
        @wraps(view_func)
        async def wrapper(request: Request):
            lang = get_user_language(request)
            context = await view_func(request)
            translated = {k: translate_text(v, lang) for k, v in context.items()}
            return templates.TemplateResponse(
                template_name,
                {"request": request, **translated, "languages": SUPPORTED_LANGUAGES, "current_lang": lang}
            )
        return wrapper
    return decorator
