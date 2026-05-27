"""
Integration tests for the locations and subscriptions API routes.

We point DATABASE_URL at a SQLite file (set in conftest.py) and create all
tables on the live app engine before tests run. This lets us test the real
route handlers without needing Postgres in CI.

Note: the upsert path in `subscribe()` uses Postgres-only dialect features,
so we exercise the GET endpoints and the DB unique constraint here, not
the POST.
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.db.base import Base
from app.db.session import engine
from app.main import app
from app.models.location import Location
from app.models.subscription import Subscription


@pytest.fixture(scope="module", autouse=True)
def _setup_db():
    """Create all tables on the live engine and seed two locations."""
    Base.metadata.create_all(engine)

    with Session(engine) as s:
        # Idempotent seed (in case the file persists between local runs)
        if not s.query(Location).filter_by(name="Boston").first():
            s.add(Location(name="Boston", state="MA", country="US", lat=42.36, lon=-71.06))
        if not s.query(Location).filter_by(name="New York").first():
            s.add(Location(name="New York", state="NY", country="US", lat=40.71, lon=-74.00))
        s.commit()

    yield

    # Cleanup: drop subscriptions added during tests so reruns are clean
    with Session(engine) as s:
        s.query(Subscription).delete()
        s.commit()


client = TestClient(app)


def test_healthz_returns_ok():
    r = client.get("/healthz")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


def test_readyz_reports_db_status():
    r = client.get("/readyz")
    assert r.status_code == 200
    body = r.json()
    assert "db" in body
    assert "status" in body


def test_list_locations_returns_seed_data():
    r = client.get("/locations")
    assert r.status_code == 200
    body = r.json()
    assert isinstance(body, list)
    names = {row["name"] for row in body}
    assert {"Boston", "New York"}.issubset(names)


def test_get_location_by_id_404():
    r = client.get("/locations/99999")
    assert r.status_code == 404


def test_get_location_by_id_returns_row():
    # Find a real id
    with Session(engine) as s:
        boston = s.query(Location).filter_by(name="Boston").first()
        boston_id = boston.id
    r = client.get(f"/locations/{boston_id}")
    assert r.status_code == 200
    body = r.json()
    assert body["name"] == "Boston"
    assert body["state"] == "MA"
    assert body["lat"] == pytest.approx(42.36)


def test_list_subscriptions_returns_empty_for_unknown_email():
    r = client.get("/subscriptions?email=nobody@example.com")
    assert r.status_code == 200
    assert r.json() == []


def test_subscription_uniqueness_constraint():
    """The (email, location_id) unique constraint should prevent duplicates."""
    with Session(engine) as s:
        boston = s.query(Location).filter_by(name="Boston").first()
        s.add(Subscription(email="alice@example.com", location_id=boston.id, threshold=35.0, is_active=1))
        s.commit()

    # A second insert with the same (email, location_id) should fail at the DB
    from sqlalchemy.exc import IntegrityError
    with Session(engine) as s:
        boston = s.query(Location).filter_by(name="Boston").first()
        s.add(Subscription(email="alice@example.com", location_id=boston.id, threshold=50.0, is_active=1))
        with pytest.raises(IntegrityError):
            s.commit()


def test_summary_bad_days_empty_when_no_metrics():
    r = client.get("/summary/bad-days")
    assert r.status_code == 200
    assert r.json() == []
