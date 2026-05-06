"""For each manual pairing, show its rank in every mode and the dominant
score components so we can see which rules are blocking the match.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from scripts.validate_pairing_rules import (
    _load_manual_pairings,
    _load_recipes,
    _load_sakes,
)
from app.core.pairing_score import (
    SCORERS,
    _recipe_weight,
    _sake_weight,
    rank_recipes,
)


# Mode classification per pairing based on description in sake_recipe.csv.
# S = synergy (同調), C = contrast (対比), W = cleanse (洗浄/wash).
INTENDED_MODE = {
    ("dassai-45", "92053519-ba49-4d32-b8e9-f385462d5d48"): "S",  # 焼き鳥タレ
    ("dassai-45", "978db53c-5606-4797-ad95-5735c385874d"): "S",  # 旬の刺身
    ("dassai-45", "b8325ac7-b157-4443-a2ba-067454491824"): "S",  # カマンベール
    ("kubota-manju", "92053519-ba49-4d32-b8e9-f385462d5d48"): "C",  # 焼き鳥タレ
    ("kubota-manju", "4cb50bcc-b685-4724-a911-1ae1a79fdff7"): "S",  # 昆布締め
    ("kubota-manju", "67153d6f-2318-4ecd-9761-4522ec2193d2"): "C",  # 湯豆腐
    ("juyondai-honmaru", "b3ec295b-2733-41fd-8a12-d50b02f9cfbc"): "C",  # まぐろ
    ("juyondai-honmaru", "d9009430-e088-40e5-b333-a1c7033e8971"): "C",  # 生ハム
    ("juyondai-honmaru", "16048727-4591-4a66-84fc-c2c0a3f1525f"): "S",  # 苺白和え
    ("hakkaisan-tokubetsu", "7506ddbd-ec4d-4e1b-9981-f8e7beba8beb"): "W",  # 塩焼き
    ("hakkaisan-tokubetsu", "9bcfab49-68e1-4e21-8664-ca28efee0720"): "S",  # おでん
    ("hakkaisan-tokubetsu", "0c20dfdb-632e-4dae-954d-b7754a192110"): "S",  # 浅漬け
    ("denshu-tokubetsu", "0f523b74-e063-4ff1-82d8-3c78ec2ba04b"): "S",  # もつ鍋
    ("denshu-tokubetsu", "7d57f7a7-f910-4e77-966b-ccbf61f82fbb"): "S",  # ぶり
    ("denshu-tokubetsu", "493dc608-ab04-45b4-b291-d7bb51fa2a92"): "S",  # 焼きおにぎり
    ("nabeshima-newmoon", "cd19979d-2b46-4c16-b108-74dae3aff68e"): "S",  # 生春巻き
    ("nabeshima-newmoon", "77ba9dc2-b34c-45ed-941c-114721ee97bc"): "S",  # カプレーゼ
    ("nabeshima-newmoon", "ced792f9-b97d-43a0-b1b8-68254a257e12"): "S",  # フルーツタルト
    ("aramasa-no6", "c4d205d6-0059-4784-aae1-1ede484c9122"): "S",  # 牡蠣ポン酢
    ("aramasa-no6", "d1b31b09-b584-41b8-9e7e-e1df81222080"): "S",  # シェーヴル
    ("aramasa-no6", "a194a281-3afc-43dc-a45a-1ba1acaaeca9"): "W",  # カルパッチョ
    ("kokuryu-daiginjo", "1017a7f6-7fde-42b5-9db6-e7d07f0f002d"): "S",  # 白身薄造り
    ("kokuryu-daiginjo", "8186d3c1-cafb-4d46-bd4a-eb4df9e5524e"): "S",  # 茶碗蒸し
    ("kokuryu-daiginjo", "698cb0f1-ae89-4213-a472-338f91563bf1"): "C",  # みたらし
    ("kuheiji-kibou", "16e4f2bc-1147-432b-95fd-8bb2f481fa13"): "S",  # 鶏塩焼き
    ("kuheiji-kibou", "91e41c71-cb32-4b87-b4c3-cc6a600534fb"): "S",  # コンテ
    ("kuheiji-kibou", "699090fd-f5a4-45f3-bdcd-99da0bebe906"): "S",  # 鯛昆布
}

MODE_NAME = {"S": "synergy", "C": "contrast", "W": "cleanse"}


def _explain_synergy(sake, recipe):
    """Return list of (label, weight, value, contribution) for each term."""
    p_umami = (sake.umami - recipe.umami) ** 2
    p_sweet_sym = (sake.sweetness - recipe.sweetness) ** 2
    p_sweet_asym = max(0.0, recipe.sweetness - sake.sweetness) ** 2
    p_acid_asym = max(0.0, recipe.acidity - sake.acidity) ** 2
    p_aroma_asym = max(0.0, recipe.aroma - sake.aroma) ** 2
    p_salt_aroma = (recipe.saltiness * sake.aroma) ** 2 if sake.aroma > 0.7 else 0.0
    p_salt_umami = max(0.0, recipe.saltiness - sake.umami) ** 2
    p_weight_asym = max(0.0, _recipe_weight(recipe) - _sake_weight(sake)) ** 2
    b_fat_sweet = (
        recipe.fat * sake.sweetness
        if (recipe.fat > 0.5 and sake.sweetness > 0.5)
        else 0.0
    )
    return [
        ("umami_diff", 1.5, p_umami, 1.5 * p_umami),
        ("sweet_sym", 0.7, p_sweet_sym, 0.7 * p_sweet_sym),
        ("sweet_asym", 0.5, p_sweet_asym, 0.5 * p_sweet_asym),
        ("acid_asym", 0.8, p_acid_asym, 0.8 * p_acid_asym),
        ("aroma_asym", 0.6, p_aroma_asym, 0.6 * p_aroma_asym),
        ("salt_aroma", 0.5, p_salt_aroma, 0.5 * p_salt_aroma),
        ("salt_umami", 1.4, p_salt_umami, 1.4 * p_salt_umami),
        ("weight_asym", 1.0, p_weight_asym, 1.0 * p_weight_asym),
        ("-fat_sweet", -0.6, b_fat_sweet, -0.6 * b_fat_sweet),
    ]


def main() -> None:
    sakes = _load_sakes()
    recipes_d = _load_recipes()
    recipes = list(recipes_d.values())
    pairs = _load_manual_pairings()

    rank_cache: dict[tuple[str, str], list[str]] = {}
    for sake_id, sake in sakes.items():
        for mode in SCORERS:
            top = rank_recipes(sake, recipes, mode, top_k=26)
            rank_cache[(sake_id, mode)] = [r.id for r, _ in top]

    print(f"{'pairing':<48}{'intended':<10}{'rank_S':<8}{'rank_W':<8}{'rank_C':<8}")
    print("-" * 90)
    for sake_id, recipe_id in pairs:
        sake = sakes[sake_id]
        recipe = recipes_d[recipe_id]
        intended = INTENDED_MODE.get((sake_id, recipe_id), "?")
        ranks = {}
        for mode in SCORERS:
            ids = rank_cache[(sake_id, mode)]
            ranks[mode] = ids.index(recipe_id) + 1 if recipe_id in ids else "-"
        label = f"{sake.name[:18]} × {recipe.name[:18]}"
        print(
            f"{label:<48}{MODE_NAME[intended]:<10}"
            f"{str(ranks['synergy']):<8}{str(ranks['cleanse']):<8}{str(ranks['contrast']):<8}"
        )

    print("\n--- Synergy term breakdown for misses (intended = S, rank_S > 3) ---\n")
    for sake_id, recipe_id in pairs:
        if INTENDED_MODE.get((sake_id, recipe_id)) != "S":
            continue
        sake = sakes[sake_id]
        recipe = recipes_d[recipe_id]
        ids = rank_cache[(sake_id, "synergy")]
        rank = ids.index(recipe_id) + 1
        if rank <= 3:
            continue
        print(f"{sake.name} × {recipe.name}  (rank #{rank})")
        terms = _explain_synergy(sake, recipe)
        terms.sort(key=lambda t: -abs(t[3]))
        for label, w, val, contrib in terms[:5]:
            print(f"  {label:<14} weight={w:+.2f} value={val:.3f} → {contrib:+.3f}")
        total = sum(t[3] for t in terms)
        print(f"  TOTAL synergy = {total:+.3f}\n")


if __name__ == "__main__":
    main()
