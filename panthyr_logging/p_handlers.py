#! /usr/bin/python3
# -*- coding: utf-8 -*-

__author__ = 'Dieter Vansteenwegen'
__email__ = 'dieter.vansteenwegen@vliz.be'
__project__ = 'Panthyr'
__project_link__ = 'https://waterhypernet.org/equipment/'

import logging
import logging.handlers

try:
    from panthyr_email.p_email import pEmail
except ImportError:
    pEmail = None


class buffered_SMTP_Handler(logging.handlers.BufferingHandler):
    def __init__(
        self,
        host: str,
        password: str,
        fromaddress: str,
        toaddress: str,
        station_id: str,
    ):
        """Set up the email handler.

        Args:
            host (str): server hostname
            password (str): email password
            fromaddress (str): sender address
            toaddress (str): recipient address
            station_id (str): identifier for the Panthyr station, used in header
        """
        logging.handlers.BufferingHandler.__init__(self, 1)
        self.server, self.port = host.split(':')
        self.password = password
        self.fromaddress = fromaddress
        self.toaddress = (toaddress.replace(' ', '').replace(';', ',')).split(',')
        self.station_id = station_id
        # strip spaces from toaddress, then put different recipients in list
        self.subject = f'[{self.station_id.upper()}] Error log sent by PANTHYR'

    def flush(self) -> None:
        """Send email with log messages.

        Get all CRITICAL logs from the logging buffer and add them to the email body.
        Send the email to recipient.
        """
        if len(self.buffer) == 0 or not pEmail:
            return

        mailheader: str = (
            f'From: {self.fromaddress}\r\nTo: {", ".join(self.toaddress)}\r\n'
            f'Subject: {self.subject}\r\n\r\n'
        )
        mailbody = ''
        for log in self.buffer:
            mailbody += '*' * 40 + '\r\n'
            log_str = self.format(log)
            log_str = '\r\n'.join(
                [line for line in log_str.split('\r\n') if line != ''],
            )
            mailbody += f'{log_str}\r\n'

        mail = pEmail(
            server=self.server,
            username=self.fromaddress,
            password=self.password,
            port=int(self.port),
        )
        print(f'{mailbody=}')
        mail.create_email(
            to=self.toaddress,
            subject='subject',
            # subject=mailheader,
            text=mailbody,
            station_id=self.station_id,
        )
        mail.send()

        # try:
        #     connection = smtplib.SMTP(host=self.host, timeout=10)
        # except socket.gaierror as e:
        #     print(f"ERROR: Could not resolve name: {e}")
        #     # TODO: empty log handler buffer? Flush?
        #     return

        # connection.starttls()

        # try:
        #     connection.login(self.fromaddress, self.password)
        # except smtplib.SMTPAuthenticationError:
        #     pass
        # else:
        #     connection.sendmail(self.fromaddress, self.toaddress, mailheader + mailbody)
        #     connection.quit()
        # finally:
        #     super(
        #         buffered_SMTP_Handler,
        #         self,
        #     ).flush()  # And do the normal email as default as well
        super(
            buffered_SMTP_Handler,
            self,
        ).flush()  # And do the normal email as default as well


class db_Handler(logging.Handler):
    def __init__(self, db):
        """Add a handler to add logs to the database.

        Args:
            db (_type_): Panthyr database to add logs to. Requires add_log method.
        """
        logging.Handler.__init__(self)
        self.db = db

    def emit(self, record: logging.LogRecord):
        """Add records to database.

        Args:
            record (logging.LogRecord): logging record to add to db.
        """
        db_level = record.levelname  # log level
        db_source = f'{record.module}.{record.funcName}({record.lineno})'
        db_log = record.msg  # the log text
        if (
            record.exc_info
        ):  # an exception was thrown, log additional data such as traceback
            clean_tb = self._cleaned_traceback(record)
            db_log = f'EXCEPTION:{db_log}, TYPE/VALUE:{record.exc_info[1]}, TRACEBACK:{clean_tb}'

        self.db.add_log(db_log, db_source, db_level)

    def _cleaned_traceback(self, record: logging.LogRecord) -> str:
        """Get the traceback and clean it up.

        Get the traceback from the logging record and clean it up:
            - remove the ' File' at the beginning
            - replace double spaces with single spaces
            - replace the '/home/panthyr/repos' path with '.'
            - remove whitespace after a newline

        Args:
            record (logging.LogRecord): logrecord to extract from

        Returns:
            str: cleaned up traceback
        """
        import traceback

        tb = traceback.format_list(
            traceback.extract_tb(record.exc_info[2]),
        )  # get the traceback as string
        tb = tb[0][7:-1].replace(
            '/home/panthyr/repos',
            '.',
        )  # shorten pad + get rid of ' File' and newline at the end
        tb = tb.replace('  ', ' ')  # remove double spaces
        tb = tb.replace('\n  ', '\n')  # remove whitespace after newline
        return tb
