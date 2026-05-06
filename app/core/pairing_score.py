"""Sake ↔ recipe pairing scores.

Three modes mirror Japanese pairing tradition:
    - synergy_score (寄り添う): same-axis matching
    - cleanse_score (口直し):  acidic sake cuts fatty/salty food
    - contrast_score (意外な出会い): intentional mismatch on one axis

Lower score = better pairing. Each function returns a single float;
callers sort ascending and take top-K per mode.

Recipe carries 6 axes (sweetness, umami, acidity, fat, aroma, saltiness).
Sake carries 5 axes (sweetness, umami, acidity, bitterness, aroma) plus
serving_temperature/season metadata.
"""

from app.models.sake import Recipe, Sake


def _recipe_weight(r: Recipe) -> float:
    """Boldness in the mouth — what the sake has to stand up to."""
    return 0.4 * r.umami + 0.4 * r.fat + 0.2 * r.saltiness


def _sake_weight(s: Sake) -> float:
    """Bitterness adds heft, acidity makes a sake feel lighter."""
    return 0.4 * s.umami + 0.3 * s.bitterness + 0.3 * (1.0 - s.acidity)


def _temp_axis(s: Sake) -> float:
    """+1 for chilled, 0 for room temp, -1 for warmed."""
    temp = s.serving_temperature or ""
    if "冷" in temp:
        return 1.0
    if "燗" in temp:
        return -1.0
    return 0.0


def _recipe_temp_pref(r: Recipe) -> float:
    """+1 prefers chilled sake (light, acidic), -1 prefers warmed (rich)."""
    cold = 0.5 * (1.0 - r.fat) + 0.5 * r.acidity
    warm = 0.5 * r.umami + 0.5 * r.fat
    return cold - warm


def synergy_score(sake: Sake, recipe: Recipe) -> float:
    """同調 — closer matches. Lower is better.

    Volume/body matching is the *primary* axis (multiple Japanese sources call
    it the most important factor). Other axes are secondary and weighted
    accordingly. Soft sakes (爽酒, low umami AND low aroma) are scored as
    "supporting actors" — they don't need to mirror the recipe's umami; they
    just shouldn't be drowned out.
    """
    is_soft_sake = sake.umami < 0.55 and sake.aroma < 0.55  # 爽酒-style

    # Volume asymmetry: heavy recipe with light sake = sake crushed (full penalty),
    # heavy sake with light recipe = sake "lifts" the dish (mild penalty).
    volume_diff = _recipe_weight(recipe) - _sake_weight(sake)
    p_volume = (volume_diff if volume_diff > 0 else 0.4 * volume_diff) ** 2

    if is_soft_sake:
        # Supporting-actor sake: only penalty is being overwhelmed
        deficit_umami = max(0.0, recipe.umami - sake.umami - 0.2) ** 2
        excess_umami = 0.0
    else:
        deficit_umami = max(0.0, recipe.umami - sake.umami) ** 2
        excess_umami = max(0.0, sake.umami - recipe.umami) ** 2

    p_sweet_asym = max(0.0, recipe.sweetness - sake.sweetness) ** 2
    p_acid_asym = max(0.0, recipe.acidity - sake.acidity) ** 2
    p_aroma_asym = max(0.0, recipe.aroma - sake.aroma) ** 2
    p_salt_umami = max(0.0, recipe.saltiness - sake.umami) ** 2

    # Bonus: 相乗 — both sides umami-strong (米の旨味 × 食材の旨味)
    b_umami_resonance = (
        (sake.umami - 0.5) * (recipe.umami - 0.5)
        if (sake.umami > 0.6 and recipe.umami > 0.6)
        else 0.0
    )
    # Bonus: 香り resonance — both sides aroma-strong (薫酒 + 香り高い food)
    b_aroma_resonance = (
        (sake.aroma - 0.5) * (recipe.aroma - 0.5)
        if (sake.aroma > 0.65 and recipe.aroma > 0.55)
        else 0.0
    )
    # Bonus: 酸 resonance — both sides acid-bright
    b_acid_resonance = (
        (sake.acidity - 0.5) * (recipe.acidity - 0.5)
        if (sake.acidity > 0.6 and recipe.acidity > 0.5)
        else 0.0
    )

    return (
        1.4 * p_volume
        + 1.2 * deficit_umami
        + 0.3 * excess_umami
        + 0.5 * p_sweet_asym
        + 0.5 * p_acid_asym
        + 0.4 * p_aroma_asym
        + 1.0 * p_salt_umami
        - 0.5 * b_umami_resonance
        - 0.3 * b_aroma_resonance
        - 0.7 * b_acid_resonance
    )


def cleanse_score(sake: Sake, recipe: Recipe) -> float:
    """洗浄 — acidic sake refreshes the palate against dense food.

    Density = fat OR saltiness (whichever stronger). Without density there's
    nothing to clean → low-intensity dishes score poorly here. Lower is better.
    """
    intensity = max(recipe.fat, recipe.saltiness)
    cut = sake.acidity * intensity
    weight_diff = (_sake_weight(sake) - _recipe_weight(recipe)) ** 2
    aroma_clash = (recipe.saltiness * sake.aroma) if sake.aroma > 0.7 else 0.0
    intensity_floor = max(0.0, 0.4 - intensity) ** 2  # both fat and salt low → no cleanse

    return (
        -2.0 * cut
        + 0.8 * weight_diff
        + 0.5 * aroma_clash
        + 1.5 * intensity_floor
    )


def contrast_score(sake: Sake, recipe: Recipe) -> float:
    """対比 — sweet sake bridges salty/spicy food, or character meets character.

    The two classic 対比 patterns:
      1. Sweet sake + salty/grilled/fatty food (sweet bridges salt or fat)
      2. High-character sake (high aroma OR acidity) + bold individual food
    Lower is better.
    """
    # Pattern 1: sweet sake bridges
    salt_sweet_bridge = recipe.saltiness * sake.sweetness
    fat_sweet_bridge = recipe.fat * sake.sweetness * 0.7
    sweet_active = max(salt_sweet_bridge, fat_sweet_bridge)

    # Pattern 2: character meets character — high-aroma sake + aromatic food,
    # or high-acid sake + tangy food
    aroma_x_aroma = (
        sake.aroma * recipe.aroma if (sake.aroma > 0.7 and recipe.aroma > 0.6) else 0.0
    )
    acid_x_acid = (
        sake.acidity * recipe.acidity if (sake.acidity > 0.7 and recipe.acidity > 0.5) else 0.0
    )
    character_active = max(aroma_x_aroma, acid_x_acid)

    standout = max(sweet_active, character_active)

    weight_diff = abs(_sake_weight(sake) - _recipe_weight(recipe))

    # Penalty when neither pattern fires — contrast isn't applicable
    no_pattern_penalty = max(0.0, 0.3 - standout) ** 2

    return (
        -1.2 * sweet_active
        - 1.0 * character_active
        + 0.5 * weight_diff
        + 2.0 * no_pattern_penalty
    )


SCORERS = {
    "synergy": synergy_score,
    "cleanse": cleanse_score,
    "contrast": contrast_score,
}


def rank_recipes(
    sake: Sake, recipes: list[Recipe], mode: str, top_k: int = 3
) -> list[tuple[Recipe, float]]:
    """Return [(recipe, score), ...] sorted ascending (best first)."""
    scorer = SCORERS[mode]
    scored = [(r, scorer(sake, r)) for r in recipes]
    scored.sort(key=lambda x: x[1])
    return scored[:top_k]


def rank_sakes(
    recipe: Recipe, sakes: list[Sake], mode: str, top_k: int = 3
) -> list[tuple[Sake, float]]:
    """Return [(sake, score), ...] sorted ascending (best first)."""
    scorer = SCORERS[mode]
    scored = [(s, scorer(s, recipe)) for s in sakes]
    scored.sort(key=lambda x: x[1])
    return scored[:top_k]
