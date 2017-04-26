FROM python:3.4

ENV DEBIAN_FRONTEND noninteractive

ADD . /code/

WORKDIR /code

RUN apt-get update \
	&& apt-get install -y --no-install-recommends postfix \
	&& pip install -U pip \
	&& pip install .[gevent]
	
ENTRYPOINT ["/usr/local/bin/fake-mailer"]

CMD ["--help"]	