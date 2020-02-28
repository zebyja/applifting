import pytest

from ms import create_app
from ms import init_all
from ms import db
from ms.dbModels import Product


@pytest.fixture
def app():
    app = create_app({'TESTING': True, 'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:'})

    with app.app_context():
        db.session.add_all(
            (
                Product(name='fixed', description='description of fixed product.'),
                Product(name='to_delete', description='product to delete.')
            )
        )
        init_all(without_job=True)
        db.session.commit()

    yield app


@pytest.fixture
def fixed_product_id(app):
    with app.app_context():
        return Product.query.filter_by(name='fixed').first().id


@pytest.fixture
def to_delete_product_id(app):
    with app.app_context():
        return Product.query.filter_by(name='to_delete').first().id


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def runner(app):
    return app.test_cli_runner()
