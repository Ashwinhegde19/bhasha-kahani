from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import time

from app.config import get_settings
from app.routers import auth, stories, audio, users, choices

settings = get_settings()
allowed_origins = [origin.strip() for origin in settings.cors_origins.split(",") if origin.strip()]
allow_credentials = "*" not in allowed_origins

app = FastAPI(
    title="Bhasha Kahani API",
    description="Multilingual Interactive Folktale Storytelling API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)


# CORS - Allow frontend to call API
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins or ["http://localhost:3000"],
    allow_credentials=allow_credentials,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response


# Include routers
app.include_router(auth.router, prefix="/auth", tags=["Authentication"])
app.include_router(stories.router, prefix="/stories", tags=["Stories"])
app.include_router(audio.router, prefix="/audio", tags=["Audio"])
app.include_router(users.router, prefix="/users", tags=["Users"])
app.include_router(choices.router, prefix="/choices", tags=["Choices"])
# Keep canonical story choice route for API-spec compatibility.
app.include_router(choices.router, prefix="/stories", tags=["Choices"])


@app.get("/")
async def root():
    return {"message": "Bhasha Kahani API", "version": "1.0.0", "docs": "/docs"}


@app.get("/health")
async def health_check():
    return {"status": "healthy"}
