#! /usr/bin/python3
# -*- coding: utf-8 -*-

__author__ = 'Dieter Vansteenwegen'
__email__ = 'dieter.vansteenwegen@vliz.be'
__project__ = 'Panthyr'
__project_link__ = 'https://waterhypernet.org/equipment/'
import logging
import logging.handlers
import datetime as dt
import os
from typing import Union

LOG_FMT = '%(asctime)s|%(levelname)-7.7s|%(module)-15.15s|%(lineno)-0.3d|%(funcName)s|%(message)s'
# See https://docs.python.org/3/library/datetime.html#strftime-and-strptime-format-codes
DATE_FMT = '%d/%m/%Y %H:%M:%S'
LOGFILE = '/home/panthyr/data/logs/panthyr_log.log'
LOGMAXBYTES = 500000


class MilliSecondsFormatter(logging.Formatter):

    def formatTime(self, record: logging.LogRecord, datefmt: Union[str, None] = None) -> str:
        # sourcery skip: lift-return-into-if, remove-unnecessary-else
        creation_time = dt.datetime.fromtimestamp(record.created)
        if datefmt:
            s = creation_time.strftime(datefmt)
        else:
            t = creation_time.strftime(DATE_FMT)
            s = f'{t}.{int(record.msecs)}'
        return s


def setup_logger(name: Union[str, None] = None) -> logging.Logger:
    """Setup logging.

    Returns logger object with (at least) 1 streamhandler to stdout.
    Base logger level is set to logging.DEBUG
    Streamhandler level is set to logging.ERROR
    Uses the MilliSecondsFormatter to add milliseconds to the timestamp.

    Args:
        name (Union[str, None], optional): Name of the logger. None to get the root logger.
                Defaults to None.

    Returns:
        logging.Logger: configured logger object with streamhandler
    """

    logger = logging.getLogger() if name is None else logging.getLogger(name)
    logger.setLevel(logging.DEBUG)

    stream_handler = logging.StreamHandler()  # handler to stdout
    stream_handler.setLevel(logging.ERROR)
    stream_handler.setFormatter(MilliSecondsFormatter(LOG_FMT))
    logger.addHandler(stream_handler)
    return logger


def add_rotating_file_handler(logger: logging.Logger) -> None:
    """Add a rotating file handler to the logger.

    Uses LOGFILE constant for the base file name and LOGMAXBYTES for the rollover size.
    Handler level is set to logging.DEBUG.

    Args:
        logger (logging.Logger): Logger to add the handler to.
    """
    log_dir = os.path.dirname(LOGFILE)
    if not os.path.isdir(log_dir):
        os.makedirs(log_dir)
    rot_file_handler = logging.handlers.RotatingFileHandler(
        LOGFILE,
        maxBytes=LOGMAXBYTES,
        backupCount=3,
    )
    rot_file_handler.doRollover()
    rot_file_handler.setLevel(logging.DEBUG)
    rot_file_handler.setFormatter(MilliSecondsFormatter(LOG_FMT))
    logger.addHandler(rot_file_handler)


def add_email_handler(logger: logging.Logger, db) -> None:
    """Adds and configures email handler.

    Adds the buffered_SMTP_Handler to the logger.
    Gets (login) credentials and server from the credentials module, recipient from the database.
    Handler level is set to logging.WARNING

    Args:
        log (logging.Logger): logger object to add handler to
        db (_type_): Panthyr database

    """
    from .p_handlers import buffered_SMTP_Handler
    try:
        from panthyr_credentials.p_credentials import pCredentials
        cred = pCredentials()
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
        h2.setFormatter(MilliSecondsFormatter(LOG_FMT))
        logger.addHandler(h2)
    except Exception:
        logger.exception('Could not add email handler.')


def add_database_handler(logger: logging.Logger, db) -> None:
    """Adds and configures database handler.

    Adds the database logs table to the logger output.
    Gets (login) credentials and server from the credentials module, recipient from the database.
    Handler level is set to logging.WARNING

    Args:
        log (logging.Logger): logger object to add handler to
        db (_type_): Panthyr database

    Returns:
        logging.Logger: logger with added email handler
    """
    from .p_handlers import db_Handler
    h3 = db_Handler(db)
    h3.setLevel(logging.DEBUG)
    h3.setFormatter(MilliSecondsFormatter(LOG_FMT))
    logger.addHandler(h3)
