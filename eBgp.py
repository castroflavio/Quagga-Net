#!/usr/bin/python

from mininet.topo import Topo
from mininet.net import Mininet
from mininet.cli import CLI
from mininet.log import setLogLevel, info
from mininet.node import RemoteController, OVSBridge, Node, CPULimitedHost
from mininet.link import Intf, TCLink
from sdnip import BgpRouter, SdnipHost

linkopts = dict(bw=10, delay='1ms', max_queue_size=1000, use_htb=True)
linkopts2 = dict(bw=1000, delay='100ms', max_queue_size=1000, use_htb=True)

class BGPTopo(Topo):

    def __init__(self, *args, **kwargs):
        Topo.__init__(self, *args, **kwargs)
        # Describe Code
        # Set up data plane switch - this is the emulated router dataplane
        # Note: The controller needs to be configured with the specific driver that
        # will be attached to this switch.

        # Mgmt switch
        ma = self.addSwitch('ma1', cls=OVSBridge)
        intfs = {'r1-eth0': [{'mac': '08:00:27:89:3b:9f', 'ipAddrs': ['192.168.100.10/24']}],
                 'r1-eth1': [{'mac': '08:00:27:80:3b:9f', 'ipAddrs': ['10.0.0.1/30']}]}

        # Set up the peer router
        r1 = self.addHost('r1', intfDict=intfs, asNum=100, neighbors=[{'address':'10.0.0.2', 'as':200}],
                          routes=[], cls=BgpRouter)
        self.addLink(ma, r1, port=1, **linkopts)

        intfs = {'r2-eth0': [{'mac': '08:00:24:89:3b:9f', 'ipAddrs': ['192.168.100.20/24']}],
                 'r2-eth1': [{'mac': '08:00:24:80:3b:9f', 'ipAddrs': ['10.0.0.2/30']}]}

        # Set up the peer router
        r2 = self.addHost('r2', intfDict=intfs, asNum=200, neighbors=[{'address':'10.0.0.1', 'as':100}],
                          routes=[], cls=BgpRouter)
        self.addLink(ma, r2, port=2, **linkopts)
        self.addLink(r1, r2, intfName='r1-eth1', intfName2='r2-eth1', **linkopts2)

if __name__ == "__main__":
    setLogLevel('info')
    topo = BGPTopo()

    net = Mininet(topo=topo, switch=OVSBridge, host=CPULimitedHost, link=TCLink)
    s1 = net.switches[0]
    intfName = 'enp0s8'
    info( '*** Connecting to hw intf: %s' % intfName )
    _intf = Intf(intfName, node=s1, port=3)
    net.start()

    CLI(net)

    net.stop()

    info("done\n")
