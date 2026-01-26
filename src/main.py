import asyncio
from functools import partial

import deepl
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from .config import settings

app = FastAPI(title="KI-Translator API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

translator = deepl.Translator(settings.deepl_api_key) if settings.deepl_api_key else None


class TranslateRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=10000)
    target_lang: str = Field(..., pattern="^(de|en|fr|es)$")


class TranslateResponse(BaseModel):
    translated_text: str
    source_lang: str
    target_lang: str
    ai_generated: bool = True  # EU AI Act


@app.post("/translate", response_model=TranslateResponse)
async def translate(request: TranslateRequest):
    if not translator:
        raise HTTPException(503, "DeepL API key not configured")

    lang_map = {"de": "DE", "en": "EN-US", "fr": "FR", "es": "ES"}
    target = lang_map[request.target_lang]

    try:
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(
            None,
            partial(translator.translate_text, request.text, target_lang=target),
        )
        return TranslateResponse(
            translated_text=result.text,
            source_lang=result.detected_source_lang.lower(),
            target_lang=request.target_lang,
        )
    except Exception as e:
        raise HTTPException(500, f"Translation failed: {e}")


@app.get("/health")
async def health():
    return {"status": "ok", "deepl_configured": translator is not None}
