import os

os.environ["DATABASE_URL"] = "sqlite:///./test.db"
if os.path.exists("test.db"):
    os.remove("test.db")

from fastapi.testclient import TestClient

from app.db.base import Base
from app.db.init_db import init_db
from app.db.session import SessionLocal, engine
from main import app

Base.metadata.create_all(bind=engine)
db = SessionLocal()
try:
    init_db(db)
finally:
    db.close()

client = TestClient(app)


def get_auth_header() -> dict[str, str]:
    response = client.post(
        "/api/v1/auth/token",
        data={"username": "admin", "password": "admin123"},
    )
    assert response.status_code == 200
    token = response.json()["access_token"]

    refresh_response = client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": response.json()["refresh_token"]},
    )
    assert refresh_response.status_code == 200

    return {"Authorization": f"Bearer {token}"}


def test_health() -> None:
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_request_id_header_is_set() -> None:
    response = client.get("/health")
    assert response.status_code == 200
    assert "X-Request-ID" in response.headers


def test_health_dependencies() -> None:
    response = client.get("/health/dependencies")
    assert response.status_code in (200, 503)
    body = response.json()
    assert "dependencies" in body
    assert "redis" in body["dependencies"]
    assert "rabbitmq" in body["dependencies"]
    assert isinstance(body["dependencies"]["redis"]["ready"], bool)
    assert isinstance(body["dependencies"]["rabbitmq"]["ready"], bool)


def test_metrics_endpoint() -> None:
    response = client.get("/metrics")
    assert response.status_code == 200
    assert "http_requests_total" in response.text


def test_category_crud_flow() -> None:
    headers = get_auth_header()

    create_response = client.post(
        "/api/v1/categories",
        headers=headers,
        json={"name": "Electronics", "description": "Devices and gadgets"},
    )
    assert create_response.status_code == 201
    category_id = create_response.json()["id"]

    list_response = client.get(
        "/api/v1/categories?search=Elect&page=1&size=10",
        headers=headers,
    )
    assert list_response.status_code == 200
    assert list_response.json()["total"] >= 1

    update_response = client.put(
        f"/api/v1/categories/{category_id}",
        headers=headers,
        json={"name": "Electronics and Gadgets"},
    )
    assert update_response.status_code == 200
    assert update_response.json()["name"] == "Electronics and Gadgets"

    delete_response = client.delete(f"/api/v1/categories/{category_id}", headers=headers)
    assert delete_response.status_code == 204