import pytest

from app import create_app
from app.extensions import db


@pytest.fixture()
def app():
    application = create_app("testing")
    with application.app_context():
        db.create_all()
    yield application
    with application.app_context():
        db.session.remove()
        db.drop_all()
        db.engine.dispose()


@pytest.fixture()
def client(app):
    return app.test_client()


@pytest.fixture()
def csrf_header(client):
    def build(cookie_name: str = "csrf_access_token") -> dict[str, str]:
        cookie = client.get_cookie(cookie_name)
        assert cookie is not None
        return {"X-CSRF-TOKEN": cookie.value}

    return build
