# -*- coding: utf-8 -*-

from pprint import pprint

from fake_mail_client.backends.mailer_futures import FuturesSMTPClient as SMTPClient
from fake_mail_client.message import MessageFaker

from ..test_mailer import BaseMailerTestCase

class FuturesMailerTestCase(BaseMailerTestCase):
    
    # nosetests -s -v fake_mail_client.tests.test_backends.test_mailer_futures:FuturesMailerTestCase

    def test_sendmail(self):
        
        parallel = 5
        
        with self.start_server() as server:
            
            client = SMTPClient(host=self.host, port=self.port, 
                                parallel=parallel)
            messages = [MessageFaker().create_message() for i in range(parallel)]
            messages_byID = {msg["id"]: msg for msg in messages}
            
            results = client.send_multi_parallel(messages)
            self.assertEquals(len(results), parallel)
            #pprint(results)
            for result in results:
                self.assertSendResult(result)                
                msg = messages_byID[result["id"]]
                #self.assertEquals(server_msg["mailfrom"], msg["from"]) 
                #self.assertEquals(server_msg["rcpttos"], msg["tos"])
            self.assertEquals(len(server._messages), parallel)
            #pprint(server._messages)
 
