"""Print each sake's top-5 per mode for inspection."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from scripts.validate_pairing_rules import (
    _load_manual_pairings,
    _load_recipes,
    _load_sakes,
)
from app.core.pairing_score import SCORERS, rank_recipes


def main() -> None:
    sakes = _load_sakes()
    recipes = list(_load_recipes().values())
    pairs = _load_manual_pairings()
    manual_by_sake: dict[str, set[str]] = {}
    for s, r in pairs:
        manual_by_sake.setdefault(s, set()).add(r)

    for sake_id, sake in sakes.items():
        manual = manual_by_sake.get(sake_id, set())
        print(f"\n=== {sake.name} ({sake_id}) ===")
        print(f"  manual: {[r.name for r in recipes if r.id in manual]}")
        for mode in SCORERS:
            top = rank_recipes(sake, recipes, mode, top_k=5)
            print(f"  [{mode}]")
            for i, (r, score) in enumerate(top, 1):
                marker = " ★" if r.id in manual else ""
                print(f"    {i}. {r.name:<20} {score:+.3f}{marker}")


if __name__ == "__main__":
    main()
