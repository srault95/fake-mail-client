#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
from pprint import pprint
import json

import click

from fake_mail_client.utils import configure_logging, load_config
from fake_mail_client import version
from fake_mail_client.backends import BACKENDS
from fake_mail_client.message import MessageFaker

opt_config_file = click.option('--config-file', '-C', 
                               type=click.Path(exists=False),
                               #default="fake-mail-tests.yml",
                               #show_default=True, 
                               help='YAML config filepath for tests')

opt_silent = click.option('--silent', '-S', is_flag=True,
                          help="Suppress confirm")

opt_debug = click.option('--debug', '-D', is_flag=True)

opt_quiet = click.option('--quiet', is_flag=True)

opt_verbose = click.option('-v', '--verbose', is_flag=True,
                           help='Enables verbose mode.')

opt_logger = click.option('--log-level', '-l', 
                          required=False, 
                          type=click.Choice(['DEBUG', 'WARN', 'ERROR', 'INFO', 
                                             'CRITICAL']),
                          default='INFO', 
                          show_default=True,
                          help='Logging level')

opt_logger_file = click.option('--log-file', 
                               type=click.Path(exists=False), 
                               help='log file for output')

opt_logger_conf = click.option('--log-config', 
                               type=click.Path(exists=True), 
                               help='Logging config filepath')

opt_out = click.option('--out', '-O', 
                          required=False, 
                          type=click.Choice(['pprint',
                                             'line', 
                                             'json',
                                             'html']),
                          default='line', 
                          show_default=True,
                          help='Output format')

opt_json_result = click.option('--json-result', 
                               type=click.Path(exists=False), 
                               help='JSON file for test report')

opt_backend = click.option('--backend', '-B', 
              required=False,
              default="default", 
              show_default=True,
              type=click.Choice(list(BACKENDS.keys())), 
              help='Concurrency backend for parallel send')

class Context(object):
    def __init__(self, 
                 config_file=None,
                 verbose=False,
                 log_level='ERROR', log_config=None, log_file=None,
                 trace=False,
                 cache_enable=False,  
                 debug=False, silent=False, pretty=False, quiet=False):

        self.config = None
        self.config_file = config_file
        
        self.verbose = verbose
        self.debug = debug
        self.silent = silent
        self.pretty = pretty
        self.quiet = quiet
        self.trace = trace
        
        self.log_level = log_level
        self.log_config = log_config
        self.log_file = log_file

        if self.config_file:
            self.config = load_config(self.config_file)
        
        if self.verbose and log_level != "DEBUG":
            self.log_level = 'INFO'
        
        self._logger = configure_logging(debug=self.debug, 
                                         config_file=self.log_config, 
                                         level=self.log_level)
        
        if self.log_file:
            self._set_log_file()
            
    def _set_log_file(self):
        from logging import FileHandler
        handler = FileHandler(filename=self.log_file)
        if self._logger.hasHandlers():
            handler.setFormatter(self._logger.handlers[0].formatter)
        self._logger.addHandler(handler)
        
    def log(self, msg, *args):
        """Logs a message to stderr."""
        if args:
            msg %= args
        if self.quiet:
            self._logger.info(msg)
            return
        click.echo(msg, file=sys.stderr)

    def log_error(self, msg, *args):
        """Logs a message to stderr."""
        if args:
            msg %= args
        if self.quiet:
            self._logger.error(msg)
            return
        click.echo(click.style(msg, fg='red'), file=sys.stderr)

    def log_ok(self, msg, *args):
        """Logs a message to stdout."""
        if args:
            msg %= args
        if self.quiet:
            self._logger.info(msg)
            return
        click.echo(click.style(msg, fg='green'), file=sys.stdout)

    def log_warn(self, msg, *args):
        """Logs a message to stdout."""
        if args:
            msg %= args
        if self.quiet:
            self._logger.warn(msg)
            return
        click.echo(click.style(msg, fg='yellow'), file=sys.stdout)

    def pretty_print(self, obj):
        pprint(obj)


@click.version_option(version=version.version_str(),
                      prog_name="fake-mail-client",
                      message="%(prog)s %(version)s")
@click.group()
def cli():
    """Fake Mail Client Commands."""
    pass

def sendmail_report(results, out='line'):
    import tablib
    import arrow
    data = tablib.Dataset(headers=['From', 'Duration', 'Success'])
    for r in results:
        success = "success"
        if not r['success']:
            success = "fail"
        mail_from = None
        if "mail" in r:
            mail_from = r["mail"]["value"]
        data.append([
            #r['id'], 
            mail_from,
            "%.2f" % r['duration'], 
            success            
        ])
    
    if out == "json":
        from json import dump
        output = {
            "metas": {"date": arrow.utcnow().for_json()},
            "datas": results
        }
        dump(output, sys.stdout, indent=4)
    elif out == "pprint":
        output = {
            "metas": {"date": arrow.utcnow().for_json()},
            "datas": results
        }
        pprint(output, width=120, compact=True)
    elif out == "html":
        #TODO: reste body/title/date
        print(data.html)
    else:
        print("---------------------------------------------------")
        print(str(arrow.utcnow()))
        print("---------------------------------------------------")
        print(str(data.headers))
        print(data.json)
        for d in data:
            print(str(d))

@cli.command('sendmail')
@opt_verbose
@opt_quiet
@opt_debug
@opt_logger
@opt_logger_conf
@opt_logger_file
@opt_config_file
@opt_backend
@opt_out
@opt_json_result
@click.option('--host', '-H', default="localhost", 
              show_default=True, help='SMTP Server host.')
@click.option('--port', '-P', default=25, type=int, 
              show_default=True, help='SMTP Server port.')
@click.option('--source-address', 
              show_default=False, help='Source Address.')
@click.option('--count', default=1, type=int, 
              show_default=True, help='Number of message send.')
@click.option('--parallel', default=1, type=int, 
              show_default=True, help='Number of parallel message.')
def cmd_sendmail(host=None, port=None, source_address=None, backend="default", 
                 out='print', json_result=None, count=1, parallel=1, **kwargs):
    """Sendmail command."""
    
    ctx = Context(**kwargs)
    
    if ctx.config:
        backend = ctx.config["global"]["backend"]
        host = ctx.config["global"]["host"]
        port = ctx.config["global"]["port"]
        source_address = ctx.config["global"]["source_address"]
        parallel = ctx.config["global"]["parallel"]
        #count = ctx.config["global"]["count"]
        count = len(ctx.config["tests"])
    
    klass = BACKENDS[backend]
    client = klass(host=host, 
                   port=port, 
                   source_address=source_address,
                   parallel=parallel)
    """
    TODO: timeout global
    TODO: timeout per smtp
    TODO: multi client
    TODO: sleep
    TODO: parameters:
     xclient_enable=False
     xforward_enable=False
     timeout=GLOBAL_DEFAULT_TIMEOUT
     tls=False
     login=False, username=None, password=None
     debug_level=0
     sleep_interval=0
    """
    if count > 1:
        if ctx.config:
            messages = [MessageFaker(**config).create_message() for config in ctx.config["tests"]]
        else:
            messages = [MessageFaker().create_message() for i in range(count)]
        
        results = client.send_multi_parallel(messages)
    else:
        if ctx.config:
            message = MessageFaker(**ctx.config["tests"][0]).create_message()
        else:
            message = MessageFaker().create_message()
        
        results = [client.send(message)]
    
    if json_result:
        if os.path.exists(json_result):
            os.remove(json_result)
        with open(json_result, 'w') as fp:
            json.dump(results, fp, indent=1)
    else:
        sendmail_report(results, out=out)

def main():
    cli()

if __name__ == "__main__":
    main()
