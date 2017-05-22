#!/usr/bin/env python3
import berserker_resolver
import os
import shutil
import time

from contextlib import contextmanager
from urllib.parse import urlparse


NAMESERVERS = ('8.8.8.8', '8.8.4.4', '84.200.69.80', '84.200.70.40')
HOSTS_PATH = os.environ.get('HOSTSUPDATE_HOSTS_PATH')
CCD_FILEPATH = os.environ.get('HOSTSUPDATE_CCD_FILEPATH')


@contextmanager
def timed():
    t = time.time()
    yield
    print('Elapsed time: {:.1f}s'.format(time.time() - t))


def prepare_host(url):
    if '//' not in url:
        url = 'http://' + url

    hostname = urlparse(url).hostname
    if not hostname:
        raise ValueError('Cannot get hostname from: {!r}'.format(url))

    return hostname


def get_hosts(filepath):
    with open(filepath, 'r') as f:
        return set(prepare_host(h.strip()) for h in f)


def write_ovpn_ccd(ips, dstpath):
    with open('ovpn.ccd', 'w') as f:
        for ip in ips:
            f.write('push "route {ip} 255.255.255.0"\n'.format(ip=ip))

    shutil.copyfile('ovpn.ccd', dstpath)


def main():
    hosts = get_hosts(HOSTS_PATH)

    print('Start to resolve {} hostnames...'.format(len(hosts)))
    resolver = berserker_resolver.Resolver(
        tries=12, nameservers=NAMESERVERS, www=True, www_combine=True)

    resolved_ips = set()
    for resolves in resolver.resolve(hosts).values():
        resolved_ips.update(r.address for r in resolves)

    if CCD_FILEPATH:
        write_ovpn_ccd(resolved_ips, CCD_FILEPATH)
        print('Written {} IP addresses.'.format(len(resolved_ips)))
    else:
        print('"HOSTSUPDATE_CCD_FILEPATH" environment variable is not found.')


if __name__ == '__main__':
    with timed():
        main()
