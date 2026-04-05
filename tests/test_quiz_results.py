def test_get_result_shrb(client):
    res = client.get("/api/v1/quiz-results/SHRB")
    assert res.status_code == 200
    data = res.json()
    assert len(data["sakes"]) == 3
    assert len(data["pairings"]) == 3
    assert "pairingSectionTitle" in data


def test_get_result_fallback(client):
    res = client.get("/api/v1/quiz-results/XXXX")
    assert res.status_code == 200
    data = res.json()
    assert len(data["sakes"]) == 3  # falls back to SHRB
