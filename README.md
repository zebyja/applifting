# Applifting

Install
-------

Python version: 3.7.6

Necessary libs:
Flask
flask_sqlalchemy
click
numpy
requests
typing

Libs for development
pytest
coverage (python3.7-gdbm needed)

Install ms:

.. code-block:: text

    $ pip install -e .

Run
---

.. code-block:: text

    $ export FLASK_APP=ms
    $ flask init-all
    $ flask run

Or on Windows cmd:

.. code-block:: text

    > set FLASK_APP=flaskr
    > flask init-all
    > flask run

Open http://127.0.0.1:5000 in a browser.


Test
----

.. code-block:: text

    $ pip install -e '.[test]'
    $ pytest

Run with coverage report:

.. code-block:: text

    $ coverage run -m pytest
    $ coverage report
    $ coverage html  # open htmlcov/index.html in a browser
