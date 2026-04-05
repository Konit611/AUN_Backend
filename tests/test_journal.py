def test_list_journal(client):
    res = client.get("/api/v1/journal")
    assert res.status_code == 200
    data = res.json()
    assert len(data) >= 6
    assert "sakeName" in data[0]
    assert "tasting" in data[0]


def test_get_journal_entry(client):
    res = client.get("/api/v1/journal/1")
    assert res.status_code == 200
    data = res.json()
    assert data["id"] == "1"
    assert "profile" in data["tasting"]
    assert "aroma" in data["tasting"]


def test_get_journal_not_found(client):
    res = client.get("/api/v1/journal/999")
    assert res.status_code == 404


def test_create_journal_entry(client):
    new_entry = {
        "sakeName": "テスト酒",
        "brewery": "テスト蔵",
        "category": "純米",
        "date": "2026-04-01",
        "rating": 4,
        "tasting": {
            "profile": {
                "sweetDry": 50,
                "heavyLight": 50,
                "richCalm": 50,
                "boldSmooth": 50,
            },
            "aroma": "テスト香り",
            "taste": "テスト味わい",
            "finish": "テスト余韻",
            "temperature": "冷酒 10°C",
        },
    }
    res = client.post("/api/v1/journal", json=new_entry)
    assert res.status_code == 201
    data = res.json()
    assert data["sakeName"] == "テスト酒"
    assert "id" in data
