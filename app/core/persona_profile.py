"""Persona ↔ sake-axis matching.

Persona codes are 4 binary chars:
    1: S (sweet 甘口)  | D (dry 辛口)
    2: H (heavy 重厚)  | E (easy 軽快)
    3: R (rich 香り強) | L (light 香り控)
    4: B (bold 余韻強) | S (smooth 余韻滑)

Each code maps deterministically to an ideal 5-axis taste vector
(甘味 / 旨味 / 酸味 / 苦味 / 香り). Match score = weighted Euclidean
distance between persona ideal and sake's measured vector — lower = closer.
"""

from app.models.sake import Sake


AXIS_WEIGHTS = {
    "sweetness": 1.0,
    "umami": 1.0,
    "acidity": 1.0,
    "bitterness": 0.8,
    "aroma": 1.5,  # first impression — weighted up
}


def is_valid_code(code: str) -> bool:
    if not code or len(code) != 4:
        return False
    c = code.upper()
    return (
        c[0] in ("S", "D")
        and c[1] in ("H", "E")
        and c[2] in ("R", "L")
        and c[3] in ("B", "S")
    )


def ideal_vector(code: str) -> dict[str, float]:
    c = code.upper()
    if not is_valid_code(c):
        raise ValueError(f"invalid persona code: {code!r}")
    bitter = 0.30
    if c[1] == "H":
        bitter += 0.15
    if c[3] == "B":
        bitter += 0.15
    return {
        "sweetness": 0.75 if c[0] == "S" else 0.25,
        "umami": 0.75 if c[1] == "H" else 0.35,
        "acidity": 0.70 if c[3] == "B" else 0.30,
        "bitterness": bitter,
        "aroma": 0.85 if c[2] == "R" else 0.30,
    }


def journal_profile(sake: Sake) -> dict[str, int]:
    """Map a sake's measured taste axes to the journal's 4-axis profile
    (each 0-100, where the lower end is the left-hand label of the slider:
    甘口 / 重厚 / 華やか / 力強い). Used to pre-fill a new journal entry when
    the user records a catalog sake.
    """

    def axis(value: float) -> int:
        return round((1.0 - value) * 100)

    return {
        "sweetDry": axis(sake.sweetness),   # 甘口 ↔ 辛口
        "heavyLight": axis(sake.umami),     # 重厚 ↔ 軽快
        "richCalm": axis(sake.aroma),       # 華やか ↔ 穏やか
        "boldSmooth": axis(sake.acidity),   # 力強い ↔ 滑らか
    }


def distance(sake: Sake, code: str) -> float:
    ideal = ideal_vector(code)
    sq = 0.0
    for axis, w in AXIS_WEIGHTS.items():
        d = ideal[axis] - getattr(sake, axis)
        sq += w * d * d
    return sq ** 0.5
