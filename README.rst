Fake SMTP Client
================

|Build Status| |Coveralls| |pypi licence| |pypi wheel| |pypi downloads| |pypi version| |requires status|

Requires
--------

- Python 3.4 (Tested with Python 3.4.2)

Backends for parallel sent
--------------------------

- `concurrent.futures`_
- `Gevent`_

Usage
-----

.. code-block:: bash

   $ pip install https://github.com/srault95/fake-mail-client/archive/master.zip

   # or with gevent
   $ pip install https://github.com/srault95/fake-mail-client/archive/master.zip[gevent]

   $ fake-mailer sendmail --help
   
With Docker
-----------

.. code-block:: bash

   $ docker build -t srault95/fake-mail-client https://github.com/srault95/fake-mail-client.git#master
   
   $ docker run -it --rm srault95/fake-mail-client --help

Use API
-------

.. code-block:: python

   # With default values
   >>> from fake_mail_client.mailer import SMTPClient
   >>> from fake_mail_client.message import MessageFaker
   >>> client = SMTPClient()
   >>> msg = MessageFaker().create_message()
   >>> result = client.send(msg)
   >>> print(result)
   
   # With custom values
   >>> from fake_mail_client.mailer import SMTPClient
   >>> from fake_mail_client.message import MessageFaker
   >>> client = SMTPClient(host="1.1.1.1", port=2500, source_address="192.168.1.1")
   >>> domains = ["example.org"]
   >>> mynetworks = ["1.1.1.1"]
   >>> msg = MessageFaker(is_out=True, domains=domains, mynetworks=mynetworks).create_message()
   >>> result = client.send(msg)
   >>> print(result)
   

Example - YAML story
--------------------

- see sample file: fake-mail-tests.yml.sample

.. code-block:: bash

   $ mv fake-mail-tests.yml.sample fake-mail-tests.yml

   $ fake-mailer sendmail -C fake-mail-tests.yml


Example - One mail - json format
--------------------------------

.. code-block:: bash

   $ fake-mailer sendmail -H localhost -P 2500 -O json
   
.. code-block:: json

   {
       "datas": [
           {
               "rcpt": [
                   {
                       "msg": "2.1.5 Recipient <michelle81@yahoo.com> Ok",
                       "code": 250,
                       "error": null,
                       "name": "rcpt",
                       "duration": 0.012861967086791992,
                       "value": "michelle81@yahoo.com"
                   }
               ],
               "ehlo": {
                   "msg": "Hello mx.hanson.com\nPIPELINING\nSMTPUTF8\n8BITMIME\nSTARTTLS\nENHANCEDSTATUSCODES",
                   "code": 250,
                   "error": null,
                   "name": "ehlo",
                   "duration": 0.011757135391235352,
                   "value": "mx.hanson.com"
               },
               "success": true,
               "error": null,
               "id": "ebf099d2cb890e51f5cdcf3d07d38884ce4e19764a5dadc8777a0e9daa5be4fc",
               "duration": 0.10965204238891602,
               "quit": {
                   "msg": "2.0.0 Bye",
                   "code": 221,
                   "error": null,
                   "name": "quit",
                   "duration": 0.014549016952514648,
                   "value": null
               },
               "mail": {
                   "msg": "2.1.0 Sender <cooleymichael@hotmail.com> Ok",
                   "code": 250,
                   "error": null,
                   "name": "mail",
                   "duration": 0.013148069381713867,
                   "value": "cooleymichael@hotmail.com"
               },
               "data": {
                   "msg": "2.6.0 Message accepted for delivery",
                   "code": 250,
                   "error": null,
                   "name": "data",
                   "duration": 0.030694007873535156,
                   "value": "Content-Type: text/plain; charset=\"utf-8\"\nMIME-Version: 1.0\nContent-Transfer-Encoding: base64\nX-Mailer: MessageFaker\nX-FAKE-MAIL-ID: ebf099d2cb890e51f5cdcf3d07d38884ce4e19764a5dadc8777a0e9daa5be4fc\nMessage-ID: <147516098923.10936.10419544728895125460@DESKTOP-0ATQ5E6>\nFrom: <>\nTo: \"Rose Taylor\" <michelle81@yahoo.com>\nDate: Thu, 29 Sep 2016 14:56:29 UTC\nSubject: [UNCHECKED] Nemo nulla natus dicta dignissimos. Ducimus harum mollitia architecto eligendi labore aperiam sequi. Minima in consectetur hic consequuntur fuga voluptatibus. Explicabo ad dolore debitis earum amet dignissimos ad.\n\nU2FwaWVudGUgc2ltaWxpcXVlIHNpdCBhcmNoaXRlY3RvIHBlcmZlcmVuZGlzLiBDb25zZXF1dW50\ndXIgYmVhdGFlIG1pbmltYSBkdWNpbXVzIGFzc3VtZW5kYSBuZXF1ZSBhZGlwaXNjaS4gUmVpY2ll\nbmRpcyBwb3JybyBjb21tb2RpIHJhdGlvbmUgaWxsbyBpc3RlIGRvbG9yZSBvZGl0Lg==\n"
               },
               "connect": {
                   "msg": "ESMTP server",
                   "code": 220,
                   "error": null,
                   "name": "connect",
                   "duration": 0.026641845703125,
                   "value": {
                       "port": 2500,
                       "host": "localhost"
                   }
               }
           }
       ],
       "metas": {
           "date": "2016-09-29T14:56:29.502504+00:00"
       }
   }
   
Example - parallel with Gevent - pprint format
----------------------------------------------

.. code-block:: bash

   $ fake-mailer sendmail -H localhost -P 2500 -B gevent --count 2 --parallel 2 -O pprint

.. code-block:: python

   {
     'metas': {
      'date': '2016-09-29T14:52:13.412302+00:00'
     }
     'datas': [{'connect': {'code': 220,
                           'duration': 0.026053905487060547,
                           'error': None,
                           'msg': 'ESMTP server',
                           'name': 'connect',
                           'value': {'host': 'localhost', 'port': 2500}},
               'data': {'code': 250,
                        'duration': 0.03162503242492676,
                        'error': None,
                        'msg': '2.6.0 Message accepted for delivery',
                        'name': 'data',
                        'value': 'Content-Type: text/plain; charset="utf-8"\n'
                                 'MIME-Version: 1.0\n'
                                 'Content-Transfer-Encoding: base64\n'
                                 'X-Mailer: MessageFaker\n'
                                 'X-FAKE-MAIL-ID: 12250e218814b17e3f660badf547803b5514357a0699ad57d92387cb8ff3d499\n'
                                 'Message-ID: <147516073311.6076.16938656496648635806@DESKTOP-0ATQ5E6>\n'
                                 'From: "David Mason" <gonzalezwilliam@hotmail.com>\n'
                                 'To: "Amy Parker" <miguel13@gmail.com>\n'
                                 'Date: Thu, 29 Sep 2016 14:52:13 UTC\n'
                                 'Subject: [UNCHECKED] Sint animi eligendi tenetur. Commodi rerum aliquid voluptate '
                                 'quod corrupti tempore eaque. Iusto accusantium necessitatibus fugiat quasi '
                                 'consequuntur culpa. Maxime animi consequatur eos.\n'
                                 '\n'
                                 'UXVhZSBoYXJ1bSBudWxsYSBxdWFzaSBkaWN0YS4gQ29ycG9yaXMgc2ludCBhc3BlcmlvcmVzIGlw\n'
                                 'c2EgcXVpc3F1YW0gYXV0IHRlbXBvcmEgcXVvcy4gRHVjaW11cyBkb2xvcmVtIGNvbnNlY3RldHVy\n'
                                 'IHRlbmV0dXIgZWxpZ2VuZGkuIFF1aWJ1c2RhbSBmYWNlcmUgZWxpZ2VuZGkgc2l0Lg==\n'},
               'duration': 0.11256074905395508,
               'ehlo': {'code': 250,
                        'duration': 0.013978958129882812,
                        'error': None,
                        'msg': 'Hello mx.fox-gonzales.com\n'
                               'PIPELINING\n'
                               'SMTPUTF8\n'
                               '8BITMIME\n'
                               'STARTTLS\n'
                               'ENHANCEDSTATUSCODES',
                        'name': 'ehlo',
                        'value': 'mx.fox-gonzales.com'},
               'error': None,
               'id': '12250e218814b17e3f660badf547803b5514357a0699ad57d92387cb8ff3d499',
               'mail': {'code': 250,
                        'duration': 0.01382303237915039,
                        'error': None,
                        'msg': '2.1.0 Sender <gonzalezwilliam@hotmail.com> Ok',
                        'name': 'mail',
                        'value': 'gonzalezwilliam@hotmail.com'},
               'quit': {'code': 221,
                        'duration': 0.014036893844604492,
                        'error': None,
                        'msg': '2.0.0 Bye',
                        'name': 'quit',
                        'value': None},
               'rcpt': [{'code': 250,
                         'duration': 0.013042926788330078,
                         'error': None,
                         'msg': '2.1.5 Recipient <miguel13@gmail.com> Ok',
                         'name': 'rcpt',
                         'value': 'miguel13@gmail.com'}],
               'success': True},
              {'connect': {'code': 220,
                           'duration': 0.02614879608154297,
                           'error': None,
                           'msg': 'ESMTP server',
                           'name': 'connect',
                           'value': {'host': 'localhost', 'port': 2500}},
               'data': {'code': 250,
                        'duration': 0.034635066986083984,
                        'error': None,
                        'msg': '2.6.0 Message accepted for delivery',
                        'name': 'data',
                        'value': 'Content-Type: text/plain; charset="utf-8"\n'
                                 'MIME-Version: 1.0\n'
                                 'Content-Transfer-Encoding: base64\n'
                                 'X-Mailer: MessageFaker\n'
                                 'X-FAKE-MAIL-ID: 65618590a752207cf4371132835f51992dc056ad25c80f74aa5e5765c301f16c\n'
                                 'Message-ID: <147516073314.6076.460766315749624068@DESKTOP-0ATQ5E6>\n'
                                 'From: <>\n'
                                 'To: "Jason Hawkins" <jjimenez@hotmail.com>\n'
                                 'Date: Thu, 29 Sep 2016 14:52:13 UTC\n'
                                 'X-Amavis-Alert: BANNED\n'
                                 'Subject: Atque nemo adipisci repellendus aliquid aliquam numquam porro. Sint '
                                 'molestiae incidunt incidunt odit rem in. Occaecati error deserunt distinctio eius '
                                 'facilis provident. Facilis neque porro et officia neque rem quibusdam corporis. '
                                 'Vitae nesciunt quis perferendis atque.\n'
                                 '\n'
                                 'TGFib3JlIGVzc2Ugc2l0IGVhcnVtIGNvcnJ1cHRpIGVycm9yLiBNaW51cyBhZCBhdXRlbSBzZXF1\n'
                                 'aS4gUmF0aW9uZSBlYXJ1bSB2ZWwgbmF0dXMgcXVpIGF0cXVlIGluIGN1cGlkaXRhdGUuIEFyY2hp\n'
                                 'dGVjdG8gcXVpZGVtIGhpYyBkb2xvcmVtIGFwZXJpYW0gYWRpcGlzY2ku\n'},
               'duration': 0.1162109375,
               'ehlo': {'code': 250,
                        'duration': 0.01388406753540039,
                        'error': None,
                        'msg': 'Hello mx.hull.org\nPIPELINING\nSMTPUTF8\n8BITMIME\nSTARTTLS\nENHANCEDSTATUSCODES',
                        'name': 'ehlo',
                        'value': 'mx.hull.org'},
               'error': None,
               'id': '65618590a752207cf4371132835f51992dc056ad25c80f74aa5e5765c301f16c',
               'mail': {'code': 250,
                        'duration': 0.01448202133178711,
                        'error': None,
                        'msg': '2.1.0 Sender <shawnjenkins@gmail.com> Ok',
                        'name': 'mail',
                        'value': 'shawnjenkins@gmail.com'},
               'quit': {'code': 221,
                        'duration': 0.014039039611816406,
                        'error': None,
                        'msg': '2.0.0 Bye',
                        'name': 'quit',
                        'value': None},
               'rcpt': [{'code': 250,
                         'duration': 0.01302194595336914,
                         'error': None,
                         'msg': '2.1.5 Recipient <jjimenez@hotmail.com> Ok',
                         'name': 'rcpt',
                         'value': 'jjimenez@hotmail.com'}],
               'success': True}],
  }
      
      
TODO
----

- Improve report formats
- Add attachment files
- Add eicar file for infected mail
- Add gtube file for spam mail
- TLS
- Login
- XCLIENT / XFORWARD tests
- Python 3.5 new async
- Fake SMTP Server (ESMTP, WEB, Rest API)

   
.. |Build Status| image:: https://travis-ci.org/srault95/fake-mail-client.svg?branch=master
   :target: https://travis-ci.org/srault95/fake-mail-client
   :alt: Travis Build Status
   
.. |Coveralls| image:: https://coveralls.io/repos/github/srault95/fake-mail-client/badge.svg?branch=master
   :target: https://coveralls.io/github/srault95/fake-mail-client?branch=master
   :alt: Coverage
   
.. |pypi licence| image:: https://img.shields.io/pypi/l/fake-mail-client.svg
    :target: https://pypi.python.org/pypi/fake-mail-client
    :alt: License

.. |pypi wheel| image:: https://img.shields.io/pypi/wheel/fake-mail-client.svg?maxAge=2592000
    :target: https://pypi.python.org/pypi/fake-mail-client/
    :alt: Python Wheel

.. |pypi downloads| image:: https://img.shields.io/pypi/dm/fake-mail-client.svg
    :target: https://pypi.python.org/pypi/fake-mail-client
    :alt: Number of PyPI downloads

.. |pypi version| image:: https://img.shields.io/pypi/v/fake-mail-client.svg
    :target: https://pypi.python.org/pypi/fake-mail-client
    :alt: Latest Version

.. |requires status| image:: https://requires.io/github/srault95/fake-mail-client/requirements.svg?branch=master
     :target: https://requires.io/github/srault95/fake-mail-client/?branch=master
     :alt: Requirements Status
     
.. _`Gevent`: http://www.gevent.org/
.. _`concurrent.futures`: https://docs.python.org/3/library/concurrent.futures.html