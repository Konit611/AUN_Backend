from fastapi import APIRouter, HTTPException

router = APIRouter()

SAKE_DETAILS = {
    "dassai-45": {
        "id": "dassai-45",
        "name": "獺祭 純米大吟醸45",
        "brewery": "旭酒造",
        "region": "山口県",
        "description": "最高の「普通」を目指した、旭酒造のスタンダード。磨き45%の贅沢な造りでありながら、日常に寄り添う親しみやすさと、果実のような華やかな香りが調和した一品です。",
        "type": "純米大吟醸",
        "rice": "山田錦",
        "polishing": "45%",
        "flavorTags": [
            {"label": "フルーティー", "primary": True},
            {"label": "華やか", "primary": True},
            {"label": "軽い", "primary": False},
            {"label": "甘口", "primary": False},
        ],
        "servingTags": ["冷酒 5-10\u00b0C", "通年"],
        "pairings": [
            {
                "emoji": "\U0001f362",
                "foodName": "焼き鳥（タレ）",
                "description": "甘辛いタレのコクが、獺祭のフルーティーな甘みと絶妙に引き立て合います。",
                "imagePlaceholder": "yakitori",
            },
            {
                "emoji": "\U0001f41f",
                "foodName": "旬の刺身",
                "description": "白身魚や帆立など、繊細な甘みを持つ魚介との相性は抜群です。",
                "imagePlaceholder": "sashimi",
            },
            {
                "emoji": "\U0001f9c0",
                "foodName": "カマンベール",
                "description": "クリーミーなチーズの質感が、大吟醸の滑らかな口当たりと優雅に重なります。",
                "imagePlaceholder": "cheese",
            },
        ],
    },
}


@router.get("/sake")
def list_sake():
    return [
        {
            "id": s["id"],
            "name": s["name"],
            "brewery": s["brewery"],
            "region": s["region"],
            "servingTags": s["servingTags"],
        }
        for s in SAKE_DETAILS.values()
    ]


@router.get("/sake/{sake_id}")
def get_sake(sake_id: str):
    sake = SAKE_DETAILS.get(sake_id)
    if not sake:
        raise HTTPException(status_code=404, detail=f"Sake '{sake_id}' not found")
    return sake
