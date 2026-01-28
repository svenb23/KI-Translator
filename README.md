Zum Testen:
1. .env erstellen
2. DEEPL_API_KEY eintragen
2. pip install -r requirements.txt
3. uvicorn src.main:app --reload
4. Frontend öffnen: frontend/index.html im Browser öffnen
5. API-Docs: http://localhost:8000/docs

Endpoints:
- POST /translate/deepl - DeepL API (braucht API-Key)
- POST /translate/opus - OPUS-MT (lokal, kein Key nötig)
- GET /health - Status

Hinweis: OPUS-MT lädt beim ersten Aufruf Modelle (~300MB pro Sprachpaar).
