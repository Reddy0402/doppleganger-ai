import os
import sys
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

# Ensure root directory is on sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from backend.app.core.config import settings
from backend.app.core.security import ephemeral_manager
from backend.app.database.db import init_db
from backend.app.services.match_service import init_gallery_index
from backend.app.api.routes import router as api_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: ensure database and precomputed gallery index are loaded
    init_db()
    init_gallery_index()
    ephemeral_manager.cleanup_expired()
    yield
    # Shutdown
    ephemeral_manager.cleanup_expired()

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Doppelgänger AI: Biometrically Private Perceptual Lookalike Retrieval API",
    lifespan=lifespan
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Mount API routes
app.include_router(api_router, prefix=settings.API_V1_STR)

@app.get("/")
def read_root():
    return {
        "app": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "docs_url": "/docs",
        "health_url": f"{settings.API_V1_STR}/health"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.app.main:app", host=settings.HOST, port=settings.PORT, reload=settings.DEBUG)
