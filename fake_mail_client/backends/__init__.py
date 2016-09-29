

BACKENDS = {}

from fake_mail_client.mailer import SMTPClient
BACKENDS["default"] = SMTPClient

try:
    from fake_mail_client.backends.mailer_gevent import GeventSMTPClient
    BACKENDS["gevent"] = GeventSMTPClient
except ImportError:
    pass
    
try:
    from fake_mail_client.backends.mailer_futures import FuturesSMTPClient
    BACKENDS["futures"] = FuturesSMTPClient
except ImportError:
    pass
        