
import os

import httpx
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))

QLOO_API_KEY = os.getenv("QLOO_API_KEY", "").strip()
QLOO_API_URL = os.getenv(
    "QLOO_API_URL",
    "https://hackathon.api.qloo.com",
).rstrip("/")


class QlooConfigurationError(Exception):
    """Raised when Qloo credentials are missing."""


class QlooAPIError(Exception):
    """Raised when a Qloo request fails."""


def _get_json(endpoint: str, params: dict) -> dict:
    if not QLOO_API_KEY:
        raise QlooConfigurationError(
            "QLOO_API_KEY is missing. Configure backend/.env."
        )

    try:
        response = httpx.get(
            f"{QLOO_API_URL}{endpoint}",
            headers={
                "X-Api-Key": QLOO_API_KEY,
                "Accept": "application/json",
            },
            params=params,
            timeout=45.0,
        )
    except httpx.RequestError as exc:
        raise QlooAPIError(
            "Could not connect to Qloo. Check your connection and API URL."
        ) from exc

    if response.status_code in (401, 403):
        raise QlooAPIError(
            f"Qloo authentication/access failed (HTTP {response.status_code})."
        )

    if response.status_code >= 400:
        raise QlooAPIError(
            f"Qloo returned HTTP {response.status_code} for {endpoint}. "
            "Check the documented parameters and API access."
        )

    try:
        data = response.json()
    except ValueError as exc:
        raise QlooAPIError(
            "Qloo returned a response that was not valid JSON."
        ) from exc

    if not isinstance(data, dict):
        raise QlooAPIError("Qloo returned an unexpected response structure.")

    return data


def get_qloo_insights(
    location: str = "Bengaluru",
    take: int = 10,
    tag_ids: list[str] | None = None,
) -> dict:
    """Fetch place insights, optionally influenced by Qloo interest tags."""

    location = location.strip()

    if not location:
        raise ValueError("Location cannot be blank.")

    if not 1 <= take <= 50:
        raise ValueError("take must be between 1 and 50.")

    params = {
        "filter.type": "urn:entity:place",
        "filter.location.query": location,
        "take": take,
        "feature.explainability": "true",
    }

    clean_tag_ids = list(
        dict.fromkeys(
            tag.strip()
            for tag in (tag_ids or [])
            if isinstance(tag, str) and tag.strip()
        )
    )

    if clean_tag_ids:
        params["signal.interests.tags"] = ",".join(clean_tag_ids)
        params["operator.signal.interests.tags"] = "union"

    return _get_json("/v2/insights", params)


def search_qloo_tags(query: str, take: int = 10) -> dict:
    """Search Qloo's supported tags for an interest phrase."""

    query = query.strip()

    if not query:
        raise ValueError("Tag search query cannot be blank.")

    if not 1 <= take <= 50:
        raise ValueError("take must be between 1 and 50.")

    return _get_json(
        "/v2/tags",
        {
            "filter.query": query,
            "feature.semantic_search": "true",
            "take": take,
            "page": 1,
        },
    )
