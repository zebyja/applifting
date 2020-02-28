import os

import click
from flask import Flask
from flask.cli import with_appcontext
from flask_sqlalchemy import SQLAlchemy
from logging.config import dictConfig

from ms.offersConnector import OffersConnector

__version__ = (1, 0, 0, "dev")

db = SQLAlchemy()
logger = None

RESET = os.getenv('RESET_DB') is not None


def create_app(test_config=None):
    if test_config is not None:  # logger to stdout in case of testing
        dictConfig({
            'version': 1,
            'formatters': {'default': {
                'format': '[%(asctime)s] %(levelname)s in %(module)s: %(message)s',
            }},
            'handlers': {'wsgi': {
                'class': 'logging.StreamHandler',
                'stream': 'sys.stdout',
                'formatter': 'default'
            }},
            'root': {
                'level': 'INFO',
                'handlers': ['wsgi']
            }
        })

    app = Flask(__name__, instance_relative_config=True)

    global logger
    logger = app.logger

    # use sqlite if DATABASE_URL is not defined
    db_uri = os.getenv('DATABASE_URL') or 'sqlite:///' + os.path.join(app.instance_path, 'ms.db')

    app.config.from_mapping(
        SQLALCHEMY_DATABASE_URI=db_uri,
        SQLALCHEMY_TRACK_MODIFICATIONS=False  # doesn't need
    )

    if test_config is not None:
        app.config.update(test_config)

    try:
        os.makedirs(app.instance_path, exist_ok=True)
    except OSError:
        pass

    db.init_app(app)
    app.cli.add_command(init_all_command)

    from ms import interface

    app.register_blueprint(interface.interface_blueprint)

    return app


def init_all(without_job: bool = False):
    if RESET:
        db.drop_all()
        logger.info('Database reset. All data removed.')
    db.create_all()
    logger.info('Database initialized.')

    global offersMS
    offersMS = offersConnector.OffersConnector(load_token, save_token)
    logger.info('OffersConnector initialized.')

    from ms.core import Core
    Core.init(db, offersMS)
    logger.info('Core initialized.')

    if not without_job:  # Job is not necessary during api testing.
        from ms.OffersSyncJob import OffersSyncJob
        OffersSyncJob.start(offersMS, db)
        logger.info('offers ms job started.')


@click.command('init-all')
@with_appcontext
def init_all_command():
    init_all()


# db must be initialized, so I run load/save token later
def load_token() -> str:
    from ms.dbModels import Settings
    token = Settings.query.get('access_token')
    return token


def save_token(token: str) -> None:
    from ms.dbModels import Settings
    db.session.add(Settings(name='access_token', value=token))
    db.session.commit()
    logger.info('New access token for offers ms was received.')
