def test_list_journal(client):
    res = client.get("/api/v1/journal")
    assert res.status_code == 200
    data = res.json()
    assert "items" in data
    assert len(data["items"]) >= 6
    assert "sakeName" in data["items"][0]
    assert "tasting" in data["items"][0]
    assert data["page"] == 1


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


def test_update_journal_entry(client):
    updated = {
        "sakeName": "更新された酒",
        "date": "2026-04-02",
        "rating": 3,
        "tasting": {
            "profile": {
                "sweetDry": 60,
                "heavyLight": 40,
                "richCalm": 50,
                "boldSmooth": 50,
            },
            "aroma": "更新香り",
            "taste": "更新味わい",
            "finish": "更新余韻",
            "temperature": "常温 15°C",
        },
    }
    res = client.put("/api/v1/journal/1", json=updated)
    assert res.status_code == 200
    data = res.json()
    assert data["sakeName"] == "更新された酒"
    assert data["id"] == "1"


def test_delete_journal_entry(client):
    res = client.delete("/api/v1/journal/2")
    assert res.status_code == 204
    res2 = client.get("/api/v1/journal/2")
    assert res2.status_code == 404
