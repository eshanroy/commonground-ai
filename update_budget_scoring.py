
from pathlib import Path
import re
import shutil

path = Path("backend/recommendations.py")
source = path.read_text(encoding="utf-8")
backup = path.with_suffix(".py.budget-backup")

catalog_tiers = {
    "A food crawl with something for everyone": "low",
    "An arts and culture afternoon": "low",
    "A live music discovery night": "premium",
    "An outdoor adventure together": "low",
    "A creative workshop for the group": "moderate",
    "A relaxed games and café meetup": "low",
    "A premium tasting experience": "premium",
    "A film and discussion night": "moderate",
    "A discovery day exploring the city": "low",
}

updated = source

for title, tier in catalog_tiers.items():
    pattern = (
        r'("title": "' + re.escape(title)
        + r'",.*?)(        "budgets": \{[^}]*\},)'
    )

    def add_tier(match, tier=tier):
        return (
            match.group(1)
            + f'        "budget_tier": "{tier}",\n'
            + match.group(2)
        )

    # Do not insert the field twice if rerun after a partial update.
    if f'"title": "{title}"' not in updated:
        raise RuntimeError(f"Catalog entry not found: {title}")

    updated, count = re.subn(
        pattern, add_tier, updated, count=1, flags=re.S
    )

    if count == 0:
        # Accept an already-added budget_tier field.
        entry_start = updated.index(f'"title": "{title}"')
        entry_end = updated.find('"title": "', entry_start + 1)
        if entry_end == -1:
            entry_end = len(updated)
        entry = updated[entry_start:entry_end]
        if '"budget_tier":' not in entry:
            raise RuntimeError(
                f"Could not safely update catalog entry: {title}"
            )

old_budget = '''    # Component 4: budget alignment (0-10).
    budget_score = (
        10 if request.budget in candidate["budgets"] else 0
    )'''

new_budget = '''    # Component 4: estimated budget alignment (0-10).
    # These tiers are illustrative activity estimates, not venue prices.
    budget_order = {"low": 0, "moderate": 1, "premium": 2}
    selected_tier = budget_order[request.budget]
    estimated_tier = budget_order[candidate["budget_tier"]]
    tier_distance = abs(selected_tier - estimated_tier)
    budget_score = {0: 10, 1: 6, 2: 2}[tier_distance]'''

if old_budget in updated:
    updated = updated.replace(old_budget, new_budget, 1)
elif new_budget not in updated:
    raise RuntimeError("Could not find the expected budget-scoring block.")

old_explanation = '''    explanation_parts.append(
        f"Budget alignment: {budget_score}/10."
    )'''

new_explanation = '''    explanation_parts.append(
        f"Budget alignment: {budget_score}/10 "
        f"(estimated activity tier: {candidate['budget_tier']}; "
        f"selected tier: {request.budget})."
    )'''

if old_explanation in updated:
    updated = updated.replace(old_explanation, new_explanation, 1)
elif new_explanation not in updated:
    raise RuntimeError("Could not find the expected budget explanation.")

old_tradeoff = '''    if request.budget not in candidate["budgets"]:
        tradeoffs.append(
            "This concept may not align with the selected budget."
        )'''

new_tradeoff = '''    if budget_score < 10:
        tradeoffs.append(
            f"Estimated activity tier is {candidate['budget_tier']}, "
            f"while the group selected {request.budget}."
        )'''

if old_tradeoff in updated:
    updated = updated.replace(old_tradeoff, new_tradeoff, 1)
elif new_tradeoff not in updated:
    raise RuntimeError("Could not find the expected budget trade-off block.")

# Validate before writing anything.
compile(updated, str(path), "exec")

if updated != source:
    shutil.copy2(path, backup)
    path.write_text(updated, encoding="utf-8")
    print("Budget scoring updated successfully.")
    print(f"Backup saved to: {backup}")
else:
    print("No changes were necessary; the update may already be applied.")
