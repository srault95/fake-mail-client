# -*- coding: utf-8 -*-

try:
    from fake_mail_client.backends.mailer_gevent import GeventSMTPClient as SMTPClient
    GEVENT_ENABLE = True
except ImportError:
    GEVENT_ENABLE = False

from fake_mail_client.message import MessageFaker

import unittest 
from pprint import pprint
from ..test_mailer import BaseMailerTestCase

@unittest.skipIf(not GEVENT_ENABLE, "Skip Gevent not installed")
class GeventMailerTestCase(BaseMailerTestCase):
    
    # nosetests -s -v fake_mail_client.tests.test_backends.test_mailer_gevent:GeventMailerTestCase

    def test_sendmail(self):
        
        concurrency = 5
        
        with self.start_server() as server:
            
            client = SMTPClient(host=self.host, port=self.port, 
                                concurrency=concurrency)
            messages = [MessageFaker().create_message() for i in range(concurrency)]
            messages_byID = {msg["id"]: msg for msg in messages}
            
            results = client.send_multi_concurrency(messages)
            self.assertEqual(len(results), concurrency)
            #pprint(results)
            for result in results:
                self.assertSendResult(result)                
                msg = messages_byID[result["id"]]
                #self.assertEqual(server_msg["mailfrom"], msg["from"]) 
                #self.assertEqual(server_msg["rcpttos"], msg["tos"])
            self.assertEqual(len(server._messages), concurrency)
            #pprint(server._messages)
 
