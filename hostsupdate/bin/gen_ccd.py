#!/usr/bin/env python3
import ipaddress
import os
import shutil
import time

from contextlib import contextmanager
from ipwhois.asn import ASNOrigin
from ipwhois.net import Net
from itertools import chain


CCD_FILEPATH = os.environ.get('HOSTSUPDATE_CCD_FILEPATH')
ASN_LIST = (
    'AS43247',  # Yandex
    'AS13238',  # Yandex
    'AS202611',  # Yandex
    'AS207207',  # Yandex
    'AS47542',  # Vkontakte
    'AS47541',  # Vkontakte
    'AS62243',  # Vkontakte
    'AS47764',  # Mail.ru
    'AS21051',  # Mail.ru
    'AS41983',  # Kaspersky Lab
    'AS200107',  # Kaspersky Lab
    'AS61306',  # LitRes
)


@contextmanager
def timed():
    t = time.time()
    yield
    print('Elapsed time: {:.1f}s'.format(time.time() - t))


def get_networks_from_asn(asn_list):
    net = Net('2001:43f8:7b0::')
    asn_origin = ASNOrigin(net)
    networks = []
    for asn in ASN_LIST:
        nets = asn_origin.lookup(asn, field_list=['source'])['nets']
        networks.extend(ipaddress.ip_network(net['cidr']) for net in nets)

    return networks


def make_push_route_str(ip_network):
    if ip_network.version == 4:
        push_str = 'push "route {ip} {mask}"\n'.format(
            ip=ip_network.network_address,
            mask=ip_network.netmask,
        )
    else:
        push_str = 'push "route-ipv6 {cidr}"\n'.format(
            cidr=ip_network.compressed,
        )
    return push_str


def write_ovpn_ccd(ip_networks, dstpath):
    with open('ovpn.ccd', 'w') as f:
        for ip_network in ip_networks:
            f.write(make_push_route_str(ip_network))

    shutil.copyfile('ovpn.ccd', dstpath)


def main():
    networks = get_networks_from_asn(ASN_LIST)

    ipv4_networks = [n for n in networks if n.version == 4]
    ipv6_networks = [n for n in networks if n.version == 6]
    print('Recieved: {} IPv4 networks, {} IPv6 networks.'.format(
        len(ipv4_networks), len(ipv6_networks),
    ))

    collapsed_ipv4 = list(ipaddress.collapse_addresses(ipv4_networks))
    collapsed_ipv6 = list(ipaddress.collapse_addresses(ipv6_networks))
    print('After collapsing: {} IPv4 networks, {} IPv6 networks.'.format(
        len(collapsed_ipv4), len(collapsed_ipv6),
    ))

    if CCD_FILEPATH:
        write_ovpn_ccd(chain(collapsed_ipv4, collapsed_ipv6), CCD_FILEPATH)
    else:
        print('"HOSTSUPDATE_CCD_FILEPATH" environment variable is not found.')


if __name__ == '__main__':
    with timed():
        main()
