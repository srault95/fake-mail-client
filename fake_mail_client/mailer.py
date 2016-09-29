# -*- coding: utf-8 -*-

import smtplib
import socket

from fake_mail_client.utils import SMTPCommand

try:
    GLOBAL_DEFAULT_TIMEOUT = socket._GLOBAL_DEFAULT_TIMEOUT
except:
    GLOBAL_DEFAULT_TIMEOUT = None
    
class SMTP(smtplib.SMTP):
    
    def xclient(self, addr=None, name=None, helo=None, proto='ESMTP'):
        """Postfix XCLIENT extension
        
        http://www.postfix.org/XCLIENT_README.html
        
        required: smtpd_authorized_xclient_hosts
        
        PROTO SMTP or ESMTP
        
        attribute-name = ( NAME | ADDR | PORT | PROTO | HELO | LOGIN (SASL) )  
        
        ADDR UNAVAILABLE ?
        """
        xclient_cmd = 'XCLIENT NAME=%s ADDR=%s PROTO=%s HELO=%s' % (name or addr,
                                                                    addr,
                                                                    proto,
                                                                    helo or name or addr)
        
        (code,msg) = self.docmd(xclient_cmd)
        return (code,msg)

    def xforward(self, addr=None, name=None, helo=None):
        u"""Postfix XFORWARD extension
        
        http://www.postfix.org/XFORWARD_README.html
        
        required: smtpd_authorized_xforward_hosts
        """
        xforward_cmd = 'XFORWARD NAME=%s ADDR=%s HELO=%s' % (name or addr, 
                                                             addr, 
                                                             helo or name or addr)
        (code,msg) = self.docmd(xforward_cmd)
        return (code,msg)

class SMTPClient(object):
    
    def __init__(self, 
                 host='127.0.0.1', 
                 port=25,
                 source_address=None, 
                 xclient_enable=False,
                 xforward_enable=False,
                 timeout=GLOBAL_DEFAULT_TIMEOUT,
                 tls=False, 
                 login=False, username=None, password=None,
                 debug_level=0,
                 parallel=1,
                 sleep_interval=0):
        
        self.host = host
        self.port = port
        self.source_address = source_address
        self.timeout = timeout
        
        if xclient_enable and xforward_enable:
            raise ValueError("Please choice xclient or xforward protocol")
        
        self.xclient_enable = xclient_enable
        self.xforward_enable = xforward_enable
        self.tls = tls
        self.login = login
        self.username = username
        self.password = password or ''        
        self.debug_level = debug_level
        
        self.sleep_interval = sleep_interval
        self.parallel = parallel
        
    def send_multi(self, messages):
        """Sent sequential messages"""
        results = []
        for message in messages:
            results.append(self.send(message))
        return results

    def send_multi_parallel(self, messages):
        raise NotImplementedError()
        
    def send(self, message):
        result = {'duration': 0, 'success': False, 'id': message['id'], 'error': None}
        try:
            self._send(message, result)
        except Exception as err:
            result['error'] = str(err)
        else:
            for field in result.values():
                if isinstance(field, dict):
                    if 'duration' in field:
                        result['duration'] += field['duration']
                elif isinstance(field, list):
                    for r in field:
                        if 'duration' in r:
                            result['duration'] += r['duration']

        return result
    
    def _send(self, message, result):
        
        smtp_client = SMTP(source_address=self.source_address, timeout=self.timeout)
        smtp_client.set_debuglevel(self.debug_level)

        value = dict(host=self.host, port=self.port)
        result['connect'] = SMTPCommand("connect", value=value, func=smtp_client.connect, kwargs=value).run()
        if result['connect']["error"]:
            raise Exception(result['connect']["error"])
                    
        """
        TODO: tls
        if self.tls:
            (code, msg) = smtp_client.starttls()#keyfile, certfile
            result['starttls'] = (code, msg)
            
        TODO: login
        if self.login:
            (code, msg) = smtp_client.login(self.username, self.password)
            result['login'] = (code, msg)
        """
        value = dict(name=message.get('from_heloname', "helo.example.net"))
        result['ehlo'] = SMTPCommand("ehlo", value=value["name"], func=smtp_client.ehlo, kwargs=value).run() 
        if result['ehlo']["error"]:
            raise Exception(result['ehlo']["error"])

        features = smtp_client.esmtp_features
        if self.xclient_enable and "xclient" in features:
            value = dict(addr=message.get('from_ip'), 
                         name=message.get('from_hostname', None), 
                         helo=message.get('from_heloname', None))
            result['xclient'] = SMTPCommand("xclient", value=value["addr"], func=smtp_client.xclient, kwargs=value).run()
            if result['xclient']["error"]:
                raise Exception(result['xclient']["error"])
            
        elif self.xforward_enable and "xforward" in features:
            value = dict(addr=message.get('from_ip'), 
                         name=message.get('from_hostname', None), 
                         helo=message.get('from_heloname', None))
            result['xforward'] = SMTPCommand("xforward", value=value["addr"], func=smtp_client.xforward, kwargs=value).run()
            if result['xforward']["error"]:
                raise Exception(result['xforward']["error"])

        value = smtplib.quoteaddr(message['from'])
        result['mail'] = SMTPCommand("mail", value=message['from'], func=smtp_client.mail, args=[value]).run()
        if result['mail']["error"]:
            raise Exception(result['mail']["error"])
        
        recipients_result = []
        for recipient in message['tos']:
            value = smtplib.quoteaddr(recipient)
            r = SMTPCommand("rcpt", value=recipient, func=smtp_client.rcpt, args=[value]).run()
            if r["error"]:
                raise Exception(r["error"])
            recipients_result.append(r)
        result["rcpt"] = recipients_result
        
        value = message['message']
        result['data'] = SMTPCommand("data", value=value, func=smtp_client.data, args=[value]).run()
        if result['data']["error"]:
            raise Exception(result['data']["error"])
        """
        TODO: avec regexp ou grok, récupérer queue_id selon implémentation server !
        """
            
        result['quit'] = SMTPCommand("quit", value=None, func=smtp_client.quit).run()
        if result['quit']["error"]:
            raise Exception(result['quit']["error"])
        
        result['success'] = True

