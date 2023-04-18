#!/usr/bin/python

from mininet.net import Mininet
from mininet.node import Controller, RemoteController, OVSController
from mininet.node import CPULimitedHost, Host, Node
from mininet.node import OVSKernelSwitch, UserSwitch
from mininet.node import IVSSwitch
from mininet.cli import CLI
from mininet.log import setLogLevel, info
from mininet.link import TCLink, Intf
from subprocess import call
import os
import time
import subprocess
from datetime import datetime

def myNetwork():

    net = Mininet( topo=None,
                   build=False,
                   ipBase='10.0.0.0/8',
                   autoSetMacs=True)

    info( '*** Adding controller\n' )
    c0=net.addController(name='c0',
                      controller=RemoteController,
                      ip='127.0.0.1',
                      protocol='tcp',
                      port=6633)

    info( '*** Add switches\n')
    s2 = net.addSwitch('s2', cls=OVSKernelSwitch, protocols=['OpenFlow13']) # default datapath='kernel',
    s1 = net.addSwitch('s1', cls=OVSKernelSwitch, protocols=['OpenFlow13'])


    info( '*** Add hosts\n')
    ECS_src = net.addHost('ECS_src', cls=Host, ip='10.0.0.1', defaultRoute=None)
    D_src = net.addHost('D_src', cls=Host, ip='10.0.0.2', defaultRoute=None)
    ND_src = net.addHost('ND_src', cls=Host, ip='10.0.0.3', defaultRoute=None)
    ECS_dst = net.addHost('ECS_dst', cls=Host, ip='10.0.0.4', defaultRoute=None)
    D_dst = net.addHost('D_dst', cls=Host, ip='10.0.0.5', defaultRoute=None)
    ND_dst = net.addHost('ND_dst', cls=Host, ip='10.0.0.6', defaultRoute=None)


    link_bw = 100

    info( '*** Add links\n')
    ECS_srcs1 = {'bw':link_bw}
    net.addLink(ECS_src, s1, cls=TCLink , **ECS_srcs1)
    D_srcs1 = {'bw':link_bw}
    net.addLink(D_src, s1, cls=TCLink , **D_srcs1)
    ND_srcs1 = {'bw':link_bw}
    net.addLink(ND_src, s1, cls=TCLink , **ND_srcs1)
    ECS_dsts2 = {'bw':link_bw}
    net.addLink(ECS_dst, s2, cls=TCLink , **ECS_dsts2)
    D_dsts2 = {'bw':link_bw}
    net.addLink(D_dst, s2, cls=TCLink , **D_dsts2)
    ND_dsts2 = {'bw':link_bw}
    net.addLink(ND_dst, s2, cls=TCLink , **ND_dsts2)
    s1s2 = {'bw':link_bw}
    net.addLink(s1, s2, cls=TCLink , **s1s2)

    info( '*** Starting network\n')
    net.build()
    info( '*** Starting controllers\n')
    for controller in net.controllers:
        controller.start()

    info( '*** Starting switches\n')
    net.get('s2').start([c0])
    net.get('s1').start([c0])

    info('\n*** Setting OVS config (required for meters) on new terminal\n')

    SET_METER_SUPPORT = False
    if SET_METER_SUPPORT:

        proc = subprocess.Popen(
            ["xterm", "-hold", "-e", "~/ryu/ryu/app/cf_apps/scripts/set_bridges.sh"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE)
        proc.poll()
        time.sleep(2)

    # for switch in net.switches:
    #     if not switch.batch:
    #         for intf in switch.intfList():
    #             switch.TCReapply(intf)
    #             print("hice algo: " + switch.name + " + " + str(intf))


    info( '*** Launching Ryu on new terminal\n')

    proc = subprocess.Popen(
        ["xterm", "-hold", "-e", "~/ryu/ryu/app/cf_apps/scripts/minimal_ryu.sh"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE)
    proc.poll()

    time.sleep(6)

    # Test: set tx queue len
    # proc = subprocess.Popen(
    #     ["ifconfig", "s1-eth4", "txqueuelen", "20000"],
    #     stdout=subprocess.PIPE,
    #     stderr=subprocess.PIPE)
    # proc.poll()
    # time.sleep(1)

    # Test ping reachability

    # net.pingAll()

    # Ping specific routes
    net.ping([ECS_src, ECS_dst])
    net.ping([D_src, D_dst])
    net.ping([ND_src, ND_dst])


    time.sleep(1)

    info( '*** Start iPerf servers\n')
    serverCommand(ECS_dst)
    serverCommand(D_dst)
    serverCommand(ND_dst)

    time.sleep(1)

    info( '*** Start iPerf clients\n')

    clientCommand(ND_src, ND_dst, "100")
    clientCommand(D_src, D_dst, "100")
    clientCommand(ECS_src, ECS_dst, "100")


    CLI(net)
    net.stop()

# EXP_DIR = "/home/ubuntu/Desktop/Experiments/Minimal-ECS-D-ND/Results/OF13-NormalOp/"
#EXP_DIR = "/home/ubuntu/Desktop/Experiments/Minimal-ECS-D-ND/Results/OF13-DisasterInSitu/"
# EXP_DIR = "/home/ubuntu/Desktop/Experiments/Minimal-ECS-D-ND/Results/OF13-DisasterInSitu-100-100-100-33-33-33/"
# EXP_DIR = "/home/ubuntu/Desktop/Experiments/Minimal-ECS-D-ND/Results/OF13-DisasterInSitu-20-100-100-20-50-30/"
# EXP_DIR = "/home/ubuntu/Desktop/Experiments/Minimal-ECS-D-ND/Results/OF13-NormalOp-33-33-33/"
# EXP_DIR = "/home/ubuntu/Desktop/Experiments/Minimal-ECS-D-ND/Results/OF13-NormalOp-100-100-100-new/"
EXP_DIR = "/home/ubuntu/Desktop/Experiments/Minimal-ECS-D-ND/Results/OF13-NormalOp-100-100-100-new-no-meter-supp/"
# EXP_DIR = "/home/ubuntu/Desktop/Experiments/Minimal-ECS-D-ND/Results/OF13-NormalOp-50-50-50-link50/"

date_str = datetime.now().strftime("%Y_%m_%d-%I_%M_%S_%p")

def serverCommand(hostNode):
    # hostNode.cmdPrint("iperf -s -u | tee " + EXP_DIR + date_str + "-server-" + hostNode.name + ".log &")
    hostNode.cmdPrint("iperf -s -u &")


def clientCommand(hostNodeSrc, hostNodeDst, BW):
    hostNodeSrc.cmdPrint(
        "iperf -c " + hostNodeDst.IP() + " -b " + BW + "MB -t 10 | tee " + EXP_DIR + date_str + "-client-" + hostNodeSrc.name + ".log &")


if __name__ == '__main__':
    setLogLevel( 'info' )
    myNetwork()

