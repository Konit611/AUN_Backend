"""Print each sake's top-5 per mode for inspection."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from scripts.validate_pairing_rules import (
    _load_manual_pairings,
    _load_sakana,
    _load_sakes,
)
from app.core.pairing_score import SCORERS, rank_sakana


def main() -> None:
    sakes = _load_sakes()
    sakana_list = list(_load_sakana().values())
    pairs = _load_manual_pairings()
    manual_by_sake: dict[str, set[str]] = {}
    for s, r in pairs:
        manual_by_sake.setdefault(s, set()).add(r)

    for sake_id, sake in sakes.items():
        manual = manual_by_sake.get(sake_id, set())
        print(f"\n=== {sake.name} ({sake_id}) ===")
        print(f"  manual: {[s.name for s in sakana_list if s.id in manual]}")
        for mode in SCORERS:
            top = rank_sakana(sake, sakana_list, mode, top_k=5)
            print(f"  [{mode}]")
            for i, (s, score) in enumerate(top, 1):
                marker = " ★" if s.id in manual else ""
                print(f"    {i}. {s.name:<20} {score:+.3f}{marker}")


if __name__ == "__main__":
    main()
