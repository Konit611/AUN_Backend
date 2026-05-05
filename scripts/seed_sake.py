"""Seed pairing_category and pairing_item tables.

Sake / flavor / recipe seeding has moved to scripts/import_sake_csv.py
(it reads the canonical CSVs in `aun_back/data/`). This script now only
seeds the pairing_guide tables.

Run inside the backend container:
    docker compose exec backend uv run python scripts/seed_sake.py

Idempotent: skips rows whose primary key (pairing_category.slug or
pairing_item.id) already exists.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from sqlmodel import Session, select

from app.core.database import engine
from app.models.pairing_guide import PairingCategory, PairingItem


CATEGORIES: list[dict] = [
    {"slug": "grilled", "label": "焼き物", "title": "焼き物のペアリング", "position": 0},
    {"slug": "sashimi", "label": "刺身", "title": "刺身のペアリング", "position": 1},
    {"slug": "nabe", "label": "鍋物", "title": "鍋物のペアリング", "position": 2},
]


# sake_id is set only when the referenced sake exists in the sake table (FK).
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
        n_cats = seed_categories(session)
        session.commit()  # commit categories so seed_items can resolve their IDs
        n_items = seed_items(session)
        session.commit()
        print(f"Seeded categories={n_cats} pairing_items={n_items}")


if __name__ == "__main__":
    main()
