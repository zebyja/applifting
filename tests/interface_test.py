import pytest

from flask import g, session

from ms.dbModels import Product

from ms.consts import PRODUCT_NAME, PRODUCT_DESCRIPTION, HTTP_OK, HTTP_CREATED, HTTP_BAD_REQUEST, HTTP_NOT_FOUND


def test_product_register_ok(client, app):
    response = client.post('/product', json={PRODUCT_NAME: 'test', PRODUCT_DESCRIPTION: 'test description'})
    assert response.status_code == HTTP_CREATED

    with app.app_context():
        assert Product.query.filter_by(name='test').first() is not None


def test_product_register_bad_request(client, app):
    response = client.post('/product', json={})
    assert response.status_code == HTTP_BAD_REQUEST


def test_product_read_ok(client, fixed_product_id):
    response = client.get('/product/{}'.format(fixed_product_id))
    assert response.status_code == HTTP_OK


def test_product_read_not_found(client):
    response = client.get('/product/{}'.format(9999))
    assert response.status_code == HTTP_NOT_FOUND


@pytest.mark.parametrize(
    ('data', 'status_code'),
    (
        ({}, HTTP_BAD_REQUEST),
        ({PRODUCT_NAME: "renamed"}, HTTP_OK),
        ({PRODUCT_NAME: "edited description"}, HTTP_OK),
        ({PRODUCT_NAME: "fixed", PRODUCT_DESCRIPTION: "edited description"}, HTTP_OK)
    )
)
def test_product_update(client, fixed_product_id, data, status_code):
    response = client.post('/product/{}'.format(fixed_product_id), json=data)
    assert response.status_code == status_code


def test_product_update_not_found(client):
    response = client.post('product/{}'.format(9999), json={PRODUCT_NAME: 'fixed', PRODUCT_DESCRIPTION: 'description'})
    assert response.status_code == HTTP_NOT_FOUND


def test_product_delete(client, to_delete_product_id):
    response = client.delete('product/{}'.format(to_delete_product_id))
    assert response.status_code == HTTP_OK


def test_product_delete_not_found(client):
    response = client.delete('product/{}'.format(9999))
    assert response.status_code == HTTP_NOT_FOUND
