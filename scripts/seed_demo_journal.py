"""Seed the existing 6 hardcoded journal entries under the demo user.

Run inside the backend container:
    uv run python scripts/seed_demo_journal.py

Idempotent: skips entries already present for the demo user.
"""

from sqlmodel import Session, select

from app.core.database import engine
from app.models.journal import JournalEntry
from app.models.user import User

DEMO_EMAIL = "demo@aun.jp"

ENTRIES = [
    {
        "id": "1",
        "sake_name": "獺祭 純米大吟醸45",
        "brewery": "旭酒造",
        "category": "純米大吟醸",
        "date": "2026-03-28",
        "rating": 5,
        "tasting": {
            "profile": {"sweetDry": 20, "heavyLight": 70, "richCalm": 15, "boldSmooth": 65},
            "aroma": "メロン、白桃、ほのかな花の香り",
            "taste": "滑らかで透明感のある甘み、軽い酸味",
            "finish": "すっきりと長い余韻",
            "temperature": "冷酒 10°C",
            "pairing": "白身魚の刺身",
            "memo": "開栓してすぐが一番華やか。",
        },
        "image_path": "/images/journal/sake-1.jpg",
    },
    {
        "id": "2",
        "sake_name": "久保田 萬寿",
        "brewery": "朝日酒造",
        "category": "純米大吟醸",
        "date": "2026-03-25",
        "rating": 4,
        "tasting": {
            "profile": {"sweetDry": 55, "heavyLight": 30, "richCalm": 40, "boldSmooth": 45},
            "aroma": "青りんご、洋梨、穏やかな吟醸香",
            "taste": "まろやかなコク、ふくよかな旨味",
            "finish": "キレが良くすっきり",
            "temperature": "冷酒 12°C",
            "pairing": "昆布締め",
        },
        "image_path": "/images/journal/sake-2.jpg",
    },
    {
        "id": "3",
        "sake_name": "新政 No.6 S-type",
        "brewery": "新政酒造",
        "category": "純米",
        "date": "2026-03-20",
        "rating": 5,
        "tasting": {
            "profile": {"sweetDry": 35, "heavyLight": 80, "richCalm": 25, "boldSmooth": 75},
            "aroma": "白ぶどう、ヨーグルトのような乳酸香",
            "taste": "シャープな酸味、軽やかな甘み",
            "finish": "ドライで切れ味鋭い",
            "temperature": "冷酒 8°C",
            "pairing": "牡蠣のポン酢",
            "memo": "ワイン好きにも薦めたい一本。",
        },
        "image_path": "/images/journal/sake-3.jpg",
    },
    {
        "id": "4",
        "sake_name": "醸し人九平次 希望の月",
        "brewery": "萬乗醸造",
        "category": "純米大吟醸",
        "date": "2026-03-15",
        "rating": 4,
        "tasting": {
            "profile": {"sweetDry": 60, "heavyLight": 35, "richCalm": 20, "boldSmooth": 40},
            "aroma": "柑橘、ハーブ、ミネラル感",
            "taste": "立体的な旨味、奥行きのある酸",
            "finish": "エレガントで長い",
            "temperature": "常温 15°C",
            "pairing": "鶏の塩焼き",
        },
        "image_path": "/images/journal/sake-4.jpg",
    },
    {
        "id": "5",
        "sake_name": "黒龍 大吟醸",
        "brewery": "黒龍酒造",
        "category": "大吟醸",
        "date": "2026-01-20",
        "rating": 3,
        "tasting": {
            "profile": {"sweetDry": 45, "heavyLight": 55, "richCalm": 60, "boldSmooth": 80},
            "aroma": "バナナ、バニラ、控えめな花の香り",
            "taste": "なめらかで柔らかい口当たり",
            "finish": "穏やかに消えていく",
            "temperature": "冷酒 10°C",
        },
        "image_path": "/images/journal/sake-5.jpg",
    },
    {
        "id": "6",
        "sake_name": "鍋島 New Moon",
        "brewery": "富久千代酒造",
        "category": "純米吟醸",
        "date": "2026-01-05",
        "rating": 5,
        "tasting": {
            "profile": {"sweetDry": 25, "heavyLight": 85, "richCalm": 10, "boldSmooth": 70},
            "aroma": "ライチ、マスカット、微かな発泡感",
            "taste": "ジューシーな甘酸っぱさ、弾ける果実味",
            "finish": "爽やかでフレッシュ",
            "temperature": "冷酒 5°C",
            "pairing": "生春巻き",
            "memo": "開けたてのガス感が最高。",
        },
        "image_path": "/images/journal/sake-6.jpg",
    },
]


def main() -> None:
    with Session(engine) as session:
        user = session.exec(select(User).where(User.email == DEMO_EMAIL)).first()
        if not user:
            raise SystemExit(
                f"Demo user {DEMO_EMAIL} not found. Sign up first via /api/v1/auth/signup."
            )

        inserted = 0
        for data in ENTRIES:
            if session.get(JournalEntry, data["id"]):
                continue
            session.add(JournalEntry(user_id=user.id, **data))
            inserted += 1
        session.commit()
        print(f"Seeded {inserted} journal entries for user {user.email} (id={user.id}).")


if __name__ == "__main__":
    main()
