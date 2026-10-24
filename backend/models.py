
from typing import Literal

from pydantic import BaseModel, Field, model_validator


class GroupMember(BaseModel):
    name: str = Field(min_length=1, max_length=40)
    interests: list[str] = Field(min_length=1, max_length=10)
    dislikes: list[str] = Field(default_factory=list, max_length=10)


class GroupPlanRequest(BaseModel):
    members: list[GroupMember] = Field(min_length=2, max_length=8)
    location: str = Field(min_length=2, max_length=120)
    budget: Literal["low", "moderate", "premium"] = "moderate"
    occasion: Literal[
        "casual",
        "celebration",
        "date",
        "weekend",
        "team_outing",
    ] = "casual"

    @model_validator(mode="after")
    def validate_group(self):
        names = [member.name.strip().casefold() for member in self.members]

        if any(not name for name in names):
            raise ValueError("Member names cannot be blank.")

        if len(names) != len(set(names)):
            raise ValueError("Each group member must have a unique name.")

        return self


class ExperienceRecommendation(BaseModel):
    title: str = Field(min_length=1, max_length=120)
    category: str = Field(min_length=1, max_length=60)
    compatibility_score: int = Field(ge=0, le=100)
    explanation: str = Field(min_length=1, max_length=500)
    tradeoffs: list[str] = Field(default_factory=list, max_length=10)
