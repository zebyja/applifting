import numpy as np
from flask_sqlalchemy import SQLAlchemy
from multiprocessing import Process
from time import sleep

from ms.dbModels import Product, Offer
from ms.offersConnector import OffersConnector


PRICE = 'price'
ITEMS_IN_STOCK = 'items_in_stock'
ID = 'id'


class OffersSyncJob:

    offersMS = None
    db = None
    process = None

    @staticmethod
    def start(offers_ms: OffersConnector, db: SQLAlchemy):
        OffersSyncJob.offersMS = offers_ms
        OffersSyncJob.db = db
        OffersSyncJob.process = Process(target=OffersSyncJob.offers_sync)
        OffersSyncJob.process.start()

    @staticmethod
    def offers_sync():
        while True:
            products = Product.query.all()
            for product in products:
                offers = OffersSyncJob.offersMS.product_offers(product.id)
                offers = OffersSyncJob.merge_with_local_offers(prod_id=product.id, remote_offers=offers)
                for offer in offers:
                    # add new offers to local DB
                    db_offer = Offer(prod_id=product.id, price=offer[PRICE], items_in_stock=offer[ITEMS_IN_STOCK],
                                     remote_id=offer[ID])
                    OffersSyncJob.db.session.add(db_offer)
            OffersSyncJob.db.session.commit()

            sleep(60.)

    @staticmethod
    def offer_validation(offer: dict):
        if PRICE in offer and ITEMS_IN_STOCK in offer and ID in offer:
            return True
        return False

    @staticmethod
    def merge_with_local_offers(prod_id: int, remote_offers: list):
        local_offers = OffersSyncJob.db.session.query(Offer).filter_by(prod_id=prod_id)
        ret = []
        for offer in local_offers:
            ret.append(offer.remote_id)
        ret.sort()

        i = 0
        while i < len(remote_offers):
            offer = remote_offers[i]

            # skip invalid offers
            if not OffersSyncJob.offer_validation(offer):
                remote_offers = np.delete(remote_offers, i)
                continue  # Remote offers is invalid

            # skip synchronized offers
            j = np.searchsorted(ret, offer[ID])
            if j >= len(ret):
                i += 1
                continue  # Remote offers wasn't found in DB -> add them

            remote_offers = np.delete(remote_offers, i)
            ret = np.delete(ret, j)

        return remote_offers
