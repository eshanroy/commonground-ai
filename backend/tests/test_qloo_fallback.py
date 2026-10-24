
import main
import recommendations
from models import GroupMember, GroupPlanRequest


def test_unexpected_qloo_error_preserves_local_recommendations(
    monkeypatch,
):
    """An unexpected Qloo error must not break local recommendations."""

    def raise_unexpected_error(**kwargs):
        raise RuntimeError("Simulated unexpected Qloo failure")

    monkeypatch.setattr(
        recommendations,
        "get_group_place_candidates",
        raise_unexpected_error,
    )

    request = GroupPlanRequest(
        members=[
            GroupMember(name="Eshan", interests=["food", "culture"]),
            GroupMember(name="Alex", interests=["music", "cooking"]),
        ],
        location="Bengaluru",
        budget="moderate",
        occasion="weekend",
    )

    response = main.get_recommendations(request)

    assert response["recommendation_count"] > 0
    assert len(response["recommendations"]) > 0

    qloo_result = response["qloo_discovery"]

    assert qloo_result["status"] == "unavailable"
    assert qloo_result["candidate_count"] == 0
    assert qloo_result["candidates"] == []
    assert "unexpected error" in qloo_result["reason"].lower()
    assert "local compatibility recommendations remain available" in (
        qloo_result["notice"].lower()
    )
