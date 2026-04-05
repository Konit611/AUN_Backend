from fastapi import APIRouter, HTTPException

router = APIRouter()

CATEGORIES = [
    {
        "slug": "grilled",
        "label": "焼き物",
        "title": "焼き物のペアリング",
        "items": [
            {
                "id": "grilled-1",
                "emoji": "\U0001f362",
                "foodName": "焼き鳥（タレ）",
                "sakeName": "久保田 萬寿",
                "sakeBrewery": "朝日酒造（新潟県）",
                "sakeType": "純米大吟醸",
                "temperature": "冷酒 5-10\u00b0C",
                "season": "冬",
                "description": "芳醇なコクのあるタレには、同じく深みのある萬寿を。甘辛い醤油の風味と、酒のまろやかな旨味が口の中で静かに重なり合います。",
                "body": "居酒屋の定番、焼き鳥のタレ。その甘辛い醤油ダレの奥深い味わいに、久保田 萬寿のふくよかなコクが寄り添います。萬寿の持つ柔らかな甘みと旨味が、タレの焦がし醤油の香ばしさと重なり合い、口の中で豊かなハーモニーを奏でます。",
                "whyItWorks": "タレの甘辛さは、酒の旨味成分と共鳴しやすい。萬寿のまろやかなコクがタレの味わいを包み込み、脂の後味を優しく流してくれるため、何本でも食べ進められる心地よさが生まれます。",
                "howToEnjoy": "焼き鳥は焼きたてが命。まずはタレをひと口、次に萬寿を含んで味わいの変化を楽しんでください。5〜10\u00b0Cに冷やすと、キレが出てタレの濃さとバランスが取れます。",
                "foodImage": "/images/pairing/yakitori-tare.jpg",
                "sakeImage": "/images/pairing/kubota-manju.jpg",
            },
            {
                "id": "grilled-2",
                "emoji": "\U0001f41f",
                "foodName": "塩焼き（鮭・鯖）",
                "sakeName": "八海山 特別本醸造",
                "sakeBrewery": "八海醸造（新潟県）",
                "sakeType": "特別本醸造",
                "temperature": "常温 15-20\u00b0C",
                "season": "通年",
                "description": "魚の脂をさっぱりと流す、キレのある辛口。素材本来の味を引き立てるこの組み合わせは、毎日の夕食を格上げする究極の定番です。",
                "body": "塩だけで焼き上げた鮭や鯖。素材そのものの旨味が凝縮された一品に合わせるのは、八海山の特別本醸造。すっきりとした辛口でありながら、米の旨味がしっかり感じられるバランスの良さが、魚の持ち味を引き出します。",
                "whyItWorks": "塩焼きの魚は脂と塩味のシンプルな構成。八海山のキレのある酸味が脂をさっぱりと流し、次のひと口への食欲を呼び起こします。常温にすることで酒の旨味が広がり、魚の脂との調和がより深まります。",
                "howToEnjoy": "焼き上がりに大根おろしとレモンを添えて。常温の八海山と交互にいただくと、魚の旨味が口の中でじんわり広がります。毎日の晩酌の定番にしたいペアリングです。",
                "foodImage": "/images/pairing/shioyaki-salmon.jpg",
                "sakeImage": "/images/pairing/hakkaisan.jpg",
            },
            {
                "id": "grilled-3",
                "emoji": "\U0001f969",
                "foodName": "牛の炙り焼き",
                "sakeName": "獺祭 純米大吟醸 磨き三割九分",
                "sakeBrewery": "旭酒造（山口県）",
                "sakeType": "純米大吟醸",
                "temperature": "ぬる燗 40\u00b0C",
                "season": "冬",
                "description": "和牛の甘みのある脂には、華やかな香りの獺祭を。少し温めることで酒の甘みが膨らみ、肉の濃厚な旨味と美しく調和します。",
                "body": "炭火で炙った和牛の芳醇な香りと、獺祭 磨き三割九分の華やかな吟醸香。一見意外な組み合わせですが、和牛の甘みのある脂と獺祭のフルーティーな甘みは、驚くほど自然に調和します。",
                "whyItWorks": "和牛の脂は甘みが特徴。獺祭をぬる燗にすることで酒の甘みと旨味が膨らみ、肉の脂の甘みと同調します。香りの複雑さが加わることで、単なる「肉と酒」を超えた上質な食体験になります。",
                "howToEnjoy": "肉は表面だけ炙って、中はレアに。獺祭は40\u00b0C前後のぬる燗で。肉をひと切れ口に入れ、脂が溶け始めたところで酒を含むと、口の中で味わいが花開きます。",
                "foodImage": "/images/pairing/wagyu-aburi.jpg",
                "sakeImage": "/images/pairing/dassai.jpg",
            },
        ],
    },
    {
        "slug": "sashimi",
        "label": "刺身",
        "title": "刺身のペアリング",
        "items": [
            {
                "id": "sashimi-1",
                "emoji": "\U0001f41f",
                "foodName": "まぐろの赤身",
                "sakeName": "十四代 本丸",
                "sakeBrewery": "高木酒造（山形県）",
                "sakeType": "本醸造",
                "temperature": "冷酒 8-12\u00b0C",
                "season": "通年",
                "description": "まぐろの鉄分を含んだ旨味に、十四代のフルーティーな甘みがマッチ。赤身の力強さを優雅に包み込みます。",
                "body": "まぐろの赤身は、鉄分を含んだ独特の旨味と適度な酸味が魅力。その力強い味わいに、十四代 本丸のフルーティーで華やかな香りが優しく寄り添います。幻の酒と呼ばれる十四代の、親しみやすい本丸だからこそ実現する日常の贅沢です。",
                "whyItWorks": "赤身の鉄分は、酒の甘みと合わせることで角が取れ、旨味が引き立ちます。十四代の果実的な香りがまぐろの生臭さを包み込み、後味を爽やかにまとめます。",
                "howToEnjoy": "赤身は薄めに切り、少量の醤油で。十四代は8〜12\u00b0Cに冷やして、赤身を口に含んだ直後に酒をひと口。鮮度の良い赤身であるほど、このペアリングの真価が発揮されます。",
                "foodImage": "/images/pairing/maguro.jpg",
                "sakeImage": "/images/pairing/juyondai.jpg",
            },
        ],
    },
    {
        "slug": "nabe",
        "label": "鍋物",
        "title": "鍋物のペアリング",
        "items": [
            {
                "id": "nabe-1",
                "emoji": "\U0001fad5",
                "foodName": "もつ鍋",
                "sakeName": "田酒 特別純米",
                "sakeBrewery": "西田酒造店（青森県）",
                "sakeType": "特別純米",
                "temperature": "ぬる燗 40\u00b0C",
                "season": "冬",
                "description": "濃厚なもつの旨味を、田酒のしっかりとした米の味わいが受け止めます。温めた酒が体を芯から温めてくれます。",
                "body": "博多名物のもつ鍋。ぷりぷりのもつから溶け出す濃厚な旨味と、醤油ベースのスープの深い味わい。そこに田酒の特別純米を合わせると、米の旨味がスープの奥行きと呼応し、体の芯から温まる至福の時間が訪れます。",
                "whyItWorks": "もつの脂とコラーゲンは、温めた酒の旨味成分と絶妙に調和します。田酒のしっかりとした米の味わいが、濃厚なスープに負けることなく、むしろ互いの旨味を増幅させます。",
                "howToEnjoy": "鍋が煮立ったら、まずスープをひと口。続いて田酒をぬる燗で。もつを食べた後の口の中に残る脂を、酒がすっと流してくれます。〆のちゃんぽん麺と一緒に最後の一杯を。",
                "foodImage": "/images/pairing/motsunabe.jpg",
                "sakeImage": "/images/pairing/denshu.jpg",
            },
        ],
    },
]

SEASON_FILTERS = [
    {"key": "all", "label": "すべて"},
    {"key": "your-type", "label": "あなたのタイプ"},
    {"key": "winter", "label": "冬", "match": "冬"},
    {"key": "year-round", "label": "通年", "match": "通年"},
]


def _all_items():
    return [item for cat in CATEGORIES for item in cat["items"]]


@router.get("/pairing-guide/categories")
def get_categories():
    return CATEGORIES


@router.get("/pairing-guide/items/{item_id}")
def get_item(item_id: str):
    for item in _all_items():
        if item["id"] == item_id:
            return item
    raise HTTPException(status_code=404, detail=f"Pairing item '{item_id}' not found")


@router.get("/pairing-guide/filters/season")
def get_season_filters():
    return SEASON_FILTERS


@router.get("/pairing-guide/filters/food")
def get_food_filters():
    return [{"key": cat["slug"], "label": cat["label"]} for cat in CATEGORIES]
