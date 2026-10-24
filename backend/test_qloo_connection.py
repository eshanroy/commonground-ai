
from qloo_client import (
    QlooAPIError,
    QlooConfigurationError,
    get_qloo_insights,
)


def main():
    location = input("Enter a city or locality [Bengaluru]: ").strip()
    if not location:
        location = "Bengaluru"

    try:
        data = get_qloo_insights(location=location, take=10)

        results = data.get("results", {})
        entities = results.get("entities", [])

        print("\nQloo request succeeded.")
        print("Requested location:", location)
        print("Entities returned:", len(entities))

        for index, entity in enumerate(entities, start=1):
            properties = entity.get("properties", {})
            address = properties.get("address", {})

            print(f"\n{index}. {entity.get('name', 'Unnamed entity')}")
            print("   Entity ID available:", bool(entity.get("entity_id")))
            print("   Subtype:", entity.get("subtype", "Not provided"))

            if isinstance(address, dict):
                print(
                    "   Address:",
                    address.get("label")
                    or address.get("display_address")
                    or "Not provided",
                )
            elif isinstance(address, str):
                print("   Address:", address)

            print("   Popularity:", entity.get("popularity", "Not provided"))

        print("\nInspection complete. No API key was displayed.")

    except (QlooAPIError, QlooConfigurationError) as exc:
        print("Qloo request failed:", str(exc))
        raise SystemExit(1)


if __name__ == "__main__":
    main()
