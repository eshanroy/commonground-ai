
from models import ExperienceRecommendation, GroupPlanRequest
from qloo_recommendations import (
    QlooAPIError,
    QlooConfigurationError,
    get_group_place_candidates,
)


# Illustrative activity concepts, not verified local venues.
EXPERIENCE_CATALOG = [
    {
        "title": "A food crawl with something for everyone",
        "category": "food",
        "keywords": {
            "food", "street food", "restaurants", "cooking", "culture",
        },
        "budget_tier": "low",
        "budgets": {"low", "moderate"},
    },
    {
        "title": "An arts and culture afternoon",
        "category": "arts",
        "keywords": {
            "art", "arts", "museums", "history", "culture", "photography",
        },
        "budget_tier": "low",
        "budgets": {"low", "moderate"},
    },
    {
        "title": "A live music discovery night",
        "category": "music",
        "keywords": {
            "music", "concerts", "singing", "dancing", "nightlife",
        },
        "budget_tier": "premium",
        "budgets": {"moderate", "premium"},
    },
    {
        "title": "An outdoor adventure together",
        "category": "outdoors",
        "keywords": {
            "nature", "hiking", "walking", "adventure", "sports",
        },
        "budget_tier": "low",
        "budgets": {"low", "moderate"},
    },
    {
        "title": "A creative workshop for the group",
        "category": "creative",
        "keywords": {
            "art", "arts", "crafts", "painting", "cooking", "design",
        },
        "budget_tier": "moderate",
        "budgets": {"moderate", "premium"},
    },
    {
        "title": "A relaxed games and café meetup",
        "category": "social",
        "keywords": {
            "games", "board games", "cafes", "coffee", "conversation",
        },
        "budget_tier": "low",
        "budgets": {"low", "moderate"},
    },
    {
        "title": "A premium tasting experience",
        "category": "tasting",
        "keywords": {
            "food", "cooking", "culture", "restaurants", "coffee",
        },
        "budget_tier": "premium",
        "budgets": {"premium"},
    },
    {
        "title": "A film and discussion night",
        "category": "film",
        "keywords": {
            "movies", "films", "cinema", "storytelling", "culture",
        },
        "budget_tier": "moderate",
        "budgets": {"low", "moderate", "premium"},
    },
    {
        "title": "A discovery day exploring the city",
        "category": "exploration",
        "keywords": {
            "travel", "history", "photography", "walking", "culture",
        },
        "budget_tier": "low",
        "budgets": {"low", "moderate"},
    },
]


# Transparent aliases for common equivalent terms.
INTEREST_ALIASES = {
    "arts": "art",
    "films": "movies",
    "film": "movies",
    "cinema": "movies",
    "cafes": "coffee",
    "café": "coffee",
    "cafés": "coffee",
    "restaurants": "food",
    "street food": "food",
}


def normalize(value: str) -> str:
    return " ".join(value.casefold().strip().split())


def canonicalize_interest(value: str) -> str:
    normalized = normalize(value)
    return INTEREST_ALIASES.get(normalized, normalized)


def score_experience(
    candidate: dict,
    request: GroupPlanRequest,
) -> ExperienceRecommendation:
    members = request.members
    member_count = len(members)

    keywords = {
        canonicalize_interest(keyword)
        for keyword in candidate["keywords"]
    }

    member_matches = {}
    member_dislikes = {}
    member_interest_counts = {}

    for member in members:
        interests = {
            canonicalize_interest(item)
            for item in member.interests
        }
        dislikes = {
            canonicalize_interest(item)
            for item in member.dislikes
        }

        member_matches[member.name] = sorted(interests & keywords)
        member_dislikes[member.name] = sorted(dislikes & keywords)
        member_interest_counts[member.name] = len(interests)

    matched_members = [
        member.name
        for member in members
        if member_matches[member.name]
    ]

    unmatched_members = [
        member.name
        for member in members
        if not member_matches[member.name]
    ]

    conflicting_members = [
        member.name
        for member in members
        if member_dislikes[member.name]
    ]

    # Component 1: group coverage (0-40).
    coverage_score = 40 * len(matched_members) / member_count

    # Component 2: average individual interest alignment (0-30).
    individual_scores = []

    for member in members:
        interest_count = member_interest_counts[member.name]
        match_count = len(member_matches[member.name])

        individual_scores.append(
            match_count / interest_count if interest_count else 0.0
        )

    individual_score = (
        30 * sum(individual_scores) / member_count
    )

    # Identify interests independently matched by multiple members.
    interest_counts = {}

    for member in members:
        for interest in member_matches[member.name]:
            interest_counts[interest] = (
                interest_counts.get(interest, 0) + 1
            )

    shared_interests = sorted(
        interest
        for interest, count in interest_counts.items()
        if count >= 2
    )

    # Component 3: group interest alignment (0-20).
    # Shared interests earn up to 12 points.
    shared_score = 12 * min(len(shared_interests) / 2, 1)

    # Complementary interests earn up to 8 points when at least two
    # members match the concept through different interest sets.
    matched_interest_sets = [
        frozenset(member_matches[member.name])
        for member in members
        if member_matches[member.name]
    ]

    distinct_matched_interests = {
        interest
        for interest_set in matched_interest_sets
        for interest in interest_set
    }

    has_complementary_matches = (
        len(matched_interest_sets) >= 2
        and len(distinct_matched_interests) >= 2
        and len(set(matched_interest_sets)) >= 2
    )

    complementary_score = (
        8 if has_complementary_matches else 0
    )

    group_alignment_score = shared_score + complementary_score

    # Component 4: estimated budget alignment (0-10).
    # These tiers are illustrative activity estimates, not venue prices.
    budget_order = {"low": 0, "moderate": 1, "premium": 2}
    selected_tier = budget_order[request.budget]
    estimated_tier = budget_order[candidate["budget_tier"]]
    tier_distance = abs(selected_tier - estimated_tier)
    budget_score = {0: 10, 1: 6, 2: 2}[tier_distance]

    # Penalize activities that conflict with stated dislikes.
    dislike_penalty = min(
        45,
        25 * len(conflicting_members) / member_count
        + 10 * max(0, len(conflicting_members) - 1),
    )

    score = round(
        max(
            0,
            min(
                100,
                coverage_score
                + individual_score
                + group_alignment_score
                + budget_score
                - dislike_penalty,
            ),
        )
    )

    # Explain how many people have a direct match.
    if len(matched_members) == member_count:
        coverage_explanation = (
            f"All {member_count} members have at least one "
            "matching interest."
        )
    elif matched_members:
        coverage_explanation = (
            f"{len(matched_members)} of {member_count} members have "
            "a direct interest match; others may be compromising."
        )
    else:
        coverage_explanation = (
            "No members have a direct interest match for this concept."
        )

    # Show exactly which interests match for each person.
    member_details = []

    for member in members:
        matches = member_matches[member.name]

        if matches:
            member_details.append(
                f"{member.name}: {', '.join(matches)}"
            )
        else:
            member_details.append(
                f"{member.name}: no direct keyword match"
            )

    member_explanation = (
        "Individual matches: " + "; ".join(member_details) + "."
    )

    if shared_interests:
        shared_explanation = (
            "Shared interests: " + ", ".join(shared_interests) + "."
        )
    else:
        shared_explanation = (
            "No shared keyword interests were found for this concept."
        )

    if has_complementary_matches:
        complementary_explanation = (
            "Complementary matches: members match this activity "
            "through different interests, which may offer a way "
            "to bring their preferences together."
        )
    else:
        complementary_explanation = ""

    explanation_parts = [
        coverage_explanation,
        member_explanation,
        shared_explanation,
    ]

    if complementary_explanation:
        explanation_parts.append(complementary_explanation)

    explanation_parts.append(
        f"Budget alignment: {budget_score}/10 "
        f"(estimated activity tier: {candidate['budget_tier']}; "
        f"selected tier: {request.budget})."
    )

    explanation = " ".join(explanation_parts)

    tradeoffs = []

    if unmatched_members:
        tradeoffs.append(
            "No direct keyword match for: "
            + ", ".join(unmatched_members)
        )

    if conflicting_members:
        conflict_details = [
            f"{name} ({', '.join(member_dislikes[name])})"
            for name in conflicting_members
        ]
        tradeoffs.append(
            "Conflicts with stated dislikes: "
            + "; ".join(conflict_details)
        )

    if budget_score < 10:
        tradeoffs.append(
            f"Estimated budget tier is {candidate['budget_tier']}, "
            f"while the group selected {request.budget}."
        )

    return ExperienceRecommendation(
        title=candidate["title"],
        category=candidate["category"],
        compatibility_score=score,
        explanation=explanation,
        tradeoffs=tradeoffs,
    )


def recommend_experiences(
    request: GroupPlanRequest,
) -> list[ExperienceRecommendation]:
    recommendations = [
        score_experience(candidate, request)
        for candidate in EXPERIENCE_CATALOG
    ]

    # Deterministic ordering: score first, then title.
    recommendations.sort(
        key=lambda item: (
            item.compatibility_score,
            item.title,
        ),
        reverse=True,
    )

    selected = []
    seen_categories = set()

    for recommendation in recommendations:
        if recommendation.category in seen_categories:
            continue

        selected.append(recommendation)
        seen_categories.add(recommendation.category)

        if len(selected) >= 5:
            break

    return selected


def _collect_group_interests(
    request: GroupPlanRequest,
) -> list[str]:
    """Return unique normalized interests from all group members."""

    interests = []
    seen = set()

    for member in request.members:
        for interest in member.interests:
            cleaned = normalize(interest)

            if cleaned and cleaned not in seen:
                interests.append(cleaned)
                seen.add(cleaned)

    return interests


def discover_qloo_places(request: GroupPlanRequest) -> dict:
    """
    Discover Qloo places using the group's combined interests.

    Venue candidates are separate from compatibility-ranked concepts.
    The metadata relevance estimate is not a Qloo compatibility score
    and does not verify venue suitability or availability.
    """

    interests = _collect_group_interests(request)

    if not interests:
        return {
            "status": "skipped",
            "reason": "No group interests were provided.",
            "location": request.location,
            "requested_interests": [],
            "resolved_interests": [],
            "unresolved_interests": [],
            "resolved_tag_count": 0,
            "candidate_count": 0,
            "candidates": [],
            "source": "qloo",
            "notice": (
                "No Qloo search was made because the group has no interests."
            ),
        }

    try:
        result = get_group_place_candidates(
            location=request.location,
            interests=interests,
            take=20,
        )
    except (QlooConfigurationError, QlooAPIError) as exc:
        return {
            "status": "unavailable",
            "reason": str(exc),
            "location": request.location,
            "requested_interests": interests,
            "resolved_interests": [],
            "unresolved_interests": interests,
            "resolved_tag_count": 0,
            "candidate_count": 0,
            "candidates": [],
            "source": "qloo",
            "notice": (
                "Qloo place discovery is temporarily unavailable. "
                "The local compatibility recommendations remain available."
            ),
        }
    except Exception:
        # Keep local activity recommendations available if an unexpected
        # error occurs in the Qloo discovery integration.
        return {
            "status": "unavailable",
            "reason": "An unexpected error occurred during Qloo discovery.",
            "location": request.location,
            "requested_interests": interests,
            "resolved_interests": [],
            "unresolved_interests": interests,
            "resolved_tag_count": 0,
            "candidate_count": 0,
            "candidates": [],
            "source": "qloo",
            "notice": (
                "Qloo place discovery encountered an unexpected error. "
                "The local compatibility recommendations remain available."
            ),
        }

    result["status"] = "available"
    return result
