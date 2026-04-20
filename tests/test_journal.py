SAMPLE_ENTRY = {
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


def test_list_journal_requires_auth(client):
    assert client.get("/api/v1/journal").status_code == 401


def test_list_journal_empty_for_new_user(authed_client):
    res = authed_client.get("/api/v1/journal")
    assert res.status_code == 200
    data = res.json()
    assert data["items"] == []
    assert data["total"] == 0


def test_create_and_get_journal_entry(authed_client):
    created = authed_client.post("/api/v1/journal", json=SAMPLE_ENTRY)
    assert created.status_code == 201
    entry_id = created.json()["id"]

    got = authed_client.get(f"/api/v1/journal/{entry_id}")
    assert got.status_code == 200
    data = got.json()
    assert data["sakeName"] == "テスト酒"
    assert data["tasting"]["profile"]["sweetDry"] == 50


def test_get_journal_not_found(authed_client):
    res = authed_client.get("/api/v1/journal/nonexistent")
    assert res.status_code == 404


def test_update_journal_entry(authed_client):
    created = authed_client.post("/api/v1/journal", json=SAMPLE_ENTRY).json()
    updated = {**SAMPLE_ENTRY, "sakeName": "更新された酒", "rating": 3}
    res = authed_client.put(f"/api/v1/journal/{created['id']}", json=updated)
    assert res.status_code == 200
    assert res.json()["sakeName"] == "更新された酒"
    assert res.json()["rating"] == 3


def test_delete_journal_entry(authed_client):
    created = authed_client.post("/api/v1/journal", json=SAMPLE_ENTRY).json()
    assert authed_client.delete(f"/api/v1/journal/{created['id']}").status_code == 204
    assert authed_client.get(f"/api/v1/journal/{created['id']}").status_code == 404


def test_journal_scope_is_per_user(client):
    import uuid as _uuid

    def signup(suffix: str):
        c = type(client)(client.app)
        r = c.post(
            "/api/v1/auth/signup",
            json={
                "email": f"scope-{suffix}@example.com",
                "username": f"scope-{suffix}",
                "password": "testpass123",
            },
        )
        assert r.status_code == 201
        return c

    alice = signup(f"a-{_uuid.uuid4().hex[:6]}")
    bob = signup(f"b-{_uuid.uuid4().hex[:6]}")

    created = alice.post("/api/v1/journal", json=SAMPLE_ENTRY).json()
    assert bob.get(f"/api/v1/journal/{created['id']}").status_code == 404
    assert bob.get("/api/v1/journal").json()["total"] == 0
