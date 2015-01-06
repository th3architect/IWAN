#! /usr/bin/python

#import Router from Router
import hashlib

# boolean
false = 0
true = 1

# Interface kinds:
lan = 1
mpls = 2
inet = 3
loopback = 4

# Routing treatment for interface
active = 1
passive = 2

# Routing Protocols
eigrp = 1
bgp = 1



eigrpName = "IWAN-EIGRP"
eigrpAs = 400
eigrpStub = "no eigrp stub"
bgpAs = 1
ospfArea = 1
lanKey = "LAN-KEY"
passWord = "cisco"
timeZone = "PST -8"
timeDaylight = "PDT"
intfMgmt = "Loopback 0"
ntpServer = "a.b.c.d"
fVRFMPLS = "IWAN-TRANSPORT-1"
cryptoIkev2KeyringMPLS = "DMPVN-KEYRING-1"
fVRFINET = "IWAN-TRANSPORT-2"
cryptoIkev2KeyringINET = "DMVPN-KEYRING-2"

CommonIntfCfg = [
    "  ip pim sparse-mode\n",
    "  load-interval 30\n",
    "  no shutdown\n"
]

CommonRtrCfg = [
    "key chain %s\n" % lanKey,
    "  key 1\n",
    "    key-string %s\n" % passWord,
    "  exit\n",
    "exit\n",
    "no ip domain-lookup\n",
    "username admin secret %s\n" % passWord,
    "username %s password %s\n" % (passWord, passWord), 
#DLB    "enable secret %s\n" % passWord,
    "aaa new-model\n",
#DLB    "ntp server %s\n" % ntpServer,
    "clock timezone %s\n" % timeZone,
    "clock summer-time %s recurring\n" % timeDaylight,
    "service timestamps debug datetime msec localtime\n",
    "service timestamps log datetime msec localtime\n",
    "ntp source %s\n" % intfMgmt,
    "ip multicast-routing\n",
    "ip multicast-routing distributed\n",
    "ip pim autorp listener\n",
]

routingCfgBegin = [
    "router eigrp %s\n" % eigrpName,
    "  address-family ipv4 unicast autonomous-system %d\n" % eigrpAs,
]

routingCfgEnd = [
    "  nsf\n"
    "  exit\n"
]


class DMVPN:

    class Crypto:

        class Ikev2:

            def __init__(self, number):
                self.number = number
                self.keyRing = "DMVPN-KEYRING-" + self.number
                self.profile = "FVRF-IKEv2-IWAN-TRANSPORT-" + self.number

        class Ipsec:

            def __init__(self, number):
                self.number = number
                self.profile = "DMVPN-PROFILE-TRANSPORT-" + self.number
                self.transform = "AES256/SHA/TRANSPORT"
                self.mode = "transport"
                self.windowSize = 512

        def __init__(self, number):
            self.number = number
            self.ikev2 = self.Ikev2(number)
            self.ipsec = self.Ipsec(number)
            

    def __init__(self, description, number, kind, address, mask, prefix,
                 wildcard):
        self.description = description
        self.kind = kind
        self.number = number
        self.primary = False
        self.ca = False      # Don't configure CA, pre-shared keys only
        self.name = "IWAN-TRANSPORT-" + self.number
        self.tunnelNumber = number
        self.nhrpNetID = number
        self.tunnelKey = number
        self.address = address
        self.mask = mask
        self.wildcard = wildcard
        self.routeHelloInterval = 20
        self.routeHoldTime = 60
        self.routeTag = prefix
        self.crypto = self.Crypto(number)

class Router:

    class Intf:

        def __init__(self, name, address, mask, wildcard, kind, rtType=None,
                     description=None, peerAddr=None, bandwidth=None):
            self.name = name
            self.kind = kind
            self.rtType = rtType
            self.address = address
            self.mask = mask
            self.wildcard = wildcard
            self.description = description
            self.peerAddr = peerAddr
            self.bandwidth = bandwidth

        def isTunnel(self):
            # DLB fix this
            return False

    def __init__(self, name, stub, routeProt=eigrp):
        self.intfs = [ ]  # underlay interfaces
        self.tunnelIntfs = [ ] # overlay interfaces
        self.name = name
        self.stub = stub
        self.CfgFileName = name + "Cfg.txt"
        self.routeProt = routeProt

    def getTunnelIntf(self, intf):
        for i in self.tunnelIntfs:
            if (intf.kind == i.kind):
                return i

        return intfNone

    def getLoopbackAddr(self):
        for i in self.intfs:
            if (i.kind == loopback):
                return i.address
        
        return "no loopback address"

    def createCommonCfg(self):
        print "Write Global Router Configuration to %s\n" % self.CfgFileName
        f = open(self.CfgFileName, "w")
        f.writelines(CommonRtrCfg)

        for i in self.intfs:
            for d in DMVPNs:
                if (i.kind == d.kind):
                    f.write("ip route vrf %s 0.0.0.0 %s\n" %
                            (d.name, i.peerAddr))
                    f.write("vrf definition %s\n" % d.name)
                    f.write("  address-family ipv4\n")        

        f.close()
        
    def createIntfCfg(self):
        print "Write Interface Configuration to %s\n" % self.CfgFileName
        f = open(self.CfgFileName, "a")

        for i in self.intfs:
            f.write("interface " + i.name + "\n")
            if (i.description != None):
                f.write("  description %s\n" % i.description)

            f.write("  ip address %s %s\n" % (i.address, i.mask))

            if (i.bandwidth != None):
                f.write("  bandwidth %s\n" % i.bandwidth)
            
            for d in DMVPNs:
                if (i.kind == d.kind):
                    f.write("  vrf forwarding %s\n" % d.name)
            
            if (i.isTunnel()):
                f.write("  no ip redirects\n")
                f.write("  ip mtu 1400\n")
                f.write("  ip tcp adjust-mss 1360\n")
                f.write("  ip pim nbma-mode\n")

            f.writelines(CommonIntfCfg)

        f.close()

    def createRoutingCfg(self):

        print "Write Routing Configuration to %s\n" % self.CfgFileName
        if (self.routeProt == None):
            print "!!! Nothing to write\n"
            return

        f = open(self.CfgFileName, "a")
        
        
        f.writelines(routingCfgBegin)

        # Create interface specific commands

        for i in self.intfs:
            #  No routing for mgmt interface.
            print "File name %s interface name %s" % (self.CfgFileName, i.name)
            if (i.kind == loopback):
                continue

            routingIntf = i.name

            routingIntfPassive = ""
            if (i.rtType != passive):
                routingIntfPassive = "no "
    
            f.write("    af-interface %s\n" % routingIntf)
            f.write("      %spassive-interface\n" % routingIntfPassive)
            f.write("      authentication mode md5\n")
            f.write("      authentication key-chain %s\n" % lanKey)

            if i.isTunnel():
                f.write("      hello-interval %s\n" % self.routeHelloInterval)
                f.write("      hold-time %s\n" % self.routeHoldTime)
                f.write("      no split-horizon\n")

            f.write("    exit\n")

        for i in self.tunnelIntfs:
            f.write("    af-interface %s\n" % i.name)
            f.write("      passive-interface\n")
            f.write("      authentication mode md5\n")
            f.write("      authentication key-chain %s\n" % lanKey)

            f.write("      hello-interval %s\n" % self.routeHelloInterval)
            f.write("      hold-time %s\n" % self.routeHoldTime)
            f.write("      no split-horizon\n")

            f.write("    exit\n")

        #  Write network commands
        
        for i in self.intfs:
            f.write("  network %s %s\n" % (i.address, i.wildcard))
            
        for i in self.tunnelIntfs:
            f.write("  network %s %s\n" % (i.address, i.wildcard))

        eigrpStub = ""
        if (self.stub != true):
            eigrpStub = "no "

        f.write("  %seigrp stub\n" % eigrpStub)

        f.write("  eigrp router-id %s\n" % self.getLoopbackAddr())

        f.writelines(routingCfgEnd)
        
        f.close()

    def createCryptoCfg(self):
        print "Write Crypto Configuration to %s\n" % self.CfgFileName
        f = open(self.CfgFileName, "a")

        #  This loop assumes one physical interface kind for each DMVPN
        for i in self.intfs:
            for d in DMVPNs:
                if (i.kind == d.kind):
                            
                    f.write("crypto ikev2 keyring %s\n" %
                            d.crypto.ikev2.keyRing)
                    f.write("  peer any\n")
                    f.write("    address 0.0.0.0 0.0.0.0\n")
                    f.write("    pre-shared-key %s\n" % passWord)
                    f.write("  exit\n")
                    f.write("exit\n")

                    f.write("crypto ikev2 profile %s\n" % 
                            d.crypto.ikev2.profile)
                    f.write("  match fvrf %s\n" % d.name)
                    f.write("match identity remote address 0.0.0.0\n")
                    f.write("authentication remote pre-share\n")
                    f.write("authentication local pre-share\n")
                    f.write("keyring local %s\n" % d.crypto.ikev2.keyRing)
                    f.write("! DLB Add this in later pki trustpoing IWAN-CA\n")

                    f.write("crypto ipsec transform-set %s esp-aes 256 esp-sha-hmac\n" %
                            d.crypto.ipsec.transform)
                    f.write("  mode transport\n")
                    f.write("  exit\n")

                    f.write("crypto ipsec profile %s\n" %
                            d.crypto.ipsec.profile)
                    f.write("  set transform-set %s\n" % 
                            d.crypto.ipsec.transform)
                    f.write("  set ikev2-profile %s\n" % d.crypto.ikev2.profile)
                    f.write("crypto ipsec security-assocation replay window-size %s\n" %
                            d.crypto.ipsec.windowSize)

                    f.write("interface %s\n" % self.getTunnelIntf(i).name)
                    f.write("  tunnel source %s\n" % i.name)
                    f.write("  tunnel mode gre multipoint\n")
                    f.write("  tunnel key %s\n" % d.tunnelKey)
                    f.write("  tunnel vrf %s\n" % d.name)
                    f.write("  tunnel protection ipsec profile %s\n" % 
                            d.crypto.ipsec.profile)
                    f.write("  ip nhrp authentication %s\n" % passWord)
                    f.write("  ip nhrp map multicast dynamic\n")
                    f.write("  ip nhrp network-id %s\n" % d.nhrpNetID)
                    f.write("  ip nhrp holdtime %s\n" % d.routeHoldTime)
                    f.write("  ip nhrp redirect\n")

        f.close()
        

    def createCfgFile(self):
        self.createCommonCfg() # Always call this first to overwrite file
        self.createIntfCfg()
        self.createRoutingCfg()
        self.createCryptoCfg()

def printFile(fname):
    f = open(fname, "r")
    print fname
    for line in f:
        print line

    f.close()

print "Create configuration files for Test-3.virl"

DMVPNs = [ ]

intfNone = Router.Intf("None", None, None, None, None, None,
                       "No interface")

def main():

    Routers = [ ]

    # Enteprise Routers

    dmvpn = DMVPN("MPLS primary", "100", mpls,
                  "10.6.34.1", "255.255.254.0", "10.6.34.0", "0.0.1.255")
    dmvpn.primary = True
    DMVPNs.append(dmvpn)

    dmvpn = DMVPN("INET secondary", "200", inet,
                  "10.6.36.1", "255.255.254.0", "10.6.36.0", "0.0.1.255")

    rtr = Router("Dist", false)
    rtr.intfs.append(rtr.Intf("gig 0/1", "10.0.0.29", "255.255.255.252",
                          "0.0.0.3",
                              lan, active, "to BR1"))
    rtr.intfs.append(rtr.Intf("gig 0/2", "10.0.128.5", "255.255.255.252",
                          "0.0.0.3",
                              lan, active, "to BR2"))
    rtr.intfs.append(rtr.Intf("gig 0/3", "10.0.128.2", "255.255.255.252",
                              "0.0.0.3",
                              lan, passive, "to SRVR1"))
    rtr.intfs.append(rtr.Intf("gig 0/4", "10.0.0.1", "255.255.255.252",
                              "0.0.0.3",
                              lan, active, "to MC"))
    rtr.intfs.append(rtr.Intf("Loopback 0", "192.168.0.1", "255.255.255.255",
                              "0.0.0.0",
                              loopback, passive))
    Routers.append(rtr)

    rtr = Router("MC", true)
    rtr.intfs.append(rtr.Intf("gig 0/1", "10.0.0.2", "255.255.255.252",
                              "0.0.0.3", lan, active, "to Dist"))
    rtr.intfs.append(rtr.Intf("Loopback 0", "192.168.0.9", "255.255.255.255",
                              "0.0.0.0", loopback, passive))
    Routers.append(rtr)

    rtr = Router("BR1", false)
    rtr.intfs.append(rtr.Intf("gig 0/1", "10.0.0.30", "255.255.255.252",
                              "0.0.0.3", lan, active, "to Dist"))
    rtr.intfs.append(rtr.Intf("gig 0/3", "20.0.0.2", "255.255.255.252",
                              "0.0.0.3", mpls, passive, "to MPLS", "20.0.0.1"))
    rtr.intfs.append(rtr.Intf("Loopback 0", "192.168.0.2", "255.255.255.255",
                              "0.0.0.0",
                              loopback, passive))

    Routers.append(rtr)

    rtr = Router("BR2", false)
    rtr.intfs.append(rtr.Intf("gig 0/1", "10.0.128.6", "255.255.255.252",
                              "0.0.0.3", lan, active, "to Dist"))
    rtr.intfs.append(rtr.Intf("gig 0/2", "30.0.0.6", "255.255.255.252",
                              "0.0.0.3", inet, passive, "to INET", "30.0.0.5"))
    rtr.intfs.append(rtr.Intf("Loopback 0", "192.168.0.5", "255.255.255.255",
                              "0.0.0.0", loopback, passive))
    Routers.append(rtr)

    rtr = Router("MCBR3", true)
    rtr.intfs.append(rtr.Intf("gig 0/1", "30.0.0.2", "255.255.255.252",
                              "0.0.0.3", inet, passive, "to INET", "30.0.0.1"))
    rtr.intfs.append(rtr.Intf("gig 0/2", "10.0.128.10", "255.255.255.252",
                              "0.0.0.3", lan, passive, "to CLNT"))
    rtr.intfs.append(rtr.Intf("gig 0/3", "20.0.0.6", "255.255.255.252",
                              "0.0.0.3", mpls, passive, "to MPLS", "20.0.0.5"))
    rtr.intfs.append(rtr.Intf("Loopback 0", "192.168.0.6", "255.255.255.255",
                              "0.0.0.0", loopback, passive))
    Routers.append(rtr)



    # SP Routers

    rtr = Router("MPLS", false, None)
    rtr.intfs.append(rtr.Intf("gig 0/1", "20.0.0.1", "255.255.255.252",
                              "0.0.0.3", lan, passive, "to BR1"))
    rtr.intfs.append(rtr.Intf("gig 0/2", "20.0.0.5", "255.255.255.252",
                              "0.0.0.3", lan, passive, "to MCBR3"))
    rtr.intfs.append(rtr.Intf("Loopback 0", "20.0.0.9", "255.255.255.255",
                              "0.0.0.0", loopback, passive))
    Routers.append(rtr)

    rtr = Router("INET", false, None)
    rtr.intfs.append(rtr.Intf("gig 0/1", "30.0.0.1", "255.255.255.252",
                              "0.0.0.3", lan, passive, "to MCBR3"))
    rtr.intfs.append(rtr.Intf("gig 0/2", "30.0.0.5", "255.255.255.252",
                              "0.0.0.3", lan, passive, "to BR2"))
    rtr.intfs.append(rtr.Intf("Loopback 0", "30.0.0.9", "255.255.255.255",
                              "0.0.0.0", loopback, passive))
    Routers.append(rtr)

    for r in Routers:
        r.createCfgFile()
#        printFile(r.CfgFileName)


if __name__=='__main__':
    main()
