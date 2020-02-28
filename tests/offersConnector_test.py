# tests of offersConnector.py
import pytest

from ms import offersConnector


def test_simple():
    try:
        offers = offersConnector.OffersConnector()
        offers.auth()
    except Exception as e:
        assert True, 'Authentication raised exception: \n{}'.format(e)
        return  # cannot continue without authentication.

    # check token
    assert offers.access_token is not None, 'Token is None.'

    # register product
    try:
        offers.product_register(1, 'test', 'test description')
    except Exception as e:
        assert True, 'Product registration raised exception: \n{}'.format(e)
        return  # cannot continue without registered product.

    # get offers
    try:
        ret = offers.product_offers(1)
    except Exception as e:
        assert True, 'Getting product''s offers raised exception: \n{}'.format(e)
        return  # cannot continue without offers returned.

    # get offers of not existed product
    while True:
        try:
            ret = offers.product_offers(2)
        except offersConnector.OffersConnector.ENotFound:
            break  # valid state
        except Exception as e:
            assert True, 'During getting offers of not existed product was raised unexpected Exception:\n{}'.format(e)
        assert True, 'During getting offers of not existed product wasn''t raised NotFound Exception.'
        break

