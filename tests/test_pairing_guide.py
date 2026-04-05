def test_get_categories(client):
    res = client.get("/api/v1/pairing-guide/categories")
    assert res.status_code == 200
    data = res.json()
    assert len(data) == 3
    assert data[0]["slug"] == "grilled"
    assert len(data[0]["items"]) == 3


def test_get_item_by_id(client):
    res = client.get("/api/v1/pairing-guide/items/grilled-1")
    assert res.status_code == 200
    data = res.json()
    assert data["id"] == "grilled-1"
    assert "foodName" in data


def test_get_item_not_found(client):
    res = client.get("/api/v1/pairing-guide/items/nonexistent")
    assert res.status_code == 404


def test_season_filters(client):
    res = client.get("/api/v1/pairing-guide/filters/season")
    assert res.status_code == 200
    data = res.json()
    assert len(data) >= 3


def test_food_filters(client):
    res = client.get("/api/v1/pairing-guide/filters/food")
    assert res.status_code == 200
    data = res.json()
    assert len(data) == 3
