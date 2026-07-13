def test_health_endpoint_returns_standard_envelope(client):
    response = client.get("/api/v1/health", headers={"X-Correlation-ID": "test-request"})

    assert response.status_code == 200
    body = response.get_json()
    assert body["correlation_id"] == "test-request"
    assert body["errors"] == []
    assert body["data"]["service"] == "eye-care-api"
    assert body["data"]["status"] == "healthy"
    assert body["data"]["version"] == "0.1.0"
    assert body["data"]["timestamp"].endswith("+00:00")


def test_unknown_route_returns_standard_error_envelope(client):
    response = client.get("/api/v1/missing")

    assert response.status_code == 404
    body = response.get_json()
    assert body["data"] is None
    assert body["errors"][0]["code"] == "not_found"
    assert body["correlation_id"]

