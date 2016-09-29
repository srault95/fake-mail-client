# -*- coding: utf-8 -*-

import hashlib
import uuid
import datetime
import mimetypes
import os
import random

from email import message_from_string
from email import encoders
from email.header import Header
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from email.mime.audio import MIMEAudio
from email.mime.image import MIMEImage
from email.mime.text import MIMEText
from email.utils import make_msgid

import arrow
from faker import Factory
from faker.providers.internet.en_US import Provider as InternetUSProvider

from . import resources

FAKE_HEADER = 'X-FAKE-MAIL-ID'

RESOURCE_DIR = os.path.abspath(os.path.dirname(resources.__file__))

FILES = [
    {
        'name': 'google.pdf', 
        'path': os.path.join(RESOURCE_DIR, 'google.pdf'),
        'mimetype': 'application/pdf',
        'size': 11303, 
    },
    {
        'name': 'bunny.jpg', 
        'path': os.path.join(RESOURCE_DIR, 'bunny.jpg'),
        'mimetype': 'image/jpeg',
        'size': 27091, 
    },
]


ADDR_FORMAT = '%s <%s>'

def generate_key():
    """Génère un ID unique de 64 caractères"""
    new_uuid = str(uuid.uuid4())
    return hashlib.sha256(new_uuid.encode()).hexdigest()

def header_body_sender(name, sender, charset='utf-8'):
    return Header(ADDR_FORMAT % (name, sender), charset=charset).encode()

def is_ascii(_str):
    return all(ord(c) < 128 for c in _str)

def header(_str, charset='utf-8'):
    if is_ascii(_str):
        return _str
    return Header(_str, charset).encode()

DEFAULT_LANG = "en_US"

def attach(filepath=None, filename=None, mimetype=None):
    
    if not os.path.exists(filepath):
        raise Exception("file %s not found" % filepath)

    type_maj, type_min = mimetype.split('/')

    with open(filepath, 'rb') as fp:
        msg_file = MIMEBase(type_maj, type_min)
        msg_file.set_payload(fp.read())
        encoders.encode_base64(msg_file)
        msg_file.add_header('Content-Disposition', 'attachment', filename=filename)
        return msg_file

FILTER_CLEAN = 0    
FILTER_SPAM = 1
FILTER_VIRUS = 2
FILTER_BANNED = 3
FILTER_UNCHECKED = 4

FILTER_STATUS_CHOICES = [FILTER_CLEAN, FILTER_SPAM, FILTER_VIRUS, FILTER_BANNED, FILTER_UNCHECKED]    

class MessageFaker(object):
    
    def __init__(self,
                 id=None,
                 is_out=False,
                 from_ip=None,
                 from_hostname=None,
                 from_heloname=None, 
                 enveloppe_sender=None,
                 enveloppe_recipients=[],
                 sender=None,
                 recipients=[],
                 body=None,
                 subject=None,
                 random_files=0,
                 is_multipart=False,
                 is_bounce=None,
                 filter_status=None,
                 min_size=0,
                 sent_date=None,
                 lang=None,
                 charset='utf-8',
                 domains=[], 
                 mynetworks=[]):

        self.id = id or generate_key()

        self.lang = lang or DEFAULT_LANG
        
        self.faker = Factory.create(self.lang)

        self.charset = charset

        self.is_out = is_out
        
        if self.is_out and mynetworks and len(mynetworks)> 0:  
            self.from_ip = random.choice(mynetworks)
        else:
            self.from_ip = from_ip or self.faker.ipv4()
                
        self.from_hostname = from_hostname or "mx.%s" % self.faker.domain_name()

        self.from_heloname = from_heloname or self.from_hostname
        
        self.is_bounce = is_bounce or random.choice([False, False, True, False, False])
        
        if domains and len(domains) > 0:
            if self.is_out:
                self.enveloppe_sender = "%s@%s" % (self.faker.user_name(), random.choice(domains))
                self.enveloppe_recipients = enveloppe_recipients or [self.faker.email()]
            else:         
                self.enveloppe_sender = enveloppe_sender or self.faker.email()
                self.enveloppe_recipients = ["%s@%s" % (self.faker.user_name(), random.choice(domains))]
        else:
            self.enveloppe_sender = enveloppe_sender or self.faker.email()
            self.enveloppe_recipients = enveloppe_recipients or [self.faker.email()]
        
        if self.is_bounce:
            self.sender = "<>"
        else:
            self.sender = sender or '"%s" <%s>' % (self.faker.name(), self.enveloppe_sender)
        
        self.recipients = recipients
        
        if not recipients or len(recipients) == 0:
            self.recipients = []
            for r in self.enveloppe_recipients:
                _r  = '"%s" <%s>' % (self.faker.name(), r)
                self.recipients.append(_r)
        
        self.min_size = min_size
        
        self.body = body or self.faker.text()
        
        self.subject = subject or self.faker.paragraph()
        
        self.random_files = random_files

        self.is_multipart = is_multipart
        
        if self.random_files > 0:
            self.is_multipart = True
                
        self.filter_status = filter_status or random.choice(FILTER_STATUS_CHOICES)
        
        if self.min_size > 0 and len(self.body) < self.min_size:
            _body = []
            while len(" ".join(_body)) < self.min_size:
                _body.append(self.body)            
            self.body = " ".join(_body)
            
        self.sent_date = None
        if sent_date:
            self.sent_date = arrow.get(sent_date).datetime
        else:
            self.sent_date = arrow.utcnow().datetime
    
    def create_message(self):
        
        message = {}
        message['id'] = self.id
        message['date'] = self.sent_date
        message['is_bounce'] = self.is_bounce
        message['from'] = self.enveloppe_sender
        message['tos'] = self.enveloppe_recipients
        message['from_ip'] = self.from_ip
        message['from_hostname'] = self.from_hostname
        message['from_heloname'] = self.from_heloname
        message['filter_status'] = self.filter_status
        
        msg = None
        body_mail = MIMEText(self.body, _charset=self.charset)
        
        if self.is_multipart:
            msg = MIMEMultipart()
            msg.attach(body_mail)
        else:
            msg = body_mail
        
        msg['X-Mailer'] = 'MessageFaker'
        msg[FAKE_HEADER] = self.id
        msg['Message-ID'] = make_msgid() #'<20150407070356.10188.26737@admin-VAIO>'
        msg['From'] = header(self.sender, self.charset)
        tos = []
        for r in self.recipients:
            tos.append(header(r, self.charset))            
        msg['To'] = ", ".join(tos)
        
        msg['Date'] = self.sent_date.strftime('%a, %d %b %Y %H:%M:%S %Z')
        
        if self.filter_status == FILTER_SPAM:
            msg['X-Spam-Flag'] = "YES"
        elif self.filter_status == FILTER_BANNED:
            msg['X-Amavis-Alert'] = "BANNED"
        elif self.filter_status == FILTER_VIRUS:
            msg['X-Amavis-Alert'] = "INFECTED"
        elif self.filter_status == FILTER_UNCHECKED:
            self.subject = "[UNCHECKED] %s" % self.subject

        msg['Subject'] = header(self.subject, self.charset)
        
        #TODO: limit size
        original_size = len(self.body)
        if self.random_files > 0:
            for i in range(0, self.random_files):
                f = random.choice(FILES)                
                msg_file = attach(filepath=f['path'], filename=f['name'], mimetype=f['mimetype'])
                original_size += f['size']
                msg.attach(msg_file)

        message['message'] = msg.as_string()
        message['size'] = len(message['message'])
        message['original_size'] = original_size
        
        return message 

def main():
    from pprint import pprint as pp
    msg1 = MessageFaker().create_message()
    pp(msg1)
    #msg = message_from_string(msg1['message'])
    #print(msg.as_string())

    # output mail
    msg1 = MessageFaker(is_out=True, domains=["example.org"], mynetworks=["192.1.1.1"]).create_message()
    pp(msg1)
    
    """
    # add files
    msg2 = MessageFaker(random_files=3).create_message()
    msg = message_from_string(msg2['message'])
    pp(msg2)
    """
    
    """
    # change date
    start = datetime.datetime(2013, 5, 1, 12, 30)
    end = datetime.datetime(2013, 5, 5, 17, 15)
    for r in arrow.Arrow.range('day', start, end):
        msg = MessageFaker(sent_date=r.datetime).create_message()
        print(msg['date'], msg['from'])
        #print message_from_string(msg['message'])['Date']
    """

if __name__ == "__main__":
    """
    python -m fake_mail_client.message
    """
    main()    