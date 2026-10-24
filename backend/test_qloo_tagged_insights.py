
from qloo_client import (
    QlooAPIError,
    QlooConfigurationError,
    get_qloo_insights,
    search_qloo_tags,
)


def main():
    # Resolve an interest to a Qloo tag ID.
    tag_data = search_qloo_tags("hiking", take=10)
    tags = tag_data.get("results", {}).get("tags", [])

    # Prefer a hiking activity or hobby tag over unrelated tag types.
    preferred_prefixes = (
        "urn:tag:activity:",
        "urn:tag:hobby:",
        "urn:tag:activities:place:",
    )

    selected_tag = next(
        (
            tag for tag in tags
            if isinstance(tag.get("id"), str)
            and tag["id"].startswith(preferred_prefixes)
        ),
        None,
    )

    if not selected_tag:
        print("No suitable hiking tag was returned.")
        raise SystemExit(1)

    tag_id = selected_tag["id"]
    print("Selected tag:", selected_tag.get("name"))
    print("Selected tag type:", selected_tag.get("type"))
    print("Requesting insights for Bengaluru...")

    try:
        data = get_qloo_insights(
            location="Bengaluru",
            take=10,
            tag_ids=[tag_id],
        )
    except (QlooAPIError, QlooConfigurationError) as exc:
        print("Tagged Insights request failed:", str(exc))
        raise SystemExit(1)

    entities = data.get("results", {}).get("entities", [])
    print("Tagged Insights request succeeded.")
    print("Entities returned:", len(entities))

    for entity in entities[:10]:
        print(
            "-",
            entity.get("name", "Unnamed entity"),
            "| entity ID available:",
            bool(entity.get("entity_id")),
        )

    print("Tag-based Insights test complete.")


if __name__ == "__main__":
    main()
