from qloo_client import (
    QlooAPIError,
    QlooConfigurationError,
    get_qloo_insights,
    search_qloo_tags,
)


INTEREST_ALIASES = {
    "food": ["food", "restaurants", "cuisine"],
    "street food": ["street food", "food"],
    "restaurants": ["restaurants", "food"],
    "cooking": ["cooking", "food"],
    "music": ["music"],
    "concerts": ["concerts", "music"],
    "singing": ["singing", "music"],
    "dancing": ["dancing", "music"],
    "art": ["art"],
    "museums": ["museums", "art"],
    "history": ["history"],
    "photography": ["photography", "art"],
    "nature": ["nature"],
    "hiking": ["hiking"],
    "walking": ["walking", "hiking"],
    "adventure": ["adventure", "hiking"],
    "sports": ["sports"],
    "crafts": ["crafts", "art"],
    "painting": ["painting", "art"],
    "design": ["design", "art"],
    "games": ["games"],
    "board games": ["board games", "games"],
    "cafes": ["cafes", "coffee"],
    "coffee": ["coffee", "cafes"],
    "movies": ["movies", "film"],
    "films": ["film", "movies"],
    "cinema": ["cinema", "film"],
    "travel": ["travel"],
    "culture": ["culture", "art"],
    "nightlife": ["nightlife", "music"],
}

PREFERRED_TAG_PREFIXES = (
    "urn:tag:activity:",
    "urn:tag:hobby:",
    "urn:tag:interests:",
    "urn:tag:activities:place:",
    "urn:tag:genre:",
    "urn:tag:cuisine:",
)

EXCLUDED_CATEGORY_TERMS = (
    "guest_house",
    "guest house",
    "hostel",
    "hotel",
    "accommodation",
    "paying guest",
    "residential",
    "real estate",
    "book store",
    "bookstore",
    "clothing store",
    "shoe store",
    "electronics store",
    "supermarket",
    "grocery store",
    "shopping mall",
    "university",
    "college",
    "school",
    "software company",
    "engineering company",
    "office",
    "warehouse",
)

# Specific evidence is preferred over broad words such as "nature"
# or "sports", which can produce false-positive matches.
INTEREST_EVIDENCE = {
    "hiking": {
        "phrases": {"hiking", "trekking", "hiking trail", "trek"},
        "tag_fragments": {"hiking", "trekking"},
    },
    "nature": {
        "phrases": {
            "nature reserve",
            "nature trail",
            "botanical garden",
            "national park",
            "nature park",
            "wildlife sanctuary",
        },
        "tag_fragments": {
            "nature",
            "outdoor_experiences",
            "hiking",
        },
    },
    "sports": {
        "phrases": {
            "sports complex",
            "sports club",
            "sports facility",
            "recreation center",
            "recreational club",
            "sports arena",
        },
        "tag_fragments": {
            "sports",
            "sporting",
            "recreation",
        },
    },
    "food": {
        "phrases": {"restaurant", "food", "dining", "cuisine"},
        "tag_fragments": {"cuisine", "restaurant", "dining"},
    },
    "street food": {
        "phrases": {"street food", "food stall", "quick bite"},
        "tag_fragments": {"street_food", "quick_bite"},
    },
    "restaurants": {
        "phrases": {"restaurant", "dining", "cuisine"},
        "tag_fragments": {"restaurant", "cuisine", "dining"},
    },
    "cooking": {
        "phrases": {
            "cooking class",
            "cooking workshop",
            "culinary workshop",
        },
        "tag_fragments": {"cooking_class", "cooking_workshop"},
    },
    "music": {
        "phrases": {"live music", "music venue", "concert venue"},
        "tag_fragments": {"music", "concert"},
    },
    "concerts": {
        "phrases": {"concert venue", "live concert", "live music"},
        "tag_fragments": {"concert"},
    },
    "singing": {
        "phrases": {"singing class", "karaoke", "vocal workshop"},
        "tag_fragments": {"karaoke", "singing"},
    },
    "dancing": {
        "phrases": {"dance studio", "dance class", "dance floor"},
        "tag_fragments": {"dance", "dancing"},
    },
    "art": {
        "phrases": {"art gallery", "art museum", "art studio"},
        "tag_fragments": {"artistic", "gallery"},
    },
    "museums": {
        "phrases": {"museum", "historical exhibition"},
        "tag_fragments": {"museum", "exhibition"},
    },
    "history": {
        "phrases": {
            "historical site",
            "heritage site",
            "historic monument",
            "history museum",
        },
        "tag_fragments": {"history", "heritage", "historical"},
    },
    "photography": {
        "phrases": {
            "photography studio",
            "photo exhibition",
            "photography workshop",
        },
        "tag_fragments": {"photography"},
    },
    "walking": {
        "phrases": {"walking trail", "nature walk", "walking tour"},
        "tag_fragments": {"walking_trail", "walking_tour"},
    },
    "adventure": {
        "phrases": {
            "adventure park",
            "adventure sports",
            "rock climbing",
            "zip line",
        },
        "tag_fragments": {"adventure", "climbing", "trekking"},
    },
    "crafts": {
        "phrases": {"craft workshop", "pottery workshop", "handmade crafts"},
        "tag_fragments": {"craft_workshop", "pottery"},
    },
    "painting": {
        "phrases": {"painting class", "painting workshop", "paint studio"},
        "tag_fragments": {"painting", "paint_workshop"},
    },
    "design": {
        "phrases": {"design workshop", "design studio"},
        "tag_fragments": {"design_workshop"},
    },
    "games": {
        "phrases": {"gaming arcade", "board game cafe", "game center"},
        "tag_fragments": {"gaming", "board_games", "arcade"},
    },
    "board games": {
        "phrases": {"board game cafe", "board game club"},
        "tag_fragments": {"board_games"},
    },
    "cafes": {
        "phrases": {"cafe", "coffee shop", "coffeehouse"},
        "tag_fragments": {"cafe", "coffee"},
    },
    "coffee": {
        "phrases": {"coffee shop", "coffeehouse", "coffee roastery"},
        "tag_fragments": {"coffee"},
    },
    "movies": {
        "phrases": {"movie theater", "cinema", "film screening"},
        "tag_fragments": {"cinema", "movie"},
    },
    "films": {
        "phrases": {"film screening", "cinema", "movie theater"},
        "tag_fragments": {"film", "cinema"},
    },
    "cinema": {
        "phrases": {"cinema", "movie theater", "film screening"},
        "tag_fragments": {"cinema", "movie"},
    },
    "travel": {
        "phrases": {
            "guided tour",
            "sightseeing tour",
            "tourist attraction",
        },
        "tag_fragments": {"sightseeing", "tourist_attraction"},
    },
    "culture": {
        "phrases": {
            "cultural center",
            "cultural centre",
            "cultural heritage",
            "cultural exhibition",
        },
        "tag_fragments": {"cultural", "heritage"},
    },
    "nightlife": {
        "phrases": {"nightclub", "live music bar", "nightlife venue"},
        "tag_fragments": {"nightlife", "nightclub"},
    },
}


def normalize(value: str) -> str:
    return " ".join(value.casefold().strip().split())


def _as_text(value) -> str:
    """Convert nested Qloo metadata into searchable text safely."""

    if value is None:
        return ""

    if isinstance(value, str):
        return value

    if isinstance(value, (int, float, bool)):
        return str(value)

    if isinstance(value, list):
        return " ".join(_as_text(item) for item in value)

    if isinstance(value, dict):
        return " ".join(
            _as_text(item)
            for key, item in value.items()
            if key not in {"id", "weight", "count"}
        )

    return ""


def _entity_text(entity: dict) -> str:
    """Combine descriptive fields, tags and keywords."""

    properties = entity.get("properties", {})
    if not isinstance(properties, dict):
        properties = {}

    address = properties.get("address", {})
    if isinstance(address, dict):
        address_text = " ".join(
            _as_text(address.get(key, ""))
            for key in ("label", "display_address")
        )
    else:
        address_text = _as_text(address)

    fields = [
        entity.get("name"),
        entity.get("subtype"),
        entity.get("type"),
        entity.get("disambiguation"),
        entity.get("tags"),
        properties.get("description"),
        properties.get("short_description"),
        properties.get("overall_description"),
        properties.get("keywords"),
        properties.get("good_for"),
        properties.get("primary_genre"),
        properties.get("cuisine_description"),
        properties.get("specialty_dishes"),
        properties.get("ambience_description"),
        properties.get("physical_setting_description"),
        properties.get("unique_selling_points"),
        address_text,
    ]

    return normalize(
        " ".join(_as_text(value) for value in fields if value)
    )


def _category_text(entity: dict) -> str:
    """Extract category evidence separately from long descriptions."""

    properties = entity.get("properties", {})
    if not isinstance(properties, dict):
        properties = {}

    return normalize(
        " ".join(
            _as_text(value)
            for value in (
                entity.get("name"),
                entity.get("disambiguation"),
                entity.get("subtype"),
                entity.get("type"),
                properties.get("primary_genre"),
            )
            if value
        )
    )


def _is_obviously_irrelevant(entity: dict) -> bool:
    """Exclude clear non-experience categories."""

    category = _category_text(entity)

    return any(
        term in category
        for term in EXCLUDED_CATEGORY_TERMS
    )


def resolve_interest_tag(interest: str) -> dict | None:
    """Resolve an interest to a likely Qloo tag."""

    query = normalize(interest)
    search_terms = INTEREST_ALIASES.get(query, [query])

    for search_term in search_terms:
        data = search_qloo_tags(search_term, take=10)
        results = data.get("results", {})
        if not isinstance(results, dict):
            continue

        tags = results.get("tags", [])
        if not isinstance(tags, list):
            continue

        valid_tags = [
            tag
            for tag in tags
            if isinstance(tag, dict)
            and isinstance(tag.get("id"), str)
            and tag["id"].strip()
        ]

        if not valid_tags:
            continue

        def tag_rank(tag: dict) -> tuple[int, int]:
            tag_name = normalize(str(tag.get("name", "")))
            tag_id = tag["id"]

            exact_name_rank = (
                0 if tag_name == normalize(search_term) else 1
            )

            prefix_rank = next(
                (
                    index
                    for index, prefix in enumerate(PREFERRED_TAG_PREFIXES)
                    if tag_id.startswith(prefix)
                ),
                len(PREFERRED_TAG_PREFIXES),
            )

            return exact_name_rank, prefix_rank

        valid_tags.sort(key=tag_rank)
        return valid_tags[0]

    return None


def resolve_group_tags(
    interests: list[str],
) -> tuple[list[str], list[str]]:
    """Return unique Qloo tag IDs and interests that resolved."""

    tag_ids = []
    resolved_interests = []

    unique_interests = dict.fromkeys(
        normalize(item)
        for item in interests
        if isinstance(item, str) and normalize(item)
    )

    for interest in unique_interests:
        tag = resolve_interest_tag(interest)

        if tag:
            tag_ids.append(tag["id"])
            resolved_interests.append(interest)

    return list(dict.fromkeys(tag_ids)), resolved_interests


def _interest_relevance(
    entity: dict,
    interests: list[str],
) -> int:
    """
    Estimate relevance using specific evidence in Qloo metadata.

    This is our transparent heuristic, not a Qloo-generated score.
    """

    properties = entity.get("properties", {})
    if not isinstance(properties, dict):
        properties = {}

    raw_tags = entity.get("tags", [])
    if not isinstance(raw_tags, list):
        raw_tags = []

    tag_names = {
        normalize(str(tag.get("name", "")))
        for tag in raw_tags
        if isinstance(tag, dict) and tag.get("name")
    }

    tag_ids = {
        normalize(str(tag.get("id", "")))
        for tag in raw_tags
        if isinstance(tag, dict) and tag.get("id")
    }

    description_text = normalize(
        " ".join(
            _as_text(properties.get(field))
            for field in (
                "description",
                "short_description",
                "overall_description",
                "keywords",
                "good_for",
                "primary_genre",
                "physical_setting_description",
                "unique_selling_points",
            )
        )
    )

    matched = 0

    for interest in interests:
        normalized_interest = normalize(interest)
        rules = INTEREST_EVIDENCE.get(normalized_interest)

        # Unknown interests need a specific mapping instead of
        # receiving points from a generic substring match.
        if not rules:
            continue

        phrase_match = any(
            normalize(phrase) in description_text
            for phrase in rules["phrases"]
        )

        # Keep each tag ID paired with its own name. A cross-product
        # here could incorrectly combine an unrelated ID and tag name.
        tag_match = any(
            fragment in normalize(str(tag.get("id", "")))
            or fragment.replace("_", " ")
            in normalize(str(tag.get("name", "")))
            for fragment in rules["tag_fragments"]
            for tag in raw_tags
            if isinstance(tag, dict)
        )

        if phrase_match or tag_match:
            matched += 1

    if not interests:
        return 0

    return round(100 * matched / len(interests))


def _get_address(entity: dict) -> str:
    properties = entity.get("properties", {})
    if not isinstance(properties, dict):
        return ""

    address = properties.get("address", {})

    if isinstance(address, dict):
        return (
            address.get("label")
            or address.get("display_address")
            or ""
        )

    if isinstance(address, str):
        return address

    return ""


def _safe_float(value) -> float:
    """Safely parse optional numeric metadata."""

    try:
        return float(value)
    except (TypeError, ValueError):
        return 0.0


def get_group_place_candidates(
    location: str,
    interests: list[str],
    take: int = 20,
) -> dict:
    """
    Fetch Qloo place candidates influenced by group interests.

    Relevance is a local keyword estimate based on returned metadata.
    Candidates are not guaranteed to be verified venues or have live
    availability.
    """

    if not isinstance(location, str) or not location.strip():
        raise ValueError("Location cannot be blank.")

    if not 1 <= take <= 50:
        raise ValueError("take must be between 1 and 50.")

    clean_interests = list(
        dict.fromkeys(
            normalize(item)
            for item in interests
            if isinstance(item, str) and normalize(item)
        )
    )

    tag_ids, resolved_interests = resolve_group_tags(
        clean_interests
    )

    data = get_qloo_insights(
        location=location.strip(),
        take=take,
        tag_ids=tag_ids or None,
    )

    results = data.get("results", {})
    if not isinstance(results, dict):
        results = {}

    entities = results.get("entities", [])
    if not isinstance(entities, list):
        entities = []

    candidates = []
    seen_ids = set()

    for entity in entities:
        if not isinstance(entity, dict):
            continue

        name = entity.get("name")
        if not isinstance(name, str) or not name.strip():
            continue

        if _is_obviously_irrelevant(entity):
            continue

        entity_id = entity.get("entity_id")

        if entity_id and entity_id in seen_ids:
            continue

        if entity_id:
            seen_ids.add(entity_id)

        properties = entity.get("properties", {})
        if not isinstance(properties, dict):
            properties = {}

        closed = properties.get("is_closed")
        if closed is True:
            continue

        relevance_score = _interest_relevance(
            entity,
            clean_interests,
        )

        # Do not return candidates with no metadata evidence of a match.
        if relevance_score <= 0:
            continue

        candidates.append(
            {
                "entity_id": entity_id,
                "name": name.strip(),
                "subtype": entity.get("subtype"),
                "address": _get_address(entity),
                "popularity": entity.get("popularity"),
                "business_rating": properties.get("business_rating"),
                "price_level": properties.get("price_level"),
                "is_closed": closed,
                "website": properties.get("website"),
                "interest_relevance_score": relevance_score,
                "source": "qloo",
            }
        )

    candidates.sort(
        key=lambda item: (
            item["interest_relevance_score"],
            _safe_float(item["business_rating"]),
            _safe_float(item["popularity"]),
            item["name"].casefold(),
        ),
        reverse=True,
    )

    return {
        "location": location.strip(),
        "requested_interests": clean_interests,
        "resolved_interests": resolved_interests,
        "unresolved_interests": [
            interest
            for interest in clean_interests
            if interest not in resolved_interests
        ],
        "resolved_tag_count": len(tag_ids),
        "candidate_count": len(candidates),
        "candidates": candidates,
        "source": "qloo",
        "notice": (
            "Venue relevance is estimated from Qloo metadata using "
            "specific keyword and tag matching. This is not a Qloo "
            "compatibility score. Candidates are not guaranteed to be "
            "verified venues or to have live availability."
        ),
    }