import pytest
from app import create_app
from app.database import db as _db
from app.models import Item

@pytest.fixture(scope="module")
def app():
    test_app = create_app(test_config={
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
        "TESTING": True})
    return test_app

@pytest.fixture(scope="module")
def db(app):
    with app.app_context():
        _db.create_all()
        yield _db
        _db.drop_all()

def test_item_to_dict(db, app):
    with app.app_context():
        item = Item(name="Model Test", description="Testing the model")
        _db.session.add(item)
        _db.session.commit()
        result = item.to_dict()
        assert result["name"] == "Model Test"
        assert result["description"] == "Testing the model"
        assert "id" in result
        assert "created_at" in result