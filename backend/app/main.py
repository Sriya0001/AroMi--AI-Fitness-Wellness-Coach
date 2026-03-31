from fastapi import FastAPI # Re-triggering reload
from fastapi.middleware.cors import CORSMiddleware
from app.core.database import Base, engine
from app.core.config import settings
from app.routers import auth, users, workout, nutrition, progress, ai, calendar, spotify, reviews, favourites

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="ArogyaMitra API",
    description="AI-powered fitness platform with AROMI coach",
    version="1.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        settings.FRONTEND_URL, 
        "http://localhost:5173", 
        "http://localhost:5174", 
        "http://localhost:5175", 
        "http://127.0.0.1:5173", 
        "http://127.0.0.1:5174", 
        "http://127.0.0.1:5175", 
        "http://localhost:3000"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(workout.router)
app.include_router(nutrition.router)
app.include_router(progress.router)
app.include_router(ai.router)
app.include_router(calendar.router)
app.include_router(spotify.router)
app.include_router(reviews.router)
app.include_router(favourites.router)


@app.get("/")
def root():
    return {"message": "ArogyaMitra API is running 🏃", "docs": "/docs"}


@app.get("/health")
def health():
    return {"status": "healthy", "version": "1.0.0"}
