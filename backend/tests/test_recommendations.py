
import pytest
from pydantic import ValidationError

from models import GroupPlanRequest
from recommendations import (
    EXPERIENCE_CATALOG,
    recommend_experiences,
    score_experience,
)


def make_request(members=None, budget="moderate"):
    if members is None:
        members = [
            {
                "name": "Alex",
                "interests": ["food", "culture"],
                "dislikes": ["nightlife"],
            },
            {
                "name": "Sam",
                "interests": ["food", "music"],
                "dislikes": ["hiking"],
            },
        ]

    return GroupPlanRequest(
        members=members,
        location="Bengaluru",
        budget=budget,
        occasion="weekend",
    )


def find_candidate(category):
    return next(
        item
        for item in EXPERIENCE_CATALOG
        if item["category"] == category
    )


def test_recommendations_return_valid_scores():
    results = recommend_experiences(make_request())

    assert len(results) == 5

    for result in results:
        assert 0 <= result.compatibility_score <= 100
        assert result.title
        assert result.category
        assert result.explanation
        assert isinstance(result.tradeoffs, list)


def test_shared_food_interest_is_explained():
    results = recommend_experiences(make_request())

    food = next(
        result
        for result in results
        if result.category == "food"
    )

    assert food.compatibility_score > 0
    assert "food" in food.explanation.lower()
    assert "All 2 members" in food.explanation


def test_dislike_reduces_matching_experience_score():
    candidate = find_candidate("music")

    without_dislike = make_request(
        members=[
            {"name": "Alex", "interests": ["music"], "dislikes": []},
            {"name": "Sam", "interests": ["music"], "dislikes": []},
        ]
    )

    with_dislike = make_request(
        members=[
            {
                "name": "Alex",
                "interests": ["music"],
                "dislikes": ["nightlife"],
            },
            {"name": "Sam", "interests": ["music"], "dislikes": []},
        ]
    )

    score_without = score_experience(
        candidate, without_dislike
    ).compatibility_score

    score_with = score_experience(
        candidate, with_dislike
    ).compatibility_score

    assert score_with < score_without


def test_budget_alignment_changes_score():
    candidate = find_candidate("tasting")

    moderate = score_experience(
        candidate,
        make_request(budget="moderate"),
    )

    premium = score_experience(
        candidate,
        make_request(budget="premium"),
    )

    assert premium.compatibility_score > moderate.compatibility_score
    assert any(
        "budget" in item.lower()
        for item in moderate.tradeoffs
    )


def test_duplicate_member_names_are_rejected():
    with pytest.raises(ValidationError):
        make_request(
            members=[
                {
                    "name": "Alex",
                    "interests": ["food"],
                    "dislikes": [],
                },
                {
                    "name": "alex",
                    "interests": ["music"],
                    "dislikes": [],
                },
            ]
        )


def test_results_are_deterministic():
    request = make_request()

    first = recommend_experiences(request)
    second = recommend_experiences(request)

    assert [item.model_dump() for item in first] == [
        item.model_dump() for item in second
    ]


def test_shortlist_contains_unique_categories():
    results = recommend_experiences(make_request())

    categories = [result.category for result in results]

    assert len(results) == 5
    assert len(categories) == len(set(categories))
