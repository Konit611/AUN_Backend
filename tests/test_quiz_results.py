def test_get_result_shrb(client):
    res = client.get("/api/v1/quiz-results/SHRB")
    assert res.status_code == 200
    data = res.json()
    assert len(data["sakes"]) == 3
    assert len(data["pairings"]) == 3
    assert "pairingSectionTitle" in data


def test_get_result_all_codes(client):
    codes = [
        "SHRB", "SHRS", "SHLB", "SHLS",
        "SERB", "SERS", "SELB", "SELS",
        "DHRB", "DHRS", "DHLB", "DHLS",
        "DERB", "DERS", "DELB", "DELS",
    ]
    for code in codes:
        res = client.get(f"/api/v1/quiz-results/{code}")
        assert res.status_code == 200, f"Failed for code {code}"
        data = res.json()
        assert len(data["sakes"]) == 3, f"Wrong sake count for {code}"
        assert len(data["pairings"]) == 3, f"Wrong pairing count for {code}"


def test_get_result_unknown_code(client):
    res = client.get("/api/v1/quiz-results/XXXX")
    assert res.status_code == 404
