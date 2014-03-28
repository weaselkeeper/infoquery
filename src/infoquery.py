#!/usr/bin/env python
###
# Copyright (c) 2013, Jim Richardson <weaselkeeper@gmail.com>
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
#   * Redistributions of source code must retain the above copyright notice,
#     this list of conditions, and the following disclaimer.
#   * Redistributions in binary form must reproduce the above copyright notice,
#     this list of conditions, and the following disclaimer in the
#     documentation and/or other materials provided with the distribution.
#   * Neither the name of the author of this software nor the name of
#     contributors to this software may be used to endorse or promote products
#     derived from this software without specific prior written consent.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED.  IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.

###

"""
 Queries infoblox for information on hosts. Auth required
 Example:
    infoquery.py -u username -n testfoo* -s infoblox.server.tld
    will query infoblox.server.tld as user username for any hosts
    testfoo* (passwd will be prompted for
 """

import argparse
from ConfigParser import SafeConfigParser
import sys
import logging
import getpass
import requests

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
    if args.network:
        get_networks(args)
        sys.exit(0)
    log.debug('In run()')

    hostname = args.hostname
    session = requests.Session()
    user, passwd = args.username, args.password
    session.auth = (user, passwd)
    session.verify = False

    hosturl = 'https://' + args.server + '/wapi/v1.0/'
    query = hosturl + "record:host?name~=" + hostname
    log.debug('trying with %s', query)
    query_results = session.get(query)
    _results = query_results.json()

    for _host in _results:
        log.debug('querying for host %s', _host)
        hosts_and_ips[_host['name']] = []
        ipaddrs = []
        for ips in _host['ipv4addrs']:
            ipaddrs.append(ips['ipv4addr'])
        hosts_and_ips[_host['name']] = ips['ipv4addr']
    log.debug('leaving run()')
    log.debug(hosts_and_ips)
    return display_results(hosts_and_ips)


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


def get_networks(args):
    """ Return all the networks infoblox knows about """
    session = requests.Session()
    user, passwd = args.username, args.password
    session.auth = (user, passwd)
    session.verify = False
    hosturl = 'https://' + args.server + '/wapi/v1.0/'
    result = session.get(hosturl + 'network')
    print result.content


def display_results(_results):
    """ show the results """
    for host in _results.keys():
        print 'Host %s has IP %s' % (host, _results[host])
    return


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
    parser.add_argument("-N", "--network", action="store_true",
                        help="Get all networks")

    args = parser.parse_args()

    if not args.config:
        args.config = CONFIGFILE

    if not args.server:
        args.server = read_config(args)

    if not args.hostname and not args.network:
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


if __name__ == "__main__":
    sys.exit(run())
