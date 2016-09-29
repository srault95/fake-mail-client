# -*- coding: utf-8 -*-

import asyncore
import threading
import socket
from smtpd import SMTPServer
from email import message_from_string

from fake_mail_client.message import FAKE_HEADER

def get_free_port():
    tempsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    tempsock.bind(('localhost', 0))
    host, unused_port = tempsock.getsockname()
    tempsock.close()
    return host, unused_port

class FakeSMTPServer(SMTPServer):
    
    def __init__(self, *args, **kwargs):
        SMTPServer.__init__(self, *args, **kwargs)
        #TODO: lock self._messages?
        self._messages = []
    
    def process_message(self, peer, mailfrom, rcpttos, data):
        msg = message_from_string(data)
        value = {
            "id": msg[FAKE_HEADER],
            "peer": peer,
            "mailfrom": mailfrom,
            "rcpttos": rcpttos,
            "data": data,
        }
        self._messages.append(value)
        #OK QUEUE[41a9f1882d449d3c452859949a71a0a23b7ee8afc2aa39cc3a9c7b52a782e528]
        return '250 OK QUEUE[%s]' % value['id']


class AsyncorePoller(threading.Thread):
    """
    @see: https://austinhartzheim.me/blog/0/python-unit-tests-asyncore/
    """

    def __init__(self):
        super().__init__()
        self.continue_running = True

    def run(self):
        while self.continue_running:
            asyncore.poll()

    def stop(self):
        self.continue_running = False
