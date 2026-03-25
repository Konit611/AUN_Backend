# AUN Backend

FastAPI + SQLModel + Alembic で構築されたバックエンドAPIサーバーです。

## 要件

- Python 3.13+
- [uv](https://docs.astral.sh/uv/)
- PostgreSQL 17

## セットアップ

```bash
uv sync
cp .env.example .env  # 必要に応じて編集
```

## サーバー起動

### 開発モード

```bash
uv run fastapi dev main.py
```

- コード変更時に自動リロード
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### プロダクションモード

```bash
uv run fastapi run main.py
```

## データベースマイグレーション

```bash
# マイグレーションファイルを自動生成
uv run alembic revision --autogenerate -m "説明"

# マイグレーションを実行
uv run alembic upgrade head

# 1つ前に戻す
uv run alembic downgrade -1
```

## プロジェクト構成

```
aun_back/
├── main.py                 # FastAPIエントリーポイント
├── app/
│   ├── api/v1/router.py    # APIルーター
│   ├── core/
│   │   ├── config.py       # 環境変数・設定
│   │   └── database.py     # DB接続・セッション管理
│   ├── models/             # SQLModelテーブル定義
│   ├── schemas/            # リクエスト/レスポンススキーマ
│   ├── services/           # ビジネスロジック
│   └── repositories/       # データアクセス層
├── alembic/                # マイグレーション
├── Dockerfile
└── pyproject.toml
```
