from flask_sqlalchemy import SQLAlchemy

from ms.dbModels import Product
from ms.offersConnector import OffersConnector
from ms.consts import HTTP_NOT_FOUND, HTTP_BAD_REQUEST
from ms import logger


class Core:
    db = None
    offersMS = None

    class ECore(Exception):
        """ Common Exception for Core class. """

    class EUnexpected(ECore):
        """ Chain Exception for unexpected exceptions. """
        def __init__(self, original_exception: Exception):
            self.msg = 'Exception during request:\n{e}'.format(e=original_exception)
            self.original_exception = original_exception

    class EExcepted(ECore):
        """ Exception for expected exception with status_code """
        def __init__(self, status_code: int):
            self.status_code = status_code

        @staticmethod
        def make_descendant(status_code: int):
            if status_code == HTTP_BAD_REQUEST:
                return Core.EBadRequest(HTTP_BAD_REQUEST)
            elif status_code == HTTP_NOT_FOUND:
                return Core.ENotFound(HTTP_NOT_FOUND)

    class EBadRequest(EExcepted):
        """ Exception for Bad Request response. """
    class ENotFound(EExcepted):
        """ Exception for Not Found response. """

    @staticmethod
    def init(db: SQLAlchemy, offers_ms: OffersConnector):
        Core.db = db
        Core.offersMS = offers_ms

    @staticmethod
    def create_product(name: str, description: str):
        if name is None or description is None:
            raise Core.EExcepted.make_descendant(HTTP_BAD_REQUEST)

        try:
            p = Product(name=name, description=description)
            Core.db.session.add(p)
            Core.db.session.commit()
            Core.offersMS.product_register(p.id, p.name, p.description)
            logger.info('New product registered in offers ms: {}'.format(p))
        except Exception as e:
            raise Core.EUnexpected(e)

    @staticmethod
    def get_product(prod_id: int):
        try:
            p = Product.query.get(prod_id)
        except Exception as e:
            raise Core.EUnexpected(e)

        if p is None:
            raise Core.EExcepted.make_descendant(HTTP_NOT_FOUND)

        return {'id': p.id, 'name': p.name, 'description': p.description}

    @staticmethod
    def update_product(prod_id: int, name: str = None, description: str = None):
        if name is None and description is None:
            raise Core.EExcepted.make_descendant(HTTP_BAD_REQUEST)

        try:
            p = Product.query.get(prod_id)
        except Exception as e:
            raise Core.EUnexpected(e)

        if p is None:
            raise Core.EExcepted.make_descendant(HTTP_NOT_FOUND)

        if name is not None:
            p.name = name
        if description is not None:
            p.description = description

        try:
            Core.db.session.commit()
            # Cannot update in offers service due to missing documentation
        except Exception as e:
            raise Core.EUnexpected(e)

    @staticmethod
    def delete_product(prod_id: int):
        try:
            p = Product.query.get(prod_id)
        except Exception as e:
            raise Core.EUnexpected(e)

        if p is None:
            raise Core.EExcepted.make_descendant(HTTP_NOT_FOUND)

        try:
            Core.db.session.delete(p)
            Core.db.session.commit()
            # Cannot delete from offers service due to missing documentation.
            logger.info('Product was deleted: {}'.format(p))
        except Exception as e:
            raise Core.EUnexpected(e)
