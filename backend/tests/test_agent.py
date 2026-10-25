
import agent
import recommendations
from models import GroupMember, GroupPlanRequest


def make_request():
    return GroupPlanRequest(
        members=[
            GroupMember(
                name="Alex",
                interests=["food", "culture"],
                dislikes=["nightlife"],
            ),
            GroupMember(
                name="Sam",
                interests=["food", "music"],
                dislikes=["hiking"],
            ),
        ],
        location="Bengaluru",
        budget="moderate",
        occasion="weekend",
    )


def make_discovery(status, candidates, unresolved=None):
    return {
        "status": status,
        "candidate_count": len(candidates),
        "candidates": candidates,
        "requested_interests": [],
        "resolved_interests": [],
        "unresolved_interests": unresolved or [],
        "source": "qloo",
        "notice": "Test discovery result.",
    }


def test_plan_prioritizes_shared_interests():
    plan = agent.plan_group_discovery(make_request())

    assert plan["strategy"] == "shared_interest_first"
    assert plan["shared_interests"] == ["food"]
    assert plan["search_interests"] == ["food"]
    assert plan["location"] == "Bengaluru"


def test_plan_uses_combined_interests_when_none_are_shared():
    request = GroupPlanRequest(
        members=[
            GroupMember(name="Alex", interests=["culture"]),
            GroupMember(name="Sam", interests=["music"]),
        ],
        location="Bengaluru",
    )

    plan = agent.plan_group_discovery(request)

    assert plan["strategy"] == "combined_group_interests"
    assert set(plan["search_interests"]) == {"culture", "music"}


def test_evaluation_accepts_sufficient_discovery_results():
    plan = agent.plan_group_discovery(make_request())
    discovery = make_discovery(
        "available",
        [
            {"name": "Place A", "interest_relevance_score": 1},
            {"name": "Place B", "interest_relevance_score": 2},
            {"name": "Place C", "interest_relevance_score": 3},
        ],
    )

    evaluation = agent.evaluate_discovery(discovery, plan)

    assert evaluation["assessment"] == "sufficient"
    assert evaluation["sufficient_candidates"] is True
    assert evaluation["next_action"] == "return_shortlist"


def test_evaluation_requests_broader_discovery_when_results_are_weak():
    plan = agent.plan_group_discovery(make_request())
    discovery = make_discovery(
        "available",
        [{"name": "Place A", "interest_relevance_score": 1}],
        unresolved=["culture"],
    )

    evaluation = agent.evaluate_discovery(discovery, plan)

    assert evaluation["assessment"] == "insufficient_candidates"
    assert evaluation["sufficient_candidates"] is False
    assert evaluation["next_action"] == "consider_broader_discovery"


def test_evaluation_preserves_local_recommendations_when_qloo_unavailable():
    plan = agent.plan_group_discovery(make_request())
    discovery = make_discovery("unavailable", [], unresolved=["food"])

    evaluation = agent.evaluate_discovery(discovery, plan)

    assert evaluation["assessment"] == "unavailable"
    assert evaluation["next_action"] == "preserve_local_recommendations"


def test_agent_broadens_search_after_insufficient_results(monkeypatch):
    request = make_request()
    calls = []

    def fake_discovery(search_request):
        interests = list(search_request.members[0].interests)
        calls.append(interests)

        if len(calls) == 1:
            return make_discovery(
                "available",
                [{"name": "Place A", "interest_relevance_score": 1}],
            )

        return make_discovery(
            "available",
            [
                {"name": "Place A", "interest_relevance_score": 1},
                {"name": "Place B", "interest_relevance_score": 2},
                {"name": "Place C", "interest_relevance_score": 3},
            ],
        )

    monkeypatch.setattr(
        recommendations,
        "discover_qloo_places",
        fake_discovery,
    )

    result = agent.run_group_planning_agent(request)

    assert len(calls) == 2
    assert calls[0] == ["food"]
    assert set(calls[1]) == {"food", "culture", "music"}
    assert result["attempt_count"] == 2
    assert result["discovery"]["candidate_count"] == 3
    assert result["evaluation"]["assessment"] == "sufficient"
    assert result["agent_status"] == "completed"


def test_agent_stops_after_sufficient_first_attempt(monkeypatch):
    calls = []

    def fake_discovery(search_request):
        calls.append(search_request)
        return make_discovery(
            "available",
            [
                {"name": "Place A", "interest_relevance_score": 1},
                {"name": "Place B", "interest_relevance_score": 2},
                {"name": "Place C", "interest_relevance_score": 3},
            ],
        )

    monkeypatch.setattr(
        recommendations,
        "discover_qloo_places",
        fake_discovery,
    )

    result = agent.run_group_planning_agent(make_request())

    assert len(calls) == 1
    assert result["attempt_count"] == 1
    assert result["evaluation"]["sufficient_candidates"] is True


def test_agent_stops_retrying_when_qloo_is_unavailable(monkeypatch):
    calls = []

    def fake_discovery(search_request):
        calls.append(search_request)
        return make_discovery("unavailable", [], unresolved=["food"])

    monkeypatch.setattr(
        recommendations,
        "discover_qloo_places",
        fake_discovery,
    )

    result = agent.run_group_planning_agent(make_request())

    assert len(calls) == 1
    assert result["attempt_count"] == 1
    assert result["agent_status"] == "completed_with_fallback"
    assert result["evaluation"]["assessment"] == "unavailable"
    assert result["discovery"]["candidates"] == []
