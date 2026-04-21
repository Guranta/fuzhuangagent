from fastapi import FastAPI
from fastapi.responses import JSONResponse
from app.api.routes import router
from app.core.config import settings
from app.core.lifespan import lifespan

app = FastAPI(
    title=settings.APP_TITLE,
    version=settings.APP_VERSION,
    lifespan=lifespan,
)

app.include_router(router, prefix="/api/v1")


@app.get("/health")
async def health():
    return {"status": "ok", "version": settings.APP_VERSION}


@app.get("/ready")
async def ready():
    downloader = getattr(app.state, "downloader", None)
    whisper = getattr(app.state, "whisper", None)
    if downloader is None or whisper is None:
        return JSONResponse({"status": "not_ready"}, status_code=503)
    return {"status": "ready", "version": settings.APP_VERSION}
