def test_dashboard(client):
    res = client.get("/")
    assert res.status_code == 200


def test_post_analysis(client):
    res = client.post(
        "/api/analysis",
        json={"input": "x", "result": "y"},
    )
    assert res.status_code == 201


def test_get_analysis(client):
    res = client.get("/api/analysis")
    assert res.status_code == 200