# -*- coding: utf-8 -*-

import sys
import logging.config
import uuid
import hashlib
import time
from functools import wraps
from io import StringIO
import traceback

import six
import arrow

def last_error():
    f = StringIO() 
    traceback.print_exc(file=f)
    return f.getvalue()

class SMTPCommand:
    def __init__(self, name, value=None, func=None, args=[], kwargs={}):
        self.name = name
        self.value = value
        self.func = func
        self.cmd_args = args
        self.cmd_kwargs = kwargs
        self.error = None
        self.code = None
        self.msg = None
        self.duration = None
    
    def run(self):
        ts = time.time()
        try:
            self.code, self.msg = self.func(*self.cmd_args, **self.cmd_kwargs)
        except:
            self.error = last_error()
        te = time.time()
        self.duration = te-ts
        #if self.error:
        #    raise Exception(self.error)
        return self.result()
        
    def result(self):
        return {
            "name": self.name,
            "value": self.value,
            "error": self.error, 
            "code": self.code, 
            "msg": self.msg.decode() if self.msg else None, 
            "duration": self.duration
        }
    
    def is_error(self):
        return not self.error is None

def smtp_command_time(name):
    def timeit_wrapped(f):
        @wraps(f)
        def timed(*args, **kw):
            result = {"error": None, "code": None, "msg": None, "duration": 0}
            ts = time.time()
            try:
                result["code"], result["msg"] = f(*args, **kw)
            except Exception as err:
                result["error"] = str(err)
            te = time.time()
            result["duration"] = te-ts
            return result
        return timed
    return timeit_wrapped

def utcnow():
    return arrow.utcnow().datetime

def generate_key():
    new_uuid = str(uuid.uuid4())
    return str(hashlib.sha1(six.b(new_uuid)).hexdigest())

def configure_logging(debug=False, stdout_enable=True, config_file=None,
                      level="INFO"):

    if config_file:
        logging.config.fileConfig(config_file, disable_existing_loggers=True)
        return logging.getLogger('')

    #TODO: handler file ?    
    LOGGING = {
        'version': 1,
        'disable_existing_loggers': True,
        'formatters': {
            'debug': {
                'format': 'line:%(lineno)d - %(asctime)s %(name)s: [%(levelname)s] - [%(process)d] - [%(module)s] - %(message)s',
                'datefmt': '%Y-%m-%d %H:%M:%S',
            },
            'simple': {
                'format': '[%(process)d] - %(asctime)s %(name)s: [%(levelname)s] - %(message)s',
                'datefmt': '%Y-%m-%d %H:%M:%S',
            },
        },    
        'handlers': {
            'null': {
                'level':level,
                'class':'logging.NullHandler',
            },
            'console':{
                'level':level,
                'class':'logging.StreamHandler',
                'formatter': 'simple',
                'stream': sys.stdout
            },      
        },
        'loggers': {
            '': {
                'handlers': [],
                'level': level,
                'propagate': False,
            },
    
        },
    }
    
    logging.getLogger("requests.packages.urllib3.connectionpool").setLevel(logging.ERROR)
    
    if stdout_enable:
        if not 'console' in LOGGING['loggers']['']['handlers']:
            LOGGING['loggers']['']['handlers'].append('console')

    '''if handlers is empty'''
    if not LOGGING['loggers']['']['handlers']:
        LOGGING['loggers']['']['handlers'] = ['console']
    
    if debug:
        LOGGING['loggers']['']['level'] = 'DEBUG'
        for handler in LOGGING['handlers'].keys():
            if handler != 'null':
                LOGGING['handlers'][handler]['formatter'] = 'debug'
                LOGGING['handlers'][handler]['level'] = 'DEBUG' 

    logging.config.dictConfig(LOGGING)
    return logging.getLogger()

def load_config(filepath):
    import yaml
    with open(filepath) as fp:
        return yaml.load(fp)

