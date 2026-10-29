# SENTINEL X

Cross-platform digital forensics and defensive incident investigation application.

## Stack
- Frontend: Flutter/Dart (Android, Web, Windows, Linux)
- Backend: Python 3.12 + FastAPI + SQLAlchemy 2.x + PostgreSQL
- Local engine: Python (Windows/Linux)
- AI: Ollama Cloud (server-side only)

## Quick start (backend)
```bash
cd services/sentinel_api
cp .env.example .env  # or use provided .env
# edit .env with DATABASE_URL, JWT_SECRET
python -m pip install -r requirements.txt
python -m uvicorn app.main:app --reload --port 8000
```

## Run tests
```bash
cd services/sentinel_api
python -m pytest -q
cd ../sentinel_local
python -m pytest -q
```

## Flutter
```bash
cd apps/sentinel_flutter
flutter pub get
flutter run -d chrome
flutter build web
```

## Ollama Cloud
Set in server .env only:
```
OLLAMA_API_KEY=
OLLAMA_MODEL=
AI_ENABLED=false
```
Never put the key in Flutter or web builds.

## Platform capability matrix
| Feature | Android | Web | Windows | Linux |
|---|---|---|---|---|
| Case management | yes | yes | yes | yes |
| File hashing | yes (picked files) | yes (picked files) | yes (local engine) | yes (local engine) |
| Log investigation | yes | yes | yes | yes |
| Integrity monitoring | limited | limited | yes | yes |
| Local agent | no | no | yes | yes |