
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from models import GroupPlanRequest
from recommendations import (
    discover_qloo_places,
    recommend_experiences,
)

app = FastAPI(
    title="CommonGround AI API",
    description=(
        "Cultural intelligence for group experiences, "
        "with transparent recommendation scoring and "
        "Qloo-powered place discovery."
    ),
    version="0.3.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:5174",
        "http://127.0.0.1:5174",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {
        "message": "Welcome to CommonGround AI",
        "status": "running",
        "version": "0.3.0",
    }


@app.get("/health")
def health():
    return {
        "status": "healthy",
        "service": "CommonGround AI API",
        "version": "0.3.0",
    }


@app.post("/recommendations")
def get_recommendations(request: GroupPlanRequest):
    recommendations = recommend_experiences(request)
    qloo_discovery = discover_qloo_places(request)

    return {
        "location": request.location,
        "budget": request.budget,
        "occasion": request.occasion,
        "member_count": len(request.members),
        "recommendation_count": len(recommendations),
        "engine": "local_transparent_scoring",
        "recommendations": [
            recommendation.model_dump()
            for recommendation in recommendations
        ],
        "qloo_discovery": qloo_discovery,
    }
