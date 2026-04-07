from fastapi import APIRouter, HTTPException
from typing import Optional

from app.api.v1.schemas import paginate

router = APIRouter()

CATEGORY_FILTERS = [
    {"key": "all", "label": "すべて"},
    {"key": "brewery", "label": "蔵元の物語"},
    {"key": "sake-knowledge", "label": "日本酒の知識"},
    {"key": "culture", "label": "酒の文化"},
]

ARTICLES = [
    {
        "slug": "kubota-brewery-story",
        "title": "朝日酒造の挑戦",
        "subtitle": "久保田を生んだ新潟の蔵元が語る、伝統と革新の物語",
        "category": "brewery",
        "categoryLabel": "蔵元の物語",
        "date": "2026-03-28",
        "readTime": "8 min",
        "emoji": "🏯",
        "excerpt": "新潟県長岡市に佇む朝日酒造。1830年の創業以来、越後の厳しい冬と豊かな水が育んだ酒造りの伝統を、現代の技術と融合させてきた。",
        "body": [
            {"type": "paragraph", "text": "新潟県長岡市に佇む朝日酒造。1830年の創業以来、越後の厳しい冬と豊かな水が育んだ酒造りの伝統を、現代の技術と融合させてきた。代表銘柄「久保田」は、1985年の発売以来、日本酒の新しいスタンダードを築き上げた。"},
            {"type": "heading", "text": "越後の水、越後の米"},
            {"type": "image", "emoji": "💧", "caption": "朝日酒造の仕込み水は、地下深くから汲み上げた軟水を使用"},
            {"type": "paragraph", "text": "酒造りの根幹をなすのは、水と米。朝日酒造が使う仕込み水は、越後山脈の雪解け水が地下で長い年月をかけて磨かれた軟水だ。この水が、久保田のすっきりとしたキレ味を生み出している。"},
            {"type": "paragraph", "text": "米にもこだわりがある。自社で契約栽培する「五百万石」と「越淡麗」を主に使用し、精米から一貫して管理する。特に久保田 萬寿に使われる越淡麗は、50%まで磨き上げることで、雑味のない透明感のある味わいを実現している。"},
            {"type": "heading", "text": "伝統と革新の共存"},
            {"type": "quote", "text": "変わらない味を届けるために、私たちは常に変わり続けなければならない。", "author": "朝日酒造 杜氏"},
            {"type": "paragraph", "text": "朝日酒造の酒蔵には、最新の温度管理システムが導入されている。しかし、最終的な判断を下すのは、常に人間の五感だ。数値だけでは捉えきれない微妙な変化を、杜氏の経験と直感が補っている。"},
            {"type": "paragraph", "text": "近年では、若い蔵人たちが新しい酵母の研究や、海外市場向けの商品開発にも挑戦している。伝統を守りながら、日本酒の可能性を広げ続ける朝日酒造の姿勢は、まさに「温故知新」を体現している。"},
        ],
    },
    {
        "slug": "sake-temperature-guide",
        "title": "温度で変わる日本酒の世界",
        "subtitle": "冷酒から熱燗まで、温度帯別の楽しみ方完全ガイド",
        "category": "sake-knowledge",
        "categoryLabel": "日本酒の知識",
        "date": "2026-03-20",
        "readTime": "6 min",
        "emoji": "🌡️",
        "excerpt": "同じ一本の日本酒でも、温度を変えるだけで全く異なる表情を見せる。冷酒のシャープさ、常温のまろやかさ、燗酒の包容力。",
        "body": [
            {"type": "paragraph", "text": "日本酒は世界でも珍しい、幅広い温度帯で楽しめるお酒だ。5°Cの冷酒から55°Cの飛び切り燗まで、約50度もの温度幅の中で、それぞれ異なる魅力を発揮する。"},
            {"type": "heading", "text": "冷酒（5〜15°C）"},
            {"type": "paragraph", "text": "大吟醸や吟醸酒など、華やかな香りを楽しむタイプは冷酒がおすすめ。果物のようなフルーティーな香りが際立ち、すっきりとした飲み口が楽しめる。ただし冷やしすぎると香りが閉じてしまうので、冷蔵庫から出して少し待つのがコツ。"},
            {"type": "heading", "text": "常温（15〜25°C）"},
            {"type": "paragraph", "text": "「冷や」とも呼ばれる常温は、日本酒本来の味わいを最もストレートに感じられる温度帯。米の旨味やコク、酸味のバランスが自然に広がる。純米酒や本醸造酒で試してみてほしい。"},
            {"type": "heading", "text": "燗酒（40〜55°C）"},
            {"type": "image", "emoji": "♨️", "caption": "ぬる燗（40°C）は、最も多くの日本酒に合う万能な温度帯"},
            {"type": "paragraph", "text": "燗にすると、冷酒では感じにくかった米の甘みやコクが膨らみ、まろやかな口当たりに変化する。特にぬる燗（40°C前後）は、料理との相性も抜群。脂の乗った魚や煮物と合わせると、互いの旨味が引き立て合う至福のペアリングが完成する。"},
            {"type": "quote", "text": "燗酒は日本酒の懐の深さを教えてくれる。同じ酒でも、5度違うだけで別物になる。", "author": "ソムリエ 山田太郎"},
        ],
    },
    {
        "slug": "dassai-revolution",
        "title": "獺祭が起こした革命",
        "subtitle": "山口県の小さな蔵が、世界の日本酒市場を変えるまで",
        "category": "brewery",
        "categoryLabel": "蔵元の物語",
        "date": "2026-03-12",
        "readTime": "10 min",
        "emoji": "🌏",
        "excerpt": "かつて廃業寸前だった旭酒造が、データ駆動の酒造りと大胆なブランディングで世界的な成功を収めた。その裏には、常識を覆す決断の連続があった。",
        "body": [
            {"type": "paragraph", "text": "山口県岩国市の山奥に位置する旭酒造。1984年、三代目社長の桜井博志が家業を継いだとき、年間売上はピーク時の3分の1にまで落ち込んでいた。地方の小さな蔵が生き残るために、彼が選んだ道は「量より質」への大転換だった。"},
            {"type": "heading", "text": "杜氏なき酒造り"},
            {"type": "paragraph", "text": "旭酒造の最大の特徴は、伝統的な杜氏制度を廃止したことだ。代わりに、温度や湿度のデータを徹底的に管理し、社員全員で酒造りに携わるシステムを構築した。これにより、年間を通じた安定した品質管理が可能になった。"},
            {"type": "quote", "text": "データは嘘をつかない。しかし、データだけでは感動する酒は生まれない。", "author": "旭酒造 桜井博志"},
            {"type": "heading", "text": "世界への挑戦"},
            {"type": "paragraph", "text": "獺祭は現在、世界30カ国以上に輸出されている。ニューヨークに直営バーをオープンし、パリの三ツ星レストランのワインリストにも名を連ねる。「日本酒を世界酒に」という桜井の夢は、着実に実現しつつある。"},
            {"type": "paragraph", "text": "2023年には、ニューヨーク州ハイドパークに海外初の酒蔵を設立。現地の水と米を使いながらも、獺祭クオリティを再現するという新たな挑戦が始まっている。"},
        ],
    },
    {
        "slug": "sake-rice-varieties",
        "title": "酒米の個性を知る",
        "subtitle": "山田錦、五百万石、雄町…主要酒米の特徴と味わいの違い",
        "category": "sake-knowledge",
        "categoryLabel": "日本酒の知識",
        "date": "2026-03-05",
        "readTime": "7 min",
        "emoji": "🌾",
        "excerpt": "日本酒の味わいを大きく左右する酒米。それぞれの品種が持つ個性を知れば、日本酒選びがもっと楽しくなる。",
        "body": [
            {"type": "paragraph", "text": "日本酒造りに使われる酒造好適米は、食用米とは異なる特別な品種だ。粒が大きく、中心部に「心白」と呼ばれるデンプン質の白い部分がある。この心白が、日本酒の透明感のある味わいを生み出す鍵となっている。"},
            {"type": "heading", "text": "山田錦 — 酒米の王"},
            {"type": "paragraph", "text": "兵庫県を中心に栽培される山田錦は、酒米の最高峰とされる。大粒で心白が大きく、高精白に耐えるため、大吟醸酒の原料として最も多く使われている。山田錦で醸した酒は、華やかな香りと上品な甘みが特徴だ。"},
            {"type": "heading", "text": "五百万石 — 淡麗辛口の立役者"},
            {"type": "paragraph", "text": "新潟県で開発された五百万石は、すっきりとした淡麗辛口の酒を生み出す品種。寒冷地に適した栽培特性を持ち、新潟をはじめとする北陸地方で広く使われている。久保田や八海山など、キレの良い酒の多くがこの米から生まれている。"},
            {"type": "heading", "text": "雄町 — 個性派の古代米"},
            {"type": "paragraph", "text": "岡山県が誇る雄町は、現存する最古の酒米品種のひとつ。栽培が難しく一時は絶滅寸前だったが、近年復活を遂げた。雄町で醸した酒は、豊かなコクとふくよかな旨味が特徴で、「オマチスト」と呼ばれる熱狂的なファンも多い。"},
        ],
    },
    {
        "slug": "niigata-sake-culture",
        "title": "新潟、酒の国を歩く",
        "subtitle": "日本一の酒どころで出会う、風土と人と一杯の物語",
        "category": "culture",
        "categoryLabel": "酒の文化",
        "date": "2026-02-25",
        "readTime": "9 min",
        "emoji": "🗾",
        "excerpt": "日本で最も多くの酒蔵を擁する新潟県。雪国の厳しい気候が育んだ「淡麗辛口」の文化は、いかにして生まれたのか。",
        "body": [
            {"type": "paragraph", "text": "新潟県には約90の酒蔵がひしめく。人口あたりの酒蔵数は日本一。この数字が示すのは、新潟の人々がいかに日本酒を愛し、生活の中に根付かせてきたかということだ。"},
            {"type": "heading", "text": "雪が育てる酒"},
            {"type": "image", "emoji": "❄️", "caption": "豪雪地帯の酒蔵では、雪の冷気を利用した低温発酵が行われる"},
            {"type": "paragraph", "text": "新潟の酒造りに欠かせないのが、豊富な雪解け水と厳しい寒さだ。冬の間、蔵の中は自然と低温に保たれ、ゆっくりと発酵が進む。この環境が、新潟特有のすっきりとした味わいを生み出している。"},
            {"type": "quote", "text": "新潟の酒は、雪のように透明で、雪のように静かに心に染みる。", "author": "新潟県酒造組合"},
            {"type": "paragraph", "text": "JR新潟駅構内にある「ぽんしゅ館」では、県内すべての酒蔵の酒を利き酒できる。500円でコイン5枚を購入し、壁一面に並ぶ自動販売機型の利き酒マシンから好みの一杯を選ぶ。旅の始まりに、まずはここで新潟の酒の多様性を体感してほしい。"},
        ],
    },
]


def _article_without_body(article: dict) -> dict:
    return {k: v for k, v in article.items() if k != "body"}


@router.get("/articles")
def list_articles(
    page: int = 1,
    page_size: int = 20,
    category: Optional[str] = None,
):
    filtered = ARTICLES
    if category and category != "all":
        filtered = [a for a in ARTICLES if a["category"] == category]

    result = paginate([_article_without_body(a) for a in filtered], page, page_size)
    result["filters"] = {"categories": CATEGORY_FILTERS}
    return result


@router.get("/articles/{slug}")
def get_article(slug: str):
    for article in ARTICLES:
        if article["slug"] == slug:
            return article
    raise HTTPException(status_code=404, detail=f"Article with slug '{slug}' not found")
