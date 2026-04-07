from fastapi import APIRouter, HTTPException

from app.api.v1.schemas import paginate

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
        "servingTags": ["冷酒 5-10°C", "通年"],
        "pairings": [
            {
                "emoji": "🍢",
                "foodName": "焼き鳥（タレ）",
                "description": "甘辛いタレのコクが、獺祭のフルーティーな甘みと絶妙に引き立て合います。",
                "imagePlaceholder": "yakitori",
            },
            {
                "emoji": "🐟",
                "foodName": "旬の刺身",
                "description": "白身魚や帆立など、繊細な甘みを持つ魚介との相性は抜群です。",
                "imagePlaceholder": "sashimi",
            },
            {
                "emoji": "🧀",
                "foodName": "カマンベール",
                "description": "クリーミーなチーズの質感が、大吟醸の滑らかな口当たりと優雅に重なります。",
                "imagePlaceholder": "cheese",
            },
        ],
    },
    "kubota-manju": {
        "id": "kubota-manju",
        "name": "久保田 萬寿",
        "brewery": "朝日酒造",
        "region": "新潟県",
        "description": "朝日酒造の最高峰。越淡麗を50%まで磨き上げ、柔らかく深い味わいと、上品な香りが織りなす格調高い一杯。特別な日にふさわしい贅沢な純米大吟醸です。",
        "type": "純米大吟醸",
        "rice": "越淡麗",
        "polishing": "50%",
        "flavorTags": [
            {"label": "まろやか", "primary": True},
            {"label": "上品", "primary": True},
            {"label": "コクがある", "primary": False},
            {"label": "辛口", "primary": False},
        ],
        "servingTags": ["冷酒 5-10°C", "通年"],
        "pairings": [
            {
                "emoji": "🍢",
                "foodName": "焼き鳥（タレ）",
                "description": "萬寿のまろやかなコクが、タレの甘辛さを包み込み、何本でも進む心地よさ。",
                "imagePlaceholder": "yakitori",
            },
            {
                "emoji": "🐟",
                "foodName": "昆布締め",
                "description": "昆布の旨味と萬寿のふくよかな味わいが、静かに重なり合う上質な組み合わせ。",
                "imagePlaceholder": "kobujime",
            },
            {
                "emoji": "🍲",
                "foodName": "湯豆腐",
                "description": "素材の繊細な味わいを、萬寿の柔らかな旨味が引き立てます。",
                "imagePlaceholder": "yudofu",
            },
        ],
    },
    "juyondai-honmaru": {
        "id": "juyondai-honmaru",
        "name": "十四代 本丸",
        "brewery": "高木酒造",
        "region": "山形県",
        "description": "入手困難な幻の酒。本醸造ながら大吟醸を凌ぐフルーティーな香りと、驚くほど滑らかな口当たり。日本酒の概念を覆した革命的な一本です。",
        "type": "本醸造",
        "rice": "五百万石",
        "polishing": "55%",
        "flavorTags": [
            {"label": "フルーティー", "primary": True},
            {"label": "滑らか", "primary": True},
            {"label": "華やか", "primary": False},
            {"label": "甘口", "primary": False},
        ],
        "servingTags": ["冷酒 8-12°C", "通年"],
        "pairings": [
            {
                "emoji": "🐟",
                "foodName": "まぐろの赤身",
                "description": "赤身の鉄分と十四代のフルーティーな甘みが、優雅にマッチします。",
                "imagePlaceholder": "maguro",
            },
            {
                "emoji": "🥗",
                "foodName": "生ハムとルッコラ",
                "description": "塩気と苦味を十四代の甘みが優しく包み込む、ワイン的な楽しみ方。",
                "imagePlaceholder": "prosciutto",
            },
            {
                "emoji": "🍓",
                "foodName": "苺の白和え",
                "description": "果実味同士が共鳴し、デザート感覚で楽しめる新しいペアリング。",
                "imagePlaceholder": "ichigo-shiraae",
            },
        ],
    },
    "hakkaisan-tokubetsu": {
        "id": "hakkaisan-tokubetsu",
        "name": "八海山 特別本醸造",
        "brewery": "八海醸造",
        "region": "新潟県",
        "description": "越後の名峰・八海山の伏流水で醸す、淡麗辛口の代名詞。すっきりとしたキレ味と、米の旨味のバランスが絶妙な、毎日の食卓に寄り添う一本です。",
        "type": "特別本醸造",
        "rice": "五百万石",
        "polishing": "60%",
        "flavorTags": [
            {"label": "キレがある", "primary": True},
            {"label": "すっきり", "primary": True},
            {"label": "辛口", "primary": False},
            {"label": "淡麗", "primary": False},
        ],
        "servingTags": ["常温 15-20°C", "通年"],
        "pairings": [
            {
                "emoji": "🐟",
                "foodName": "塩焼き（鮭・鯖）",
                "description": "魚の脂をさっぱりと流すキレの良さ。毎日の晩酌の定番ペアリング。",
                "imagePlaceholder": "shioyaki",
            },
            {
                "emoji": "🍢",
                "foodName": "おでん",
                "description": "出汁の旨味と八海山のすっきりした味わいが、温かく寄り添います。",
                "imagePlaceholder": "oden",
            },
            {
                "emoji": "🥬",
                "foodName": "浅漬け",
                "description": "野菜の爽やかさと辛口の八海山は、永遠の定番コンビです。",
                "imagePlaceholder": "asazuke",
            },
        ],
    },
    "denshu-tokubetsu": {
        "id": "denshu-tokubetsu",
        "name": "田酒 特別純米",
        "brewery": "西田酒造店",
        "region": "青森県",
        "description": "田の酒、と名付けられた通り、米の旨味を最大限に引き出した骨太な純米酒。しっかりとした味わいながら、後味はすっきり。燗にすると更に旨味が広がります。",
        "type": "特別純米",
        "rice": "華吹雪",
        "polishing": "55%",
        "flavorTags": [
            {"label": "米の旨味", "primary": True},
            {"label": "骨太", "primary": True},
            {"label": "辛口", "primary": False},
            {"label": "燗上がり", "primary": False},
        ],
        "servingTags": ["ぬる燗 40°C", "冬"],
        "pairings": [
            {
                "emoji": "🫕",
                "foodName": "もつ鍋",
                "description": "濃厚なもつの旨味を、田酒のしっかりした米の味わいが受け止めます。",
                "imagePlaceholder": "motsunabe",
            },
            {
                "emoji": "🐟",
                "foodName": "ぶりの照り焼き",
                "description": "脂の乗ったぶりと、燗にした田酒のコクが絶妙にマッチ。",
                "imagePlaceholder": "buri-teriyaki",
            },
            {
                "emoji": "🍢",
                "foodName": "焼きおにぎり",
                "description": "香ばしい味噌の風味と、米の旨味同士が共鳴する素朴な幸せ。",
                "imagePlaceholder": "yaki-onigiri",
            },
        ],
    },
    "nabeshima-newmoon": {
        "id": "nabeshima-newmoon",
        "name": "鍋島 New Moon",
        "brewery": "富久千代酒造",
        "region": "佐賀県",
        "description": "IWC（インターナショナル・ワイン・チャレンジ）で頂点に輝いた実力派。ジューシーな果実味と微かな発泡感が、新しい日本酒体験を届けてくれます。",
        "type": "純米吟醸",
        "rice": "山田錦",
        "polishing": "50%",
        "flavorTags": [
            {"label": "ジューシー", "primary": True},
            {"label": "フレッシュ", "primary": True},
            {"label": "甘口", "primary": False},
            {"label": "発泡感", "primary": False},
        ],
        "servingTags": ["冷酒 5°C", "春・夏"],
        "pairings": [
            {
                "emoji": "🥗",
                "foodName": "生春巻き",
                "description": "フレッシュな野菜と海老に、鍋島の果実味が爽やかに寄り添います。",
                "imagePlaceholder": "namaharumaki",
            },
            {
                "emoji": "🧀",
                "foodName": "モッツァレラとトマト",
                "description": "カプレーゼの酸味と鍋島のジューシーさが、イタリアンな相性。",
                "imagePlaceholder": "caprese",
            },
            {
                "emoji": "🍓",
                "foodName": "フルーツタルト",
                "description": "デザートとの意外な組み合わせ。果実味同士が華やかに響き合います。",
                "imagePlaceholder": "fruit-tart",
            },
        ],
    },
    "aramasa-no6": {
        "id": "aramasa-no6",
        "name": "新政 No.6 S-type",
        "brewery": "新政酒造",
        "region": "秋田県",
        "description": "6号酵母発祥の蔵が醸す、革新的な純米酒。シャープな酸味と白ぶどうのような香り、微かな乳酸のニュアンス。ワイン好きも唸らせる個性派です。",
        "type": "純米",
        "rice": "秋田酒こまち",
        "polishing": "55%",
        "flavorTags": [
            {"label": "酸味", "primary": True},
            {"label": "モダン", "primary": True},
            {"label": "軽い", "primary": False},
            {"label": "ドライ", "primary": False},
        ],
        "servingTags": ["冷酒 8°C", "通年"],
        "pairings": [
            {
                "emoji": "🦪",
                "foodName": "牡蠣のポン酢",
                "description": "新政の酸味が牡蠣のミネラル感と共鳴し、レモンを絞ったような爽快さ。",
                "imagePlaceholder": "kaki-ponzu",
            },
            {
                "emoji": "🧀",
                "foodName": "シェーヴルチーズ",
                "description": "ヤギのチーズの酸味と新政の乳酸が、フランス的なマリアージュを生みます。",
                "imagePlaceholder": "chevre",
            },
            {
                "emoji": "🐟",
                "foodName": "カルパッチョ",
                "description": "オリーブオイルと柑橘の白身魚に、新政のシャープさが映えます。",
                "imagePlaceholder": "carpaccio",
            },
        ],
    },
    "kokuryu-daiginjo": {
        "id": "kokuryu-daiginjo",
        "name": "黒龍 大吟醸",
        "brewery": "黒龍酒造",
        "region": "福井県",
        "description": "福井県永平寺町の名水で醸す、端正な大吟醸。控えめながら品のある吟醸香と、なめらかで柔らかな口当たり。穏やかに消えていく余韻が印象的です。",
        "type": "大吟醸",
        "rice": "山田錦",
        "polishing": "50%",
        "flavorTags": [
            {"label": "穏やか", "primary": True},
            {"label": "なめらか", "primary": True},
            {"label": "上品", "primary": False},
            {"label": "バランス", "primary": False},
        ],
        "servingTags": ["冷酒 10°C", "通年"],
        "pairings": [
            {
                "emoji": "🐟",
                "foodName": "白身魚の薄造り",
                "description": "繊細な白身の甘みを、黒龍の穏やかな味わいがそっと引き立てます。",
                "imagePlaceholder": "usuzukuri",
            },
            {
                "emoji": "🍲",
                "foodName": "茶碗蒸し",
                "description": "出汁の優しい旨味と、黒龍のなめらかさが心安らぐハーモニー。",
                "imagePlaceholder": "chawanmushi",
            },
            {
                "emoji": "🍡",
                "foodName": "みたらし団子",
                "description": "甘辛い醤油ダレと大吟醸の上品な甘みが、意外な好相性。",
                "imagePlaceholder": "mitarashi",
            },
        ],
    },
    "kuheiji-kibou": {
        "id": "kuheiji-kibou",
        "name": "醸し人九平次 希望の水",
        "brewery": "萬乗醸造",
        "region": "愛知県",
        "description": "フランスの三ツ星レストランでも採用される、世界が認めた日本酒。ワインのような立体的な酸と、奥行きのある旨味。エレガントで長い余韻が特徴です。",
        "type": "純米大吟醸",
        "rice": "山田錦",
        "polishing": "50%",
        "flavorTags": [
            {"label": "エレガント", "primary": True},
            {"label": "立体的", "primary": True},
            {"label": "酸がある", "primary": False},
            {"label": "辛口", "primary": False},
        ],
        "servingTags": ["常温 15°C", "通年"],
        "pairings": [
            {
                "emoji": "🍗",
                "foodName": "鶏の塩焼き",
                "description": "シンプルな塩味と九平次のエレガントな酸が、お互いを高め合います。",
                "imagePlaceholder": "tori-shioyaki",
            },
            {
                "emoji": "🧀",
                "foodName": "コンテチーズ",
                "description": "熟成チーズの深い旨味と、ワインのような九平次は自然なペアリング。",
                "imagePlaceholder": "comte",
            },
            {
                "emoji": "🐟",
                "foodName": "鯛の昆布締め",
                "description": "昆布の旨味を纏った鯛に、九平次の立体的な味わいが寄り添います。",
                "imagePlaceholder": "tai-kobujime",
            },
        ],
    },
}


@router.get("/sake")
def list_sake(page: int = 1, page_size: int = 20):
    items = [
        {
            "id": s["id"],
            "name": s["name"],
            "brewery": s["brewery"],
            "region": s["region"],
            "servingTags": s["servingTags"],
        }
        for s in SAKE_DETAILS.values()
    ]
    return paginate(items, page, page_size)


@router.get("/sake/{sake_id}")
def get_sake(sake_id: str):
    sake = SAKE_DETAILS.get(sake_id)
    if not sake:
        raise HTTPException(status_code=404, detail=f"Sake '{sake_id}' not found")
    return sake
