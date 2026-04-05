def test_list_articles(client):
    res = client.get("/api/v1/articles")
    assert res.status_code == 200
    data = res.json()
    assert len(data) == 5
    assert "body" not in data[0]
    assert "slug" in data[0]
    assert "title" in data[0]


def test_article_filters(client):
    res = client.get("/api/v1/articles/filters")
    assert res.status_code == 200
    data = res.json()
    assert len(data) == 4
    assert data[0]["key"] == "all"


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
