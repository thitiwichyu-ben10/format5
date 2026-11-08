from fastapi.testclient import TestClient
from app.api import app
client = TestClient(app)
def test_health():
    r=client.get("/health")
    assert r.status_code == 200 and r.json() == {"status":"ok"}
def test_invalid_generate():
    r=client.post("/generate", json={"invalid":True})
    assert r.status_code == 422
