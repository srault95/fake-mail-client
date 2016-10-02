FROM python:3.4

ADD . /code/

WORKDIR /code

RUN pip install -U pip \
	&& pip install .[gevent]
	
ENTRYPOINT ["/usr/local/bin/fake-mailer"]

CMD ["--help"]	