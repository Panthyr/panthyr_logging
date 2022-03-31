#! /usr/bin/python3
# -*- coding: utf-8 -*-

__author__ = 'Dieter Vansteenwegen'
__email__ = 'dieter.vansteenwegen@vliz.be'
__project__ = 'Panthyr'
__project_link__ = 'https://waterhypernet.org/equipment/'
import logging
import logging.handlers


def setup_logging(email=False, to_db=True):

    fmt = '%(asctime)s |%(levelname)-7s |%(module)-10.10s|%(lineno)-03s |%(funcName)s |%(message)s'
    datefmt = '%d/%m/%Y %H:%M:%S'  # defines format for timestamp

    log = logging.getLogger(__name__)  # creates root logger with name of script/module
    log.setLevel(logging.DEBUG)

    # create, configure and add streamhandler(s)
    h1 = logging.StreamHandler()  # handler to stdout for less important messages
    h1.setLevel(logging.DEBUG)
    h1.setFormatter(logging.Formatter(fmt, datefmt))
    log.addHandler(h1)  # add both handlers to the logger
    if to_db:
        from panthyr_db import p_db
        from .p_handlers import buffered_SMTP_Handler
        with p_db() as db:
            if email and db.get_setting('email_enabled')[1]:

                email_conf = {'recipient': '', 'server_port': '', 'user': '', 'password': ''}
                for i in email_conf:
                    email_conf[i] = db.get_setting('email_' + i)
                station_id = db.get_setting('station_id')[1]
                h2 = buffered_SMTP_Handler(
                    host=email_conf['server_port'],
                    fromaddress=email_conf['user'],
                    toaddress=email_conf['recipient'],
                    password=email_conf['password'],
                    id=station_id,
                )  # handler for messages that should be emailed
                h2.setLevel(logging.WARNING)
                h2.setFormatter(logging.Formatter(fmt, datefmt))
                log.addHandler(h2)

    return log
