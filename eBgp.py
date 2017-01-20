#!/usr/bin/python

from mininet.topo import Topo
from mininet.net import Mininet
from mininet.cli import CLI
from mininet.log import setLogLevel, info
from mininet.node import RemoteController, OVSBridge, Node
from mininet.link import Intf
from sdnip import BgpRouter, SdnipHost


class BGPTopo(Topo):

    def __init__(self, *args, **kwargs):
        Topo.__init__(self, *args, **kwargs)
        # Describe Code
        # Set up data plane switch - this is the emulated router dataplane
        # Note: The controller needs to be configured with the specific driver that
        # will be attached to this switch.

        # IX fabric
        s1 = self.addSwitch('s1', cls=OVSBridge)

        # Each Peer consists of 1 quagga router PLUS
        # 1 host per network advertised behind quagga
        peers=[{'address':'192.168.100.20', 'as':200}]
        self.addPeer(s1, name='r1', port=2, mac='08:00:27:89:3b:9f', ip='192.168.100.10/24',
                            networks=['100.0.0.0/24', '110.0.0.0/24'], asn=100, peers=peers)

        peers=[{'address':'192.168.100.10', 'as':100}]
        self.addPeer(s1, name='r2', port=1, mac='08:00:27:92:18:1f', ip='192.168.100.20/24',
                            networks=['140.0.0.0/24', '150.0.0.0/24'], asn=200, peers=peers)

    def addPeer(self, bridge, name, port, mac, ip, networks, asn, peers):

        # Adds the interface to connect the router to the Route server
        peereth0 = [{'mac': mac, 'ipAddrs': [ip]}]
        intfs = {name+'-eth0': peereth0}

        # Adds 1 gateway interface for each network connected to the router
        for net in networks:
            eth = {'ipAddrs': [replace_ip( net, '254')]}  # ex.: 100.0.0.254
            i = len(intfs)
            intfs[name+'-eth'+str(i)] = eth
            
        # Set up the peer router
        peer = self.addHost(name, intfDict=intfs, asNum=asn,
                            neighbors=peers, routes=networks, cls=BgpRouter)
        self.addLink(bridge, peer, port)
        
        # Adds a host connected to the router via the gateway interface
        i = 0
        for net in networks:
            i += 1
            ips = [replace_ip(net, '1')]  # ex.: 100.0.0.1/24
            hostname = 'h' + str(i) + '_' + name  # ex.: h1_a1
            host = self.addHost(hostname,
                                cls=SdnipHost,
                                ips=ips,
                                gateway = replace_ip( net, '254').split('/')[0])  #ex.: 100.0.0.254
            # Set up data plane connectivity
            self.addLink(peer, host)


def replace_ip(network, ip):
    net, subnet = network.split('/')
    gw = net.split('.')
    gw[3] = ip
    gw = '.'.join(gw)
    gw = '/'.join([gw,subnet])
    return gw

if __name__ == "__main__":
    setLogLevel('info')
    topo = BGPTopo()

    net = Mininet(topo=topo, switch=OVSBridge)
    s1 = net.switches[0]
    intfName = 'enp0s8'
    info( '*** Connecting to hw intf: %s' % intfName )
    _intf = Intf(intfName, node=s1, port=3)
    net.start()

    CLI(net)

    net.stop()

    info("done\n")
