#!/usr/bin/env python
"""
 Queries infoblox for information on hosts. Auth required"""

import argparse
from ConfigParser import SafeConfigParser
import traceback
import sys
import logging
import json
import getpass

from httplib import HTTPSConnection


try:
    from pymongo import Connection
except ImportError as ERROR:
    print 'Failed import of pymmongo, system says %s' % ERROR
    sys.exit(1)

# Set some defaults

CONFIGFILE = '/etc/infoquery/infoquery.conf'


global_log_level = logging.WARN
default_log_format = logging.Formatter("%(asctime)s - %(levelname)s - \
                                       %(message)s")
default_log_handler = logging.StreamHandler(sys.stderr)
default_log_handler.setFormatter(default_log_format)

log = logging.getLogger("infoquery")
log.setLevel(global_log_level)
log.addHandler(default_log_handler)
log.debug("Starting logging")


def run():
    """ Main loop, called via .run method, or via __main__ section """
    hosts_and_ips = {}
    args = get_options()
    log.debug('In run()')
    conn = _get_server(args)

    # Setup auth
    auth_header = 'Basic %s' % (':'.join([args.username,
                                args.password]).encode('Base64').strip('\r\n'))

    log.debug('authenticating with token %s', auth_header)

    if args.hostname:
        hostname = args.hostname
        try:
            conn.request('GET', '/wapi/v1.0/record:host',
                         'name~=%s' % hostname, {'Authorization': auth_header,
                         'Content-Type': 'application/x-www-form-urlencoded'})
            _results = json.loads(conn.getresponse().read())
            log.debug('connection returns %s', _results)
            if not len(_results):
                log.warn('Zero results, host probably not in infoblox')
                sys.exit(1)
            if 'text' in _results:  # An error has occured
                log.warn('Sorry, infoblox says %s: ', _results['text'])
                sys.exit(1)
        except TypeError as error:
            log.warn('Couldn\'t fetch %s due to "%s"', hostname, error)
            sys.exit(1)

        except Exception as error:
            log.warn('trying to extract data failed with error "%s"', error)
            sys.exit(1)

    for _host in _results:
        log.debug('querying for host %s', _host)
        hosts_and_ips[_host['name']] = []
        ipaddrs = []
        for ips in _host['ipv4addrs']:
            ipaddrs.append(ips['ipv4addr'])
        hosts_and_ips[_host['name']] = ips['ipv4addr']
    log.debug('leaving run()')
    log.debug(hosts_and_ips)
    return hosts_and_ips


def read_config(args):
    """ if a config file exists, read and parse it.
    Override with the get_options function, and any relevant environment
    variables.
    Config file is in ConfigParser format

    Basically:

    [sectionname]
    key=value
    [othersection]
    key=value

    Currently, only has one key=value pair, the default cobbler host to direct
    the query to.
    """

    log.debug('entering read_config()')

    try:
        config = SafeConfigParser()
        config.read(args.config)
        server = config.get('server', 'host')
    except Exception as error:
        log.warn('Something went wrong, python says "%s"', error)
        sys.exit(1)
    log.debug('leaving read_config()')
    return server


def get_options():
    """ command-line options """
    parser = argparse.ArgumentParser(description='Pass cli options to script')

    parser.add_argument('-u', '--username', action='store', help='username')

    parser.add_argument('-p', '--password', action='store', help='password')

    parser.add_argument("-n", "--hostname", action="store",
                        help="Full or partial Hostname to query for.")
    parser.add_argument("-s", "--server", action="store",
                        dest="server", help="Infoblox server.")
    parser.add_argument("-v", "--verbose", action="store_true",
                        help="Extra info about stuff")
    parser.add_argument("-d", "--debug", action="store_true",
                        help="Set logging level to debug")
    parser.add_argument("-c", "--config", action="store", help="config file")

    args = parser.parse_args()

    if not args.config:
        args.config = CONFIGFILE

    if not args.server:
        args.server = read_config(args)

    if not args.hostname and not args.glob:
        args.hostname = raw_input('querying for hostname?: ')

    if not args.username:
        args.username = getpass.getuser()

    if not args.password:
        print 'running as user %s' % args.username
        args.password = getpass.getpass()

    if args.debug:
        log.setLevel(logging.DEBUG)

    args.usage = "usage: %prog [options]"
    log.debug('leaving get_options()')
    return args


def _get_server(args):
    """ getting the server object """
    log.debug('entering _get_server()')
    try:
        conn = HTTPSConnection(args.server)
    except Exception as error:
        log.warn('_get_server failed, python reports %s', error)
        traceback.print_exc()
        sys.exit(1)
    log.debug('leaving_get_server()')
    return conn

if __name__ == "__main__":
    results = run()
    for host in results.keys():
        print 'Host %s has IP %s' % (host, results[host])
