def test_list_articles(client):
    res = client.get("/api/v1/articles")
    assert res.status_code == 200
    data = res.json()
    assert "items" in data
    assert len(data["items"]) == 5
    assert "body" not in data["items"][0]
    assert "slug" in data["items"][0]
    assert "title" in data["items"][0]
    assert "filters" in data
    assert len(data["filters"]["categories"]) == 4
    assert data["page"] == 1
    assert data["total"] == 5


def test_list_articles_filter_by_category(client):
    res = client.get("/api/v1/articles?category=brewery")
    assert res.status_code == 200
    data = res.json()
    assert all(a["category"] == "brewery" for a in data["items"])
    assert data["total"] == 2


def test_get_article_by_slug(client):
    res = client.get("/api/v1/articles/kubota-brewery-story")
    assert res.status_code == 200
    data = res.json()
    assert data["slug"] == "kubota-brewery-story"
    assert "body" in data
    assert len(data["body"]) > 0


def test_get_article_not_found(client):
    res = client.get("/api/v1/articles/nonexistent")
    assert res.status_code == 404
