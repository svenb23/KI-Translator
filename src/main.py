import asyncio
from functools import partial, lru_cache

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

# DeepL
translator = deepl.Translator(settings.deepl_api_key) if settings.deepl_api_key else None


# OPUS-MT
@lru_cache(maxsize=12)
def get_opus_model(src: str, tgt: str):
    from transformers import MarianMTModel, MarianTokenizer
    model_name = f"Helsinki-NLP/opus-mt-{src}-{tgt}"
    tokenizer = MarianTokenizer.from_pretrained(model_name)
    model = MarianMTModel.from_pretrained(model_name)
    return model, tokenizer


def detect_language(text: str) -> str:
    text_lower = text.lower()

    scores = {
        "de": sum(1 for w in ["der", "die", "das", "und", "ist", "ein", "nicht", "auf"] if f" {w} " in f" {text_lower} "),
        "en": sum(1 for w in ["the", "is", "are", "and", "of", "to", "in", "that"] if f" {w} " in f" {text_lower} "),
        "fr": sum(1 for w in ["le", "la", "les", "de", "et", "est", "un", "une"] if f" {w} " in f" {text_lower} "),
        "es": sum(1 for w in ["el", "la", "los", "de", "y", "es", "un", "una"] if f" {w} " in f" {text_lower} "),
    }

    detected = max(scores, key=scores.get)
    return detected if scores[detected] > 0 else "en"


OPUS_DIRECT_PAIRS = {
    ("en", "de"), ("de", "en"),
    ("en", "fr"), ("fr", "en"),
    ("en", "es"), ("es", "en"),
}


def opus_translate_direct(text: str, src: str, tgt: str) -> str:
    model, tokenizer = get_opus_model(src, tgt)
    inputs = tokenizer(text, return_tensors="pt", padding=True, truncation=True)
    translated = model.generate(**inputs)
    return tokenizer.decode(translated[0], skip_special_tokens=True)


def opus_translate(text: str, src: str, tgt: str) -> str:
    if (src, tgt) in OPUS_DIRECT_PAIRS:
        return opus_translate_direct(text, src, tgt)

    # Pivot
    intermediate = opus_translate_direct(text, src, "en")
    return opus_translate_direct(intermediate, "en", tgt)


class TranslateRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=10000)
    target_lang: str = Field(..., pattern="^(de|en|fr|es)$")


class TranslateResponse(BaseModel):
    translated_text: str
    source_lang: str
    target_lang: str
    ai_generated: bool = True  # EU AI Act


# DeepL Endpoint
@app.post("/translate/deepl", response_model=TranslateResponse)
async def translate_deepl(request: TranslateRequest):
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


# OPUS-MT Endpoint
@app.post("/translate/opus", response_model=TranslateResponse)
async def translate_opus(request: TranslateRequest):
    try:
        src = detect_language(request.text)
        tgt = request.target_lang

        # Gleiche Sprache = keine Übersetzung nötig
        if src == tgt:
            return TranslateResponse(
                translated_text=request.text,
                source_lang=src,
                target_lang=tgt,
            )

        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(
            None,
            partial(opus_translate, request.text, src, tgt),
        )
        return TranslateResponse(
            translated_text=result,
            source_lang=src,
            target_lang=tgt,
        )
    except Exception as e:
        raise HTTPException(500, f"Translation failed: {e}")


@app.post("/translate", response_model=TranslateResponse)
async def translate(request: TranslateRequest):
    return await translate_deepl(request)


@app.get("/health")
async def health():
    return {
        "status": "ok",
        "deepl_configured": translator is not None,
        "opus_available": True,
    }
