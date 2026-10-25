
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from agent import run_group_planning_agent
from models import GroupPlanRequest
from recommendations import recommend_experiences


app = FastAPI(
    title="CommonGround AI API",
    description=(
        "Cultural intelligence for group experiences, "
        "with transparent recommendation scoring, "
        "Qloo-powered place discovery, and agent-driven "
        "discovery planning and evaluation."
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
        "https://commonground-ai.vercel.app",
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
    # Keep local recommendations independent of Qloo availability.
    recommendations = recommend_experiences(request)

    # The agent plans discovery, evaluates the results, and may broaden
    # the search when the initial available results are insufficient.
    agent_result = run_group_planning_agent(request)
    qloo_discovery = agent_result["discovery"]

    return {
        # Existing response fields are preserved for frontend compatibility.
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

        # New agent execution metadata.
        "agent": {
            "name": "CommonGround Group Planning Agent",
            "status": agent_result["agent_status"],
            "plan": agent_result["plan"],
            "attempt_count": agent_result["attempt_count"],
            "attempts": agent_result["attempts"],
            "evaluation": agent_result["evaluation"],
        },
    }
