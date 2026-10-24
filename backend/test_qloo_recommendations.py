
from qloo_client import get_qloo_insights, search_qloo_tags


def main():
    tag_data = search_qloo_tags("hiking", take=5)
    tags = tag_data.get("results", {}).get("tags", [])

    tag = next(
        (
            item
            for item in tags
            if isinstance(item, dict)
            and isinstance(item.get("id"), str)
            and item["id"].strip()
        ),
        None,
    )

    if not tag:
        print("No usable hiking tag found.")
        return

    data = get_qloo_insights(
        location="Bengaluru",
        take=5,
        tag_ids=[tag["id"]],
    )

    entities = data.get("results", {}).get("entities", [])

    for entity in entities[:3]:
        properties = entity.get("properties", {})
        if not isinstance(properties, dict):
            properties = {}

        print("\n" + "=" * 50)
        print("Name:", entity.get("name"))
        print("Subtype:", entity.get("subtype"))
        print("Popularity:", entity.get("popularity"))
        print("Tags:", entity.get("tags"))
        print("Description:", properties.get("description"))
        print("Short description:", properties.get("short_description"))
        print("Keywords:", properties.get("keywords"))
        print("Good for:", properties.get("good_for"))
        print("Price level:", properties.get("price_level"))
        print("Business rating:", properties.get("business_rating"))
        print("Closed:", properties.get("is_closed"))
        print("Website:", properties.get("website"))


if __name__ == "__main__":
    main()
