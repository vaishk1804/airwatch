from fastapi.testclient import TestClient
from app.main import app

client= TestClient(app)

def test_healthz():
  r= client.get("/healthz")
  assert r.status_code== 200
  assert r.json().get('status') =="ok"

def test_readyz_returns_json():
  r = client.get("/readyz")
  assert r.status_code == 200
  assert "status" in r.json()
  assert "db" in r.json()