def test_list_sake(client):
    res = client.get("/api/v1/sake")
    assert res.status_code == 200
    data = res.json()
    assert "items" in data
    assert len(data["items"]) >= 9
    assert "id" in data["items"][0]
    assert "name" in data["items"][0]
    assert data["page"] == 1


def test_get_sake_detail(client):
    res = client.get("/api/v1/sake/dassai-45")
    assert res.status_code == 200
    data = res.json()
    assert data["id"] == "dassai-45"
    assert "flavorTags" in data
    assert "pairings" in data


def test_get_sake_not_found(client):
    res = client.get("/api/v1/sake/nonexistent")
    assert res.status_code == 404
