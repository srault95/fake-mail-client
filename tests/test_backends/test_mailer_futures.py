# -*- coding: utf-8 -*-

import sys
import unittest
from pprint import pprint

try:
    from fake_mail_client.backends.mailer_futures import FuturesSMTPClient as SMTPClient
except ImportError:
    pass

from fake_mail_client.message import MessageFaker

from ..test_mailer import BaseMailerTestCase

@unittest.skipIf(sys.version_info[:2] < (3, 4), "Skip Python Version < 3.4")
class FuturesMailerTestCase(BaseMailerTestCase):
    
    # nosetests -s -v fake_mail_client.tests.test_backends.test_mailer_futures:FuturesMailerTestCase

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
 
