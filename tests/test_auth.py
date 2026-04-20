import uuid


def _unique():
    return uuid.uuid4().hex[:8]


def test_signup_login_me_logout_flow(client):
    tag = _unique()
    body = {
        "email": f"flow-{tag}@example.com",
        "username": f"flow-{tag}",
        "password": "flowpass123",
    }

    res = client.post("/api/v1/auth/signup", json=body)
    assert res.status_code == 201
    user = res.json()
    assert user["email"] == body["email"]
    assert "hashed_password" not in user

    me = client.get("/api/v1/auth/me")
    assert me.status_code == 200
    assert me.json()["id"] == user["id"]

    assert client.post("/api/v1/auth/logout").status_code == 204
    assert client.get("/api/v1/auth/me").status_code == 401

    login = client.post(
        "/api/v1/auth/login",
        json={"email": body["email"], "password": body["password"]},
    )
    assert login.status_code == 200
    assert client.get("/api/v1/auth/me").status_code == 200


def test_signup_rejects_duplicate_email(client):
    tag = _unique()
    body = {
        "email": f"dup-{tag}@example.com",
        "username": f"dup-{tag}",
        "password": "dupepass123",
    }
    assert client.post("/api/v1/auth/signup", json=body).status_code == 201
    # Different username, same email → conflict
    dup = {**body, "username": f"dup-{tag}-2"}
    assert client.post("/api/v1/auth/signup", json=dup).status_code == 409


def test_login_rejects_wrong_password(client):
    tag = _unique()
    body = {
        "email": f"wrongpw-{tag}@example.com",
        "username": f"wrongpw-{tag}",
        "password": "rightpass1",
    }
    client.post("/api/v1/auth/signup", json=body)
    res = client.post(
        "/api/v1/auth/login",
        json={"email": body["email"], "password": "nope-wrong-pw"},
    )
    assert res.status_code == 401


def test_signup_rejects_short_password(client):
    tag = _unique()
    res = client.post(
        "/api/v1/auth/signup",
        json={
            "email": f"short-{tag}@example.com",
            "username": f"short-{tag}",
            "password": "short",
        },
    )
    assert res.status_code == 422


def test_me_requires_auth(client):
    assert client.get("/api/v1/auth/me").status_code == 401
