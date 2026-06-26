from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from app.utils.limiter import limiter
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os
from app.routes.chat import router
from app.routes.auth import router as auth_router
from dotenv import load_dotenv

load_dotenv()

# FastAPI App
app = FastAPI(
    title="Chef Rolex API 🍳",
    description="AI Powered Recipe Assistant",
    version="1.0.0"
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# CORS — Frontend connect பண்ண allow பண்ணு
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Later specific URL கொடு
    allow_methods=["*"],
    allow_headers=["*"]
)

app.include_router(
    router,
    prefix="/api/v1",
    tags=["Chef Rolex"]
)

# Auth Routes include பண்ணு
app.include_router(
    auth_router,
    prefix="/api/v1/auth",
    tags=["Auth"]
)

# Health check
@app.get("/health")
async def health_check():
    return {
        "message": "Chef Rolex API Running! 🍳",
        "status": "healthy",
        "version": "1.0.0"
    } 

# Mount static files (images, css, js, html)
frontend_path = os.path.join(os.path.dirname(__file__), "frontend")
app.mount("/", StaticFiles(directory=frontend_path, html=True), name="static")