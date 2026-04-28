"""Seed sake / pairing_guide / event tables with 5 verification rows.  # noqa: D205

Runs as a script (`python scripts/seed_sake.py`); the sys.path patch below
adds the project root so `from app...` resolves.

Selected for schema-shape verification (geographic + type diversity):
  - dassai-45         (山口県, 純米大吟醸,    fruity)
  - kubota-manju      (新潟県, 純米大吟醸,    mellow)
  - denshu-tokubetsu  (青森県, 特別純米,      umami)
  - aramasa-no6       (秋田県, 純米,          modern/sour)
  - nabeshima-newmoon (佐賀県, 純米吟醸,      juicy)

Run inside the backend container:
    docker compose exec backend uv run python scripts/seed_sake.py

Idempotent: skips rows whose primary key (sake.id, pairing_item.id, or
pairing_category.slug) already exists.

Note: persona_code is intentionally left NULL — the founder must hand-curate
the persona-to-sake mapping. This is the core curation judgment that should
not be auto-generated. See docs/01_제품_설계서.md.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from sqlmodel import Session, select

from app.core.database import engine
from app.models.pairing_guide import PairingCategory, PairingItem
from app.models.sake import Sake, SakeFlavorTag, SakePairing


SAKES: list[dict] = [
    {
        "id": "dassai-45",
        "name": "獺祭 純米大吟醸45",
        "brewery": "旭酒造",
        "region": "山口県",
        "description": "最高の「普通」を目指した、旭酒造のスタンダード。磨き45%の贅沢な造りでありながら、日常に寄り添う親しみやすさと、果実のような華やかな香りが調和した一品です。",
        "type": "純米大吟醸",
        "rice": "山田錦",
        "polishing": "45%",
        "serving_temperature": "冷酒 5-10°C",
        "serving_season": "通年",
        "flavor_tags": [
            {"label": "フルーティー", "is_primary": True},
            {"label": "華やか", "is_primary": True},
            {"label": "軽い", "is_primary": False},
            {"label": "甘口", "is_primary": False},
        ],
        "pairings": [
            {"emoji": "🍢", "food_name": "焼き鳥（タレ）", "description": "甘辛いタレのコクが、獺祭のフルーティーな甘みと絶妙に引き立て合います。", "image_placeholder": "yakitori"},
            {"emoji": "🐟", "food_name": "旬の刺身", "description": "白身魚や帆立など、繊細な甘みを持つ魚介との相性は抜群です。", "image_placeholder": "sashimi"},
            {"emoji": "🧀", "food_name": "カマンベール", "description": "クリーミーなチーズの質感が、大吟醸の滑らかな口当たりと優雅に重なります。", "image_placeholder": "cheese"},
        ],
    },
    {
        "id": "kubota-manju",
        "name": "久保田 萬寿",
        "brewery": "朝日酒造",
        "region": "新潟県",
        "description": "朝日酒造の最高峰。越淡麗を50%まで磨き上げ、柔らかく深い味わいと、上品な香りが織りなす格調高い一杯。特別な日にふさわしい贅沢な純米大吟醸です。",
        "type": "純米大吟醸",
        "rice": "越淡麗",
        "polishing": "50%",
        "serving_temperature": "冷酒 5-10°C",
        "serving_season": "通年",
        "flavor_tags": [
            {"label": "まろやか", "is_primary": True},
            {"label": "上品", "is_primary": True},
            {"label": "コクがある", "is_primary": False},
            {"label": "辛口", "is_primary": False},
        ],
        "pairings": [
            {"emoji": "🍢", "food_name": "焼き鳥（タレ）", "description": "萬寿のまろやかなコクが、タレの甘辛さを包み込み、何本でも進む心地よさ。", "image_placeholder": "yakitori"},
            {"emoji": "🐟", "food_name": "昆布締め", "description": "昆布の旨味と萬寿のふくよかな味わいが、静かに重なり合う上質な組み合わせ。", "image_placeholder": "kobujime"},
            {"emoji": "🍲", "food_name": "湯豆腐", "description": "素材の繊細な味わいを、萬寿の柔らかな旨味が引き立てます。", "image_placeholder": "yudofu"},
        ],
    },
    {
        "id": "denshu-tokubetsu",
        "name": "田酒 特別純米",
        "brewery": "西田酒造店",
        "region": "青森県",
        "description": "田の酒、と名付けられた通り、米の旨味を最大限に引き出した骨太な純米酒。しっかりとした味わいながら、後味はすっきり。燗にすると更に旨味が広がります。",
        "type": "特別純米",
        "rice": "華吹雪",
        "polishing": "55%",
        "serving_temperature": "ぬる燗 40°C",
        "serving_season": "冬",
        "flavor_tags": [
            {"label": "米の旨味", "is_primary": True},
            {"label": "骨太", "is_primary": True},
            {"label": "辛口", "is_primary": False},
            {"label": "燗上がり", "is_primary": False},
        ],
        "pairings": [
            {"emoji": "🫕", "food_name": "もつ鍋", "description": "濃厚なもつの旨味を、田酒のしっかりした米の味わいが受け止めます。", "image_placeholder": "motsunabe"},
            {"emoji": "🐟", "food_name": "ぶりの照り焼き", "description": "脂の乗ったぶりと、燗にした田酒のコクが絶妙にマッチ。", "image_placeholder": "buri-teriyaki"},
            {"emoji": "🍢", "food_name": "焼きおにぎり", "description": "香ばしい味噌の風味と、米の旨味同士が共鳴する素朴な幸せ。", "image_placeholder": "yaki-onigiri"},
        ],
    },
    {
        "id": "aramasa-no6",
        "name": "新政 No.6 S-type",
        "brewery": "新政酒造",
        "region": "秋田県",
        "description": "6号酵母発祥の蔵が醸す、革新的な純米酒。シャープな酸味と白ぶどうのような香り、微かな乳酸のニュアンス。ワイン好きも唸らせる個性派です。",
        "type": "純米",
        "rice": "秋田酒こまち",
        "polishing": "55%",
        "serving_temperature": "冷酒 8°C",
        "serving_season": "通年",
        "flavor_tags": [
            {"label": "酸味", "is_primary": True},
            {"label": "モダン", "is_primary": True},
            {"label": "軽い", "is_primary": False},
            {"label": "ドライ", "is_primary": False},
        ],
        "pairings": [
            {"emoji": "🦪", "food_name": "牡蠣のポン酢", "description": "新政の酸味が牡蠣のミネラル感と共鳴し、レモンを絞ったような爽快さ。", "image_placeholder": "kaki-ponzu"},
            {"emoji": "🧀", "food_name": "シェーヴルチーズ", "description": "ヤギのチーズの酸味と新政の乳酸が、フランス的なマリアージュを生みます。", "image_placeholder": "chevre"},
            {"emoji": "🐟", "food_name": "カルパッチョ", "description": "オリーブオイルと柑橘の白身魚に、新政のシャープさが映えます。", "image_placeholder": "carpaccio"},
        ],
    },
    {
        "id": "nabeshima-newmoon",
        "name": "鍋島 New Moon",
        "brewery": "富久千代酒造",
        "region": "佐賀県",
        "description": "IWC（インターナショナル・ワイン・チャレンジ）で頂点に輝いた実力派。ジューシーな果実味と微かな発泡感が、新しい日本酒体験を届けてくれます。",
        "type": "純米吟醸",
        "rice": "山田錦",
        "polishing": "50%",
        "serving_temperature": "冷酒 5°C",
        "serving_season": "春・夏",
        "flavor_tags": [
            {"label": "ジューシー", "is_primary": True},
            {"label": "フレッシュ", "is_primary": True},
            {"label": "甘口", "is_primary": False},
            {"label": "発泡感", "is_primary": False},
        ],
        "pairings": [
            {"emoji": "🥗", "food_name": "生春巻き", "description": "フレッシュな野菜と海老に、鍋島の果実味が爽やかに寄り添います。", "image_placeholder": "namaharumaki"},
            {"emoji": "🧀", "food_name": "モッツァレラとトマト", "description": "カプレーゼの酸味と鍋島のジューシーさが、イタリアンな相性。", "image_placeholder": "caprese"},
            {"emoji": "🍓", "food_name": "フルーツタルト", "description": "デザートとの意外な組み合わせ。果実味同士が華やかに響き合います。", "image_placeholder": "fruit-tart"},
        ],
    },
]


CATEGORIES: list[dict] = [
    {"slug": "grilled", "label": "焼き物", "title": "焼き物のペアリング", "position": 0},
    {"slug": "sashimi", "label": "刺身", "title": "刺身のペアリング", "position": 1},
    {"slug": "nabe", "label": "鍋物", "title": "鍋物のペアリング", "position": 2},
]


# sake_id is set only when the referenced sake exists in SAKES above (FK).
# Otherwise None — the pairing_item still has sake_name/brewery as text.
ITEMS: list[dict] = [
    {
        "id": "grilled-1",
        "category_slug": "grilled",
        "position": 0,
        "emoji": "🍢",
        "food_name": "焼き鳥（タレ）",
        "sake_name": "久保田 萬寿",
        "sake_brewery": "朝日酒造（新潟県）",
        "sake_type": "純米大吟醸",
        "temperature": "冷酒 5-10°C",
        "season": "冬",
        "description": "芳醇なコクのあるタレには、同じく深みのある萬寿を。甘辛い醤油の風味と、酒のまろやかな旨味が口の中で静かに重なり合います。",
        "body": "居酒屋の定番、焼き鳥のタレ。その甘辛い醤油ダレの奥深い味わいに、久保田 萬寿のふくよかなコクが寄り添います。萬寿の持つ柔らかな甘みと旨味が、タレの焦がし醤油の香ばしさと重なり合い、口の中で豊かなハーモニーを奏でます。",
        "why_it_works": "タレの甘辛さは、酒の旨味成分と共鳴しやすい。萬寿のまろやかなコクがタレの味わいを包み込み、脂の後味を優しく流してくれるため、何本でも食べ進められる心地よさが生まれます。",
        "how_to_enjoy": "焼き鳥は焼きたてが命。まずはタレをひと口、次に萬寿を含んで味わいの変化を楽しんでください。5〜10°Cに冷やすと、キレが出てタレの濃さとバランスが取れます。",
        "food_image": "/images/pairing/yakitori-tare.jpg",
        "sake_image": "/images/pairing/kubota-manju.jpg",
        "sake_id": "kubota-manju",
    },
    {
        "id": "grilled-2",
        "category_slug": "grilled",
        "position": 1,
        "emoji": "🐟",
        "food_name": "塩焼き（鮭・鯖）",
        "sake_name": "八海山 特別本醸造",
        "sake_brewery": "八海醸造（新潟県）",
        "sake_type": "特別本醸造",
        "temperature": "常温 15-20°C",
        "season": "通年",
        "description": "魚の脂をさっぱりと流す、キレのある辛口。素材本来の味を引き立てるこの組み合わせは、毎日の夕食を格上げする究極の定番です。",
        "body": "塩だけで焼き上げた鮭や鯖。素材そのものの旨味が凝縮された一品に合わせるのは、八海山の特別本醸造。すっきりとした辛口でありながら、米の旨味がしっかり感じられるバランスの良さが、魚の持ち味を引き出します。",
        "why_it_works": "塩焼きの魚は脂と塩味のシンプルな構成。八海山のキレのある酸味が脂をさっぱりと流し、次のひと口への食欲を呼び起こします。常温にすることで酒の旨味が広がり、魚の脂との調和がより深まります。",
        "how_to_enjoy": "焼き上がりに大根おろしとレモンを添えて。常温の八海山と交互にいただくと、魚の旨味が口の中でじんわり広がります。毎日の晩酌の定番にしたいペアリングです。",
        "food_image": "/images/pairing/shioyaki-salmon.jpg",
        "sake_image": "/images/pairing/hakkaisan.jpg",
        "sake_id": None,
    },
    {
        "id": "grilled-3",
        "category_slug": "grilled",
        "position": 2,
        "emoji": "🥩",
        "food_name": "牛の炙り焼き",
        "sake_name": "獺祭 純米大吟醸 磨き三割九分",
        "sake_brewery": "旭酒造（山口県）",
        "sake_type": "純米大吟醸",
        "temperature": "ぬる燗 40°C",
        "season": "冬",
        "description": "和牛の甘みのある脂には、華やかな香りの獺祭を。少し温めることで酒の甘みが膨らみ、肉の濃厚な旨味と美しく調和します。",
        "body": "炭火で炙った和牛の芳醇な香りと、獺祭 磨き三割九分の華やかな吟醸香。一見意外な組み合わせですが、和牛の甘みのある脂と獺祭のフルーティーな甘みは、驚くほど自然に調和します。",
        "why_it_works": "和牛の脂は甘みが特徴。獺祭をぬる燗にすることで酒の甘みと旨味が膨らみ、肉の脂の甘みと同調します。香りの複雑さが加わることで、単なる「肉と酒」を超えた上質な食体験になります。",
        "how_to_enjoy": "肉は表面だけ炙って、中はレアに。獺祭は40°C前後のぬる燗で。肉をひと切れ口に入れ、脂が溶け始めたところで酒を含むと、口の中で味わいが花開きます。",
        "food_image": "/images/pairing/wagyu-aburi.jpg",
        "sake_image": "/images/pairing/dassai.jpg",
        "sake_id": None,
    },
    {
        "id": "sashimi-1",
        "category_slug": "sashimi",
        "position": 0,
        "emoji": "🐟",
        "food_name": "まぐろの赤身",
        "sake_name": "十四代 本丸",
        "sake_brewery": "高木酒造（山形県）",
        "sake_type": "本醸造",
        "temperature": "冷酒 8-12°C",
        "season": "通年",
        "description": "まぐろの鉄分を含んだ旨味に、十四代のフルーティーな甘みがマッチ。赤身の力強さを優雅に包み込みます。",
        "body": "まぐろの赤身は、鉄分を含んだ独特の旨味と適度な酸味が魅力。その力強い味わいに、十四代 本丸のフルーティーで華やかな香りが優しく寄り添います。幻の酒と呼ばれる十四代の、親しみやすい本丸だからこそ実現する日常の贅沢です。",
        "why_it_works": "赤身の鉄分は、酒の甘みと合わせることで角が取れ、旨味が引き立ちます。十四代の果実的な香りがまぐろの生臭さを包み込み、後味を爽やかにまとめます。",
        "how_to_enjoy": "赤身は薄めに切り、少量の醤油で。十四代は8〜12°Cに冷やして、赤身を口に含んだ直後に酒をひと口。鮮度の良い赤身であるほど、このペアリングの真価が発揮されます。",
        "food_image": "/images/pairing/maguro.jpg",
        "sake_image": "/images/pairing/juyondai.jpg",
        "sake_id": None,
    },
    {
        "id": "nabe-1",
        "category_slug": "nabe",
        "position": 0,
        "emoji": "🫕",
        "food_name": "もつ鍋",
        "sake_name": "田酒 特別純米",
        "sake_brewery": "西田酒造店(青森県)",
        "sake_type": "特別純米",
        "temperature": "ぬる燗 40°C",
        "season": "冬",
        "description": "濃厚なもつの旨味を、田酒のしっかりとした米の味わいが受け止めます。温めた酒が体を芯から温めてくれます。",
        "body": "博多名物のもつ鍋。ぷりぷりのもつから溶け出す濃厚な旨味と、醤油ベースのスープの深い味わい。そこに田酒の特別純米を合わせると、米の旨味がスープの奥行きと呼応し、体の芯から温まる至福の時間が訪れます。",
        "why_it_works": "もつの脂とコラーゲンは、温めた酒の旨味成分と絶妙に調和します。田酒のしっかりとした米の味わいが、濃厚なスープに負けることなく、むしろ互いの旨味を増幅させます。",
        "how_to_enjoy": "鍋が煮立ったら、まずスープをひと口。続いて田酒をぬる燗で。もつを食べた後の口の中に残る脂を、酒がすっと流してくれます。〆のちゃんぽん麺と一緒に最後の一杯を。",
        "food_image": "/images/pairing/motsunabe.jpg",
        "sake_image": "/images/pairing/denshu.jpg",
        "sake_id": "denshu-tokubetsu",
    },
]


def seed_sakes(session: Session) -> int:
    inserted = 0
    for data in SAKES:
        if session.get(Sake, data["id"]):
            continue
        sake_kwargs = {
            k: v for k, v in data.items() if k not in ("flavor_tags", "pairings")
        }
        session.add(Sake(**sake_kwargs))
        for i, tag in enumerate(data["flavor_tags"]):
            session.add(SakeFlavorTag(sake_id=data["id"], position=i, **tag))
        for i, pairing in enumerate(data["pairings"]):
            session.add(SakePairing(sake_id=data["id"], position=i, **pairing))
        inserted += 1
    return inserted


def seed_categories(session: Session) -> int:
    inserted = 0
    for data in CATEGORIES:
        existing = session.exec(
            select(PairingCategory).where(PairingCategory.slug == data["slug"])
        ).first()
        if existing:
            continue
        session.add(PairingCategory(**data))
        inserted += 1
    return inserted


def seed_items(session: Session) -> int:
    inserted = 0
    for data in ITEMS:
        if session.get(PairingItem, data["id"]):
            continue
        slug = data["category_slug"]
        category = session.exec(
            select(PairingCategory).where(PairingCategory.slug == slug)
        ).first()
        if not category:
            raise SystemExit(
                f"category '{slug}' not found — run seed_categories first."
            )
        item_kwargs = {k: v for k, v in data.items() if k != "category_slug"}
        session.add(PairingItem(category_id=category.id, **item_kwargs))
        inserted += 1
    return inserted


def main() -> None:
    with Session(engine) as session:
        n_sakes = seed_sakes(session)
        n_cats = seed_categories(session)
        session.commit()  # commit categories so seed_items can resolve their IDs
        n_items = seed_items(session)
        session.commit()
        print(
            f"Seeded sakes={n_sakes} categories={n_cats} pairing_items={n_items}"
        )


if __name__ == "__main__":
    main()
