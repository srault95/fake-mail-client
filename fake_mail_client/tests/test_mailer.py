# -*- coding: utf-8 -*-

import unittest
from pprint import pprint
import contextlib
from email import message_from_string

from .utils import get_free_port, FakeSMTPServer, AsyncorePoller

from fake_mail_client.mailer import SMTPClient
from fake_mail_client.message import MessageFaker

class BaseMailerTestCase(unittest.TestCase):
    
    def setUp(self):
        unittest.TestCase.setUp(self)
        
        self.host, self.port = get_free_port()
        self.server = FakeSMTPServer((self.host, self.port), None)

    def assertMessageInServer(self, msg_id):
        """
        message_from_string
        """
        
    def assertSendResult(self, result):
        self.assertTrue(result["success"], result["error"])
        
        for cmd in ["connect", "ehlo", "mail", "rcpt", "data", "quit"]:
            self.assertTrue(cmd in result)
            
        self.assertEquals(result["connect"]["code"], 220)
        self.assertEquals(result["ehlo"]["code"], 250)
        self.assertEquals(result["mail"]["code"], 250)
        for r in result["rcpt"]:
            self.assertEquals(r["code"], 250)
        self.assertEquals(result["data"]["code"], 250)
        self.assertEquals(result["quit"]["code"], 221)
        
        duration = 0
        for key, field in result.items():
            if key == "rcpt":
                for r in field:
                    duration += r['duration']
            elif isinstance(field, dict) and 'duration' in field:
                duration += field['duration']
        
        self.assertEquals(duration, result["duration"])

    @contextlib.contextmanager
    def start_server(self):
        try:
            self.async_poller = AsyncorePoller()
            self.async_poller.start()
            yield self.server
        except Exception as err:
            raise
        finally:
            self.server.close()
            self.async_poller.stop()

class MailerTestCase(BaseMailerTestCase):
    
    # nosetests -s -v fake_mail_client.tests.test_mailer:MailerTestCase


    def test_sendmail(self):
        
        with self.start_server() as server:
            
            client = SMTPClient(host=self.host, port=self.port)
            msg = MessageFaker().create_message()
            #pprint(msg)
            result = client.send(msg)
            #pprint(result)
            
            #pprint(server._messages)
            self.assertSendResult(result)
            
            self.assertEquals(len(server._messages), 1)
            server_msg = server._messages[0]
            self.assertEquals(server_msg["mailfrom"], msg["from"]) 
            self.assertEquals(server_msg["rcpttos"], msg["tos"]) 

    


