# vpnka

## Quick Start


* Initialize OpenVPN configuration files and certificates:

      docker-compose run --rm openvpn ovpn_genconfig -u udp://<VPN.SERVERNAME.COM>
      docker-compose run --rm openvpn ovpn_initpki
