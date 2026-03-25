# aun-back

## 요구사항

- Python 3.13+
- [uv](https://docs.astral.sh/uv/)

## 설치

```bash
uv sync
```

## 서버 실행

### 개발 모드

```bash
uv run fastapi dev main.py
```

- 코드 변경 시 자동 리로드
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### 프로덕션 모드

```bash
uv run fastapi run main.py
```
