#! /usr/bin/python3
# -*- coding: utf-8 -*-

__author__ = 'Dieter Vansteenwegen'
__email__ = 'dieter.vansteenwegen@vliz.be'
__project__ = 'Panthyr'
__project_link__ = 'https://waterhypernet.org/equipment/'
import logging
import logging.handlers

FMT = '%(asctime)s |%(levelname)-7s |%(module)-10.10s|%(lineno)-03s |%(funcName)s |%(message)s'
DATEFMT = '%d/%m/%Y %H:%M:%S'  # defines format for timestamp


def setup_logging(email: bool = False, to_db: bool = True) -> logging.Logger:
    """Setup logging.

    Returns logger object with (at least) 1 streamhandler to stdout.
    Additionally, it will log to the database and/or email for

    Args:
        email (bool, optional): Send email for critical logs (>= warning). Defaults to False.
        to_db (bool, optional): Add logs to database. Defaults to True.

    Returns:
        logging.Logger: configured logger object
    """

    log = logging.getLogger(__name__)  # creates root logger with name of script/module
    log.setLevel(logging.DEBUG)

    h1 = logging.StreamHandler()  # handler to stdout for less important messages
    h1.setLevel(logging.DEBUG)
    h1.setFormatter(logging.Formatter(FMT, DATEFMT))
    log.addHandler(h1)  # add both handlers to the logger

    if to_db or email:
        try:
            from panthyr_db import p_db
            db = p_db()
        except Exception:
            return log
    else:
        db = None

    if to_db:
        from .p_handlers import db_Handler
        h3 = db_Handler(db)
        h3.setLevel(logging.DEBUG)
        log.addHandler(h3)

    if email:
        setup_email(log, db)

    return log


def setup_email(log: logging.Logger, db) -> logging.Logger:
    """Set up the email handler.

    Gets credentials from the credentials module and recipient from the database.

    Args:
        log (logging.Logger): logger object to add handler to
        db (_type_): Panthyr database

    Returns:
        logging.Logger: logger with added email handler
    """
    from .p_handlers import buffered_SMTP_Handler
    try:
        if db.get_setting('email_enabled') == 1:
            from panthyr_credentials import Credentials
            cred = Credentials()
            server_port = cred.get_cred('email_server_port')
            user = cred.get_cred('email_user')
            password = cred.get_cred('email_password')

            station_id = db.get_setting('station_id')
            recipient = db.get_setting('email_recipient')
            h2 = buffered_SMTP_Handler(
                host=server_port,
                fromaddress=user,
                toaddress=recipient,
                password=password,
                station_id=station_id,
            )  # handler for messages that should be emailed
            h2.setLevel(logging.WARNING)
            h2.setFormatter(logging.Formatter(FMT, DATEFMT))
            log.addHandler(h2)
    except Exception:
        return log

    return log
