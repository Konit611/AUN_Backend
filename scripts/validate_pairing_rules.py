"""Validate pairing scoring rules against the manually curated pairings.

For every (sake, sakana) entry in sake_sakana.csv, check whether the sakana
appears in the top-K of synergy / cleanse / contrast for that sake. A match
in ANY mode counts as a hit — the three modes are alternatives, not parallel
rankings, and the founder's intent for any given pairing might be any of them.

Usage:
    python scripts/validate_pairing_rules.py [--top-k N]
"""

import argparse
import csv
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.core.pairing_score import SCORERS, rank_sakana
from app.models.sake import Sake, Sakana


DATA_DIR = Path(__file__).resolve().parent.parent / "data"


def _load_sakes() -> dict[str, Sake]:
    out: dict[str, Sake] = {}
    with (DATA_DIR / "sake.csv").open(newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            out[row["id"]] = Sake(
                id=row["id"],
                name=row["name"],
                brewery=row["brewery"],
                region=row["region"],
                description=row["description"],
                type=row["type"],
                rice=row["rice"],
                polishing=row["polishing"],
                serving_temperature=row["serving_temperature"],
                serving_season=row["serving_season"],
                sweetness=float(row["sweetness"]),
                umami=float(row["umami"]),
                acidity=float(row["acidity"]),
                bitterness=float(row["bitterness"]),
                aroma=float(row["aroma"]),
            )
    return out


def _load_sakana() -> dict[str, Sakana]:
    out: dict[str, Sakana] = {}
    with (DATA_DIR / "sakana.csv").open(newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            out[row["id"]] = Sakana(
                id=row["id"],
                name=row["name"],
                emoji=row["emoji"],
                image_placeholder=row.get("image_placeholder") or None,
                sweetness=float(row["sweetness"]),
                umami=float(row["umami"]),
                acidity=float(row["acidity"]),
                fat=float(row["fat"]),
                aroma=float(row["aroma"]),
                saltiness=float(row["saltiness"]),
            )
    return out


def _load_manual_pairings() -> list[tuple[str, str]]:
    pairs: list[tuple[str, str]] = []
    with (DATA_DIR / "sake_sakana.csv").open(newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            pairs.append((row["sake_id"], row["sakana_id"]))
    return pairs


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--top-k", type=int, default=3)
    args = ap.parse_args()

    sakes = _load_sakes()
    sakana_d = _load_sakana()
    pairs = _load_manual_pairings()
    sakana_list = list(sakana_d.values())

    # Pre-compute top-K per (sake, mode)
    rankings: dict[tuple[str, str], list[str]] = {}
    for sake_id, sake in sakes.items():
        for mode in SCORERS:
            top = rank_sakana(sake, sakana_list, mode, top_k=args.top_k)
            rankings[(sake_id, mode)] = [s.id for s, _ in top]

    # Per-pair attribution + global stats
    mode_hits = {m: 0 for m in SCORERS}
    any_hits = 0
    misses: list[tuple[str, str]] = []

    print(f"Manual pairings: {len(pairs)}  |  top-K = {args.top_k}\n")
    print(f"{'sake':<22}{'sakana':<22}{'modes hit':<22}{'rank in best mode'}")
    print("-" * 90)

    for sake_id, sakana_id in pairs:
        sake = sakes[sake_id]
        sakana = sakana_d[sakana_id]
        hits = []
        best_rank: tuple[int, str] | None = None
        for mode in SCORERS:
            top_ids = rankings[(sake_id, mode)]
            if sakana_id in top_ids:
                hits.append(mode)
                mode_hits[mode] += 1
                rank = top_ids.index(sakana_id) + 1
                if best_rank is None or rank < best_rank[0]:
                    best_rank = (rank, mode)
        if hits:
            any_hits += 1
            best_str = f"#{best_rank[0]} ({best_rank[1]})" if best_rank else ""
        else:
            misses.append((sake_id, sakana_id))
            best_str = "miss"
        print(
            f"{sake.name[:20]:<22}"
            f"{sakana.name[:20]:<22}"
            f"{','.join(hits) or '-':<22}"
            f"{best_str}"
        )

    total = len(pairs)
    union_hits = 0
    for sake_id, sakana_id in pairs:
        union = set()
        for mode in SCORERS:
            union.update(rankings[(sake_id, mode)])
        if sakana_id in union:
            union_hits += 1

    print("\n" + "=" * 90)
    print(f"ANY-mode hit rate (≥1 mode):  {any_hits}/{total} = {any_hits/total:.0%}")
    print(f"Union top-{args.top_k} (union across modes): {union_hits}/{total} = {union_hits/total:.0%}")
    for mode, count in mode_hits.items():
        print(f"  {mode:<10} hits: {count}/{total} = {count/total:.0%}")

    if misses:
        print(f"\nMisses ({len(misses)}):")
        for sid, rid in misses:
            print(f"  {sakes[sid].name}  ×  {sakana_d[rid].name}")


if __name__ == "__main__":
    main()
