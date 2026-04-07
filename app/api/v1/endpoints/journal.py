from fastapi import APIRouter, HTTPException, Response
from pydantic import BaseModel
from typing import Optional
import uuid

from app.api.v1.schemas import paginate

router = APIRouter()


class SakeProfile(BaseModel):
    sweetDry: int
    heavyLight: int
    richCalm: int
    boldSmooth: int


class TastingNote(BaseModel):
    profile: SakeProfile
    aroma: str
    taste: str
    finish: str
    temperature: str
    pairing: Optional[str] = None
    memo: Optional[str] = None


class JournalEntryCreate(BaseModel):
    sakeName: str
    brewery: Optional[str] = None
    category: Optional[str] = None
    date: str
    rating: int
    tasting: TastingNote
    imagePath: Optional[str] = None


JOURNAL_ENTRIES = [
    {
        "id": "1",
        "sakeName": "獺祭 純米大吟醸45",
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
        "imagePath": "/images/journal/sake-1.jpg",
    },
    {
        "id": "2",
        "sakeName": "久保田 萬寿",
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
        "imagePath": "/images/journal/sake-2.jpg",
    },
    {
        "id": "3",
        "sakeName": "新政 No.6 S-type",
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
        "imagePath": "/images/journal/sake-3.jpg",
    },
    {
        "id": "4",
        "sakeName": "醸し人九平次 希望の月",
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
        "imagePath": "/images/journal/sake-4.jpg",
    },
    {
        "id": "5",
        "sakeName": "黒龍 大吟醸",
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
        "imagePath": "/images/journal/sake-5.jpg",
    },
    {
        "id": "6",
        "sakeName": "鍋島 New Moon",
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
        "imagePath": "/images/journal/sake-6.jpg",
    },
]


@router.get("/journal")
def list_entries(page: int = 1, page_size: int = 20):
    return paginate(JOURNAL_ENTRIES, page, page_size)


@router.get("/journal/{entry_id}")
def get_entry(entry_id: str):
    for entry in JOURNAL_ENTRIES:
        if entry["id"] == entry_id:
            return entry
    raise HTTPException(status_code=404, detail=f"Journal entry '{entry_id}' not found")


@router.post("/journal", status_code=201)
def create_entry(entry: JournalEntryCreate):
    new_entry = entry.model_dump()
    new_entry["id"] = str(uuid.uuid4())
    JOURNAL_ENTRIES.append(new_entry)
    return new_entry


@router.put("/journal/{entry_id}")
def update_entry(entry_id: str, entry: JournalEntryCreate):
    for i, existing in enumerate(JOURNAL_ENTRIES):
        if existing["id"] == entry_id:
            updated = entry.model_dump()
            updated["id"] = entry_id
            JOURNAL_ENTRIES[i] = updated
            return updated
    raise HTTPException(status_code=404, detail=f"Journal entry '{entry_id}' not found")


@router.delete("/journal/{entry_id}", status_code=204)
def delete_entry(entry_id: str):
    for i, existing in enumerate(JOURNAL_ENTRIES):
        if existing["id"] == entry_id:
            JOURNAL_ENTRIES.pop(i)
            return Response(status_code=204)
    raise HTTPException(status_code=404, detail=f"Journal entry '{entry_id}' not found")
