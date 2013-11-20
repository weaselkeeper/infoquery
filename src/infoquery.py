#!/usr/bin/env python
"""
 Queries infoblox for information on hosts. Auth required"""

import argparse
from ConfigParser import SafeConfigParser
import traceback
import sys
import re
import pprint
import logging
import requests

from httplib import HTTPSConnection

try:
    import json
except:
    import simplejson as json


""" Set some defaults """

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
    args = get_options()
    conn = _get_server(args)

    if args.hostname:
        # Only doing one system
        hostname = args.hostname
        try:
            system = conn.get_item('system', hostname)
            name = system['name']
        except TypeError as error:
            log.warn('Couldn\'t fetch %s due to "%s"' % (hostname, error))
            sys.exit()
        except Exception as error:
            log.warn('trying to extract hostname failed with error "%s"' % error)
            sys.exit()

        print "System %s as %s:" % (name, hostname)
        if not args.quiet:
            pprint.pprint(system)


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
    try:
        config = SafeConfigParser()
        config.read(args.config)
        server = config.get('server', 'host')
        print server
    except Exception as error:
        log.warn('Something went wrong, python says "%s"' % error)
        sys.exit(1)
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
    parser.add_argument("-g", "--glob", action="store",
                        help="""restrict actions to hosts that match regex
Example, ./infoquery.py  -g 'checkout-app0?.*prod.*'
For all the checkout-app0[] in prod""")
    parser.add_argument("-q", "--quiet", action="store_true",
                        help="just tell me what systems match -g or hostname")
    parser.add_argument("-a", "--all", action="store_true",
                        help="Do for all systems infoblox knows about, use with \
-q, or get flooded with lots of text")
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

    if not args.hostname and not args.glob and not args.list_all\
            and not args.all:
        args.hostname = raw_input('hostname: ')

    if args.debug:
        log.setLevel(logging.DEBUG)

    args.usage = "usage: %prog [options]"

    return args


def _get_server(args):
    """ getting the server object """
    try:
        conn = HTTPSConnection(args.server)
        return conn
    except Exception as error:
        log.warn('Something went wrong with _get_server, python reports %s' % error)
        traceback.print_exc()
        return None

if __name__ == "__main__":
    run()
