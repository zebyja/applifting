from flask import request, jsonify, Blueprint, current_app
from ms.core import Core
from ms.consts import HTTP_INTERNAL_SERVER_ERROR, HTTP_CREATED, HTTP_OK, PRODUCT_NAME, PRODUCT_DESCRIPTION

interface_blueprint = Blueprint('interface_blueprint', __name__)


@interface_blueprint.route('/product', methods=['POST'])
def product_register():
    name, description = parse_product()

    try:
        Core.create_product(name, description)
    except Core.EExcepted as e:
        return "", e.status_code
    except Core.EUnexpected as e:
        current_app.logger.error(e)
        return "", HTTP_INTERNAL_SERVER_ERROR

    return "", HTTP_CREATED


@interface_blueprint.route('/product/<int:prod_id>', methods=['GET'])
def product_read(prod_id):
    try:
        p = Core.get_product(prod_id)
    except Core.EExcepted as e:
        return "", e.status_code
    except Core.EUnexpected as e:
        current_app.logger.error(e)
        return "", HTTP_INTERNAL_SERVER_ERROR

    return jsonify(p), HTTP_OK


@interface_blueprint.route('/product/<int:prod_id>', methods=['POST'])
def product_update(prod_id):
    name, description = parse_product()

    try:
        Core.update_product(prod_id, name, description)
    except Core.EExcepted as e:
        return "", e.status_code
    except Core.EUnexpected as e:
        current_app.logger.error(e)
        return "", HTTP_INTERNAL_SERVER_ERROR

    return "", HTTP_OK


@interface_blueprint.route('/product/<int:prod_id>', methods=['DELETE'])
def product_delete(prod_id):
    try:
        Core.delete_product(prod_id)
    except Core.EExcepted as e:
        return "", e.status_code
    except Core.EUnexpected as e:
        current_app.logger.error(e)
        return "", HTTP_INTERNAL_SERVER_ERROR

    return "", HTTP_OK


def parse_product():
    json = request.get_json(force=True, silent=True, cache=False)
    if json is None:
        return None, None

    name = json[PRODUCT_NAME] if PRODUCT_NAME in json else None
    description = json[PRODUCT_DESCRIPTION] if PRODUCT_DESCRIPTION in json else None
    return name, description
