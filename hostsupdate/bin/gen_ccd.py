#!/usr/bin/env python3
import berserker_resolver
import os
import shutil
import time

from contextlib import contextmanager
from itertools import groupby
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


def write_ovpn_ccd(ip_mask_list, dstpath):
    with open('ovpn.ccd', 'w') as f:
        for ip, mask in ip_mask_list:
            f.write('push "route {ip} {mask}"\n'.format(ip=ip, mask=mask))

    shutil.copyfile('ovpn.ccd', dstpath)


def make_24_subnet(ip):
    return ip.rsplit('.', 1)[0] + '.0'


def get_squashed_ips_with_masks(ips):
    ip_mask_list = []
    for squashed_ip, g in groupby(sorted(ips), make_24_subnet):
        grouped_ips = list(g)
        if len(grouped_ips) > 5:
            ip_mask_list.append(
                (squashed_ip, '255.255.255.0'))
        else:
            ip_mask_list.extend(
                (ip, '255.255.255.255') for ip in grouped_ips)
    return ip_mask_list


def main():
    hosts = get_hosts(HOSTS_PATH)

    print('Start to resolve {} hostnames...'.format(len(hosts)))
    resolver = berserker_resolver.Resolver(
        tries=12, nameservers=NAMESERVERS, www=True, www_combine=True)

    resolved_ips = set()
    for resolves in resolver.resolve(hosts).values():
        resolved_ips.update(r.address for r in resolves)

    if CCD_FILEPATH:
        ip_mask_list = get_squashed_ips_with_masks(resolved_ips)
        write_ovpn_ccd(ip_mask_list, CCD_FILEPATH)
        print('Recieved {} IP addresses.'.format(len(resolved_ips)))
        print('Written {} squashed IP addresses.'.format(len(ip_mask_list)))
    else:
        print('"HOSTSUPDATE_CCD_FILEPATH" environment variable is not found.')


if __name__ == '__main__':
    with timed():
        main()
