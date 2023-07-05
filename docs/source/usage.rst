===============================
Panthyr Logging example code
===============================

Example code:

.. code:: python

    >>> import panthyr_logging.p_logging
    # get the root logger (don't supply module name)
    >>> log = panthyr_logging.p_logging.setup_logger()
    # add the rotating file handler
    >>> panthyr_logging.p_logging.add_rotating_file_handler(log)

    # create database object for next handlers:
    >>> from panthyr_db.p_db import pDB
    >>> db = pDB('/home/panthyr/data/panthyr.db')

    # add the email handler (after instantiating the panthyr database as db)
    >>> panthyr_logging.p_logging.add_email_handler(log, db)
    # add the database handler (after instanciating the panthyr database as db)
    >>> panthyr_logging.p_logging.add_database_handler(log, db)
