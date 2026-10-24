
from qloo_client import (
    QlooAPIError,
    QlooConfigurationError,
    search_qloo_tags,
)


def main():
    for interest in ["food", "music", "art", "hiking"]:
        print(f"\n--- {interest.upper()} ---")

        try:
            data = search_qloo_tags(interest, take=5)
        except (QlooAPIError, QlooConfigurationError) as exc:
            print("Tag search failed:", str(exc))
            raise SystemExit(1)

        results = data.get("results", {})
        tags = results.get("tags", [])

        for tag in tags:
            print({
                "name": tag.get("name"),
                "id": tag.get("id"),
                "type": tag.get("type"),
                "tag_type": tag.get("tag_type"),
            })

    print("\nTag metadata inspection complete.")


if __name__ == "__main__":
    main()
