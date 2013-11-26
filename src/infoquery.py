#!/usr/bin/env python
"""
 Queries infoblox for information on hosts. Auth required"""

import argparse
from ConfigParser import SafeConfigParser
import traceback
import sys
import logging
import json

from httplib import HTTPSConnection


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

    if args.hostname:
        hostname = args.hostname
        try:
            conn.request('GET', '/wapi/v1.0/record:host',
                        'name~=%s' % hostname, {'Authorization': auth_header,
                        'Content-Type': 'application/x-www-form-urlencoded'})
            results = json.loads(conn.getresponse().read())
            log.debug(results)

        except TypeError as error:
            log.warn('Couldn\'t fetch %s due to "%s"' % (hostname, error))
            sys.exit(1)

        except Exception as error:
            log.warn('trying to extract data failed with error "%s"' % error)
            sys.exit(1)

    for host in results:
        hosts_and_ips[host['name']] = []
        ipaddrs = []
        for ips in host['ipv4addrs']:
            ipaddrs.append(ips['ipv4addr'])
        hosts_and_ips[host['name']] = ipaddrs
    log.debug('leaving run()')

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
        log.warn('Something went wrong, python says "%s"' % error)
        sys.exit(1)
    log.debug('leaving read_config()')
    return server


def get_options():
    """ command-line options """
    parser = argparse.ArgumentParser(description='Pass cli options to script')

    parser.add_argument('-u', '--username', action='store', help='username')

    parser.add_argument('-p', '--password', action='store', help='password')

    parser.add_argument("-n", "--hostname", action="store",
                        help="Hostname to query for.")
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
        args.username = raw_input('Username: '  )

    if not args.password:
        from getpass import getpass
        args.password = getpass()

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
        log.warn('_get_server failed, python reports %s' % error)
        traceback.print_exc()
        sys.exit(1)
    log.debug('leaving_get_server()')
    return conn

if __name__ == "__main__":
    udo  /etc/init.d/hyperic-hqee-agent status
    un()
