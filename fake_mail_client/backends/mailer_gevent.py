# -*- coding: utf-8 -*-

try:
    from gevent import monkey
    monkey.patch_all()
    from gevent import pool
    GEVENT_ENABLE = True
except ImportError:
    GEVENT_ENABLE = False
        
import time
import unittest 

from fake_mail_client.mailer import SMTPClient

@unittest.skipIf(GEVENT_ENABLE, "Skip Gevent not installed")
class GeventSMTPClient(SMTPClient):

    def send_multi_parallel(self, messages):
        greenlets = []
        _pool = pool.Pool(self.parallel)        
        
        for message in messages:
            if self.sleep_interval > 0:
                time.sleep(self.sleep_interval)
            greenlets.append(_pool.spawn(self.send, message))        
        
        _pool.join()

        results = []
        for g in greenlets:
            results.append(g.value)
        
        return results
    