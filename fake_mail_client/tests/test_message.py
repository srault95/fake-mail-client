# -*- coding: utf-8 -*-

import unittest

from fake_mail_client.message import MessageFaker

class MailerTestCase(unittest.TestCase):

    def test_simple_message(self):
        msg = MessageFaker().create_message()
        for field in ['id', 'message', 'date', 'from', 'tos', 'from_ip', 
                      'from_heloname', 'from_hostname']:
            self.assertTrue(field in msg, "not field is msg [%s]" % field)
            self.assertIsNotNone(msg[field], "field is None [%s]" % field)
            
        self.assertEquals(len(msg["tos"]), 1)
