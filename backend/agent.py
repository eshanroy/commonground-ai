
"""Planning, execution, and evaluation for the CommonGround agent."""

from collections import Counter

from models import GroupPlanRequest


MIN_CANDIDATES = 3
MAX_DISCOVERY_ATTEMPTS = 2


def plan_group_discovery(request: GroupPlanRequest) -> dict:
    """Create a discovery plan from the group's preferences."""

    interest_counts = Counter(
        interest.strip().casefold()
        for member in request.members
        for interest in member.interests
        if interest.strip()
    )

    shared_interests = sorted(
        interest
        for interest, count in interest_counts.items()
        if count == len(request.members)
    )

    group_interests = list(interest_counts)
    search_interests = shared_interests or group_interests

    return {
        "strategy": (
            "shared_interest_first"
            if shared_interests
            else "combined_group_interests"
        ),
        "location": request.location.strip(),
        "budget": request.budget,
        "occasion": request.occasion,
        "member_count": len(request.members),
        "shared_interests": shared_interests,
        "group_interests": group_interests,
        "search_interests": search_interests,
        "constraints": {
            "budget": request.budget,
            "occasion": request.occasion,
            "dislikes": sorted({
                dislike.strip().casefold()
                for member in request.members
                for dislike in member.dislikes
                if dislike.strip()
            }),
        },
    }


def evaluate_discovery(discovery: dict, plan: dict) -> dict:
    """Assess discovery results without claiming official Qloo scores."""

    candidates = discovery.get("candidates", [])
    if not isinstance(candidates, list):
        candidates = []

    candidate_count = len(candidates)

    unresolved = discovery.get("unresolved_interests", [])
    if not isinstance(unresolved, list):
        unresolved = []

    sufficient = (
        discovery.get("status") == "available"
        and candidate_count >= MIN_CANDIDATES
    )

    if discovery.get("status") != "available":
        assessment = "unavailable"
        next_action = "preserve_local_recommendations"
    elif sufficient:
        assessment = "sufficient"
        next_action = "return_shortlist"
    else:
        assessment = "insufficient_candidates"
        next_action = "consider_broader_discovery"

    return {
        "assessment": assessment,
        "candidate_count": candidate_count,
        "minimum_candidate_target": MIN_CANDIDATES,
        "sufficient_candidates": sufficient,
        "unresolved_interests": unresolved,
        "next_action": next_action,
        "evaluation_note": (
            "Candidate sufficiency is based on result count and discovery "
            "status. It does not establish venue quality, group satisfaction, "
            "real-time availability, or an official Qloo compatibility score."
        ),
    }


def run_group_planning_agent(request: GroupPlanRequest) -> dict:
    """Plan discovery, evaluate results, and broaden the search if needed."""

    # Import at runtime to avoid a circular module import and preserve
    # recommendations.py's existing discovery function and test seams.
    import recommendations

    plan = plan_group_discovery(request)
    attempts = []
    current_interests = plan["search_interests"]

    discovery = {
        "status": "skipped",
        "candidate_count": 0,
        "candidates": [],
        "requested_interests": [],
        "resolved_interests": [],
        "unresolved_interests": [],
        "reason": "No interests were available for discovery.",
        "source": "qloo",
        "notice": "Local compatibility recommendations remain available.",
    }

    for attempt_number in range(1, MAX_DISCOVERY_ATTEMPTS + 1):
        # Keep the original group and its preferences for local scoring.
        # For Qloo discovery, give each copied member the interests chosen
        # by the planner. The original request is never mutated.
        search_members = [
            member.model_copy(update={"interests": current_interests})
            for member in request.members
        ]
        search_request = request.model_copy(
            update={"members": search_members}
        )

        discovery = recommendations.discover_qloo_places(search_request)
        evaluation = evaluate_discovery(discovery, plan)

        attempts.append({
            "attempt": attempt_number,
            "strategy": (
                "shared_interest_first"
                if current_interests == plan["shared_interests"]
                and plan["shared_interests"]
                else "combined_group_interests"
            ),
            "searched_interests": list(current_interests),
            "status": discovery.get("status", "unknown"),
            "candidate_count": evaluation["candidate_count"],
            "assessment": evaluation["assessment"],
            "decision": evaluation["next_action"],
        })

        if evaluation["sufficient_candidates"]:
            break

        if discovery.get("status") != "available":
            break

        if attempt_number >= MAX_DISCOVERY_ATTEMPTS:
            break

        broader_interests = plan["group_interests"]

        if current_interests == broader_interests:
            break

        # The evaluation determines whether to broaden discovery.
        if evaluation["next_action"] != "consider_broader_discovery":
            break

        current_interests = broader_interests

    final_evaluation = evaluate_discovery(discovery, plan)

    return {
        "plan": plan,
        "attempt_count": len(attempts),
        "attempts": attempts,
        "evaluation": final_evaluation,
        "discovery": discovery,
        "agent_status": (
            "completed"
            if discovery.get("status") == "available"
            else "completed_with_fallback"
        ),
    }
