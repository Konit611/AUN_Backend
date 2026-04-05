from fastapi import APIRouter

router = APIRouter()

MOCK_RESULTS = {
    "SHRB": {
        "sakes": [
            {
                "name": "鳳凰美田 純米大吟醸",
                "brewery": "小林酒造",
                "region": "栃木県",
                "description": "華やかなマスカットの香りとクリアな酸味。",
                "imagePath": "/images/sake-placeholder.jpg",
                "tags": [
                    {"label": "Aromatic", "variant": "primary"},
                    {"label": "Chilled", "variant": "secondary"},
                ],
            },
            {
                "name": "醸し人九平次 希望の水",
                "brewery": "萬乗醸造",
                "region": "愛知県",
                "description": "ワインのような立体感とエレガントな余韻。",
                "imagePath": "/images/sake-placeholder.jpg",
                "tags": [
                    {"label": "Refined", "variant": "primary"},
                    {"label": "Room Temp", "variant": "secondary"},
                ],
            },
            {
                "name": "たかちよ 扁平精米",
                "brewery": "髙千代酒造",
                "region": "新潟県",
                "description": "完熟した果実味とジューシーな旨味の調和。",
                "imagePath": "/images/sake-placeholder.jpg",
                "tags": [
                    {"label": "Floral", "variant": "primary"},
                    {"label": "Summer", "variant": "secondary"},
                ],
            },
        ],
        "pairingSectionTitle": "美食の相性図鑑",
        "pairingSectionDescription": "SHRBタイプは、香りの重なりを愉しむマリアージュが得意。素材の甘みを引き立てる、繊細なペアリングをご提案します。",
        "pairings": [
            {
                "emoji": "\U0001f363",
                "foodName": "白身魚の昆布締め",
                "sakeName": "フルーティーな大吟醸",
                "temperature": "冷酒 5-10\u00b0C",
                "description": "昆布の旨味を日本酒の華やかな香りが包み込み、鼻に抜ける余韻が完成されます。",
            },
            {
                "emoji": "\U0001f353",
                "foodName": "フレッシュベリーの白和え",
                "sakeName": "微発泡濁り酒",
                "temperature": "冷酒 8-12\u00b0C",
                "description": "果実の酸とシュワっとした炭酸が、豆乳のまろやかさをリフレッシュさせます。",
            },
            {
                "emoji": "\U0001fad5",
                "foodName": "ブッラータチーズと季節の果実",
                "sakeName": "酸の高い原酒",
                "temperature": "常温",
                "description": "濃厚なクリーム感を、日本酒の持つ輪郭のある酸がスマートに引き締めます。",
            },
        ],
    },
}


@router.get("/quiz-results/{code}")
def get_quiz_result(code: str):
    result = MOCK_RESULTS.get(code.upper())
    if not result:
        result = MOCK_RESULTS["SHRB"]
    return result
