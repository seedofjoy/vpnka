# vpnka

## Quick Start


* Initialize OpenVPN configuration files and certificates:
      
      docker-compose run --rm openvpn ovpn_genconfig -u udp://<VPN.SERVERNAME.COM> -d -N -p block-outside-dns
      docker-compose run --rm openvpn ovpn_initpki

* Generate a client certificate:

    ```bash
    export CLIENTNAME="your_client_name"
      
    # with a passphrase (recommended)
    docker-compose run --rm openvpn easyrsa build-client-full $CLIENTNAME

    # without a passphrase (not recommended)
    docker-compose run --rm openvpn easyrsa build-client-full $CLIENTNAME nopass
    ```

* Retrieve the client configuration with embedded certificates:

      docker-compose run --rm openvpn ovpn_getclient $CLIENTNAME > $CLIENTNAME.ovpn

* Update blocked ips:

      docker-compose run --rm hostsupdate gen_ccd.py
      
* Run OpenVPN server:

      docker-compose up -d openvpn
