# -*- coding: utf-8 -*-

import sys
import unittest
import time

from fake_mail_client.mailer import SMTPClient

@unittest.skipIf(sys.version_info.major < 3 and sys.version_info.minor < 2, "Skip Python Version")
class FuturesSMTPClient(SMTPClient):

    def send_multi_parallel(self, messages):
        
        import concurrent.futures

        with concurrent.futures.ThreadPoolExecutor(max_workers=self.parallel) as executor:

            results = []
            
            tasks = []
            
            for message in messages:
                if self.sleep_interval > 0:
                    time.sleep(self.sleep_interval)
                
                tasks.append(executor.submit(self.send, message))
            
            for future in concurrent.futures.as_completed(tasks):
                try:
                    results.append(future.result())
                except Exception as exc:
                    print('generated an exception: %s' % exc)
                else:
                    pass
                
            return results