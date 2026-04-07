def test_get_pairing_guide(client):
    res = client.get("/api/v1/pairing-guide")
    assert res.status_code == 200
    data = res.json()
    assert "categories" in data
    assert len(data["categories"]) == 3
    assert data["categories"][0]["slug"] == "grilled"
    assert len(data["categories"][0]["items"]) == 3
    # List items should not have detail fields
    assert "body" not in data["categories"][0]["items"][0]
    assert "whyItWorks" not in data["categories"][0]["items"][0]
    assert "howToEnjoy" not in data["categories"][0]["items"][0]
    # Filters should be included
    assert "filters" in data
    assert len(data["filters"]["seasons"]) >= 3
    assert len(data["filters"]["foodCategories"]) == 3


def test_get_item_by_id(client):
    res = client.get("/api/v1/pairing-guide/items/grilled-1")
    assert res.status_code == 200
    data = res.json()
    assert data["id"] == "grilled-1"
    assert "foodName" in data
    # Detail endpoint should include all fields
    assert "body" in data
    assert "whyItWorks" in data
    assert "howToEnjoy" in data


def test_get_item_not_found(client):
    res = client.get("/api/v1/pairing-guide/items/nonexistent")
    assert res.status_code == 404
