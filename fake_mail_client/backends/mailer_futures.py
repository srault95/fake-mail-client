# -*- coding: utf-8 -*-

import time
import concurrent.futures

from fake_mail_client.mailer import SMTPClient

class FuturesSMTPClient(SMTPClient):

    def send_multi_concurrency(self, messages):
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.concurrency) as executor:

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