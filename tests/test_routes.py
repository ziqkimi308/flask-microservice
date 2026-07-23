import pytest
from app import create_app
from app.database import db as _db

"""
- @pytest.fixture are functions that provide a fixed baseline.
- @pytest.fixture with scope='session' means they persist. Does not tear down, or reinitialize.
- So in this case, db(app) is reinitialized and the next test is run every time while app() remains.
"""

@pytest.fixture(scope="session")
def app():
    test_app = create_app(test_config={
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
        "TESTING": True
    })
    return test_app

@pytest.fixture(scope="session")
def db(app):
    with app.app_context():
        _db.create_all()
        yield _db
        _db.drop_all()

@pytest.fixture
def client(app, db):
    with app.test_client() as client:
        yield client

def test_index_returns_200(client):
    response = client.get("/")
    assert response.status_code == 200
    data = response.get_json()
    assert data["service"] == "flask-microservice"

def test_health_returns_200(client):
    response = client.get("/health")
    assert response.status_code == 200
    data = response.get_json()
    assert data["status"] == "ok"
    assert data["db"] == "ok"

def test_get_items_empty(client):
    response = client.get("/items")
    assert response.status_code == 200
    data = response.get_json()
    assert data["items"] == []
    assert data["count"] == 0

def test_create_item(client):
    payload = {"name": "Test Item", "description": "A test description"}
    response = client.post("/items", json=payload)
    assert response.status_code == 201
    data = response.get_json()
    assert data["name"] == "Test Item"
    assert data["description"] == "A test description"
    assert "id" in data

def test_create_item_missing_name(client):
    response = client.post("/items", json={"description": "no name"})
    assert response.status_code == 400

def test_create_item_name_too_long(client):
    response = client.post("/items", json={"name": "x" * 101})
    assert response.status_code == 400

def test_get_item_by_id(client):
    create = client.post("/items", json={"name": "Fetch Me"})
    item_id = create.get_json()["id"]
    response = client.get(f"/items/{item_id}")
    assert response.status_code == 200
    assert response.get_json()["name"] == "Fetch Me"

def test_get_item_not_found(client):
    response = client.get("/items/99999")
    assert response.status_code == 404

def test_delete_item(client):
    create = client.post("/items", json={"name": "Delete Me"})
    item_id = create.get_json()["id"]
    response = client.delete(f"/items/{item_id}")
    assert response.status_code == 200
    fetch = client.get(f"/items/{item_id}")
    assert fetch.status_code == 404