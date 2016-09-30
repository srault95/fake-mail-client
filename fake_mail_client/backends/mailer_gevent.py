# -*- coding: utf-8 -*-

from gevent import pool
import time

from fake_mail_client.mailer import SMTPClient

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
    