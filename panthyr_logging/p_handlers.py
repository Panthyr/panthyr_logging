#! /usr/bin/python3
# -*- coding: utf-8 -*-

__author__ = 'Dieter Vansteenwegen'
__email__ = 'dieter.vansteenwegen@vliz.be'
__project__ = 'Panthyr'
__project_link__ = 'https://waterhypernet.org/equipment/'

import logging
import logging.handlers
import smtplib


class buffered_SMTP_Handler(logging.handlers.BufferingHandler):

    def __init__(self, host, password, fromaddress, toaddress, station_id):
        logging.handlers.BufferingHandler.__init__(self, 50)
        self.host = host
        self.port = 587
        self.password = password
        self.fromaddress = fromaddress
        self.toaddress = (toaddress.replace(' ', '').replace(';', ',')).split(',')
        self.station_id = station_id
        # strip spaces from toaddress, then put different recipients in list
        self.subject = f'[{self.station_id.upper()}] Error log send by PANTHYR'

    def flush(self):
        if len(self.buffer) == 0:
            return
        connection = smtplib.SMTP(host=self.host, timeout=10)

        mailheader = 'From: {}\r\nTo: {}\r\nSubject: {}\r\n\r\n'.format(
            self.fromaddress, ','.join(self.toaddress), self.subject,
        )
        mailbody = ''
        criticalbody = ''
        for log in self.buffer:
            mailbody += '{}\r\n'.format(
                self.format(log),
            )  # keep critical log messages in between others as well
            if self.format(log)[:8] == 'CRITICAL':
                criticalbody += '{}\r\n'.format(self.format(log))

        connection.starttls()
        connection.login(self.fromaddress, self.password)
        connection.sendmail(self.fromaddress, self.toaddress, mailheader + mailbody)
        if len(criticalbody) > 0:
            criticalhdr_template = 'From: {}\r\nTo: {}\r\nSubject: CRITICAL PANTHYR LOG\r\n\r\n'
            criticalhdr = criticalhdr_template.format(self.fromaddress, ','.join(self.toaddress))
            connection.sendmail(self.fromaddress, self.toaddress, criticalhdr + criticalbody)
        connection.quit()

        super(buffered_SMTP_Handler, self).flush()
