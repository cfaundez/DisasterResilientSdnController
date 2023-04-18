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

# sudo -E python /home/ubuntu/ryu/ryu/app/cf_apps/scripts/start-stop-switches.py

def stopSwitches():

    os.system("switch s1 stop")

    # info('*** Launching Mininet on new terminal\n')
    #
    # proc = subprocess.Popen(
    #     ["xterm", "-hold", "-e", "~/ryu/ryu/app/cf_apps/scripts/set_mininet.sh"],
    #     stdout=subprocess.PIPE,
    #     stderr=subprocess.PIPE)
    # proc.poll()
    #
    # time.sleep(8)
    #
    # info('\n*** Setting OVS config (required for meters) on new terminal\n')
    #
    # SET_METER_SUPPORT = False
    # if SET_METER_SUPPORT:
    #
    #     proc = subprocess.Popen(
    #         ["xterm", "-hold", "-e", "~/ryu/ryu/app/cf_apps/scripts/set_bridges.sh"],
    #         stdout=subprocess.PIPE,
    #         stderr=subprocess.PIPE)
    #     proc.poll()
    #     time.sleep(2)
    #
    # # for switch in net.switches:
    # #     if not switch.batch:
    # #         for intf in switch.intfList():
    # #             switch.TCReapply(intf)
    # #             print("hice algo: " + switch.name + " + " + str(intf))
    #
    #
    # info( '*** Launching Ryu on new terminal\n')
    #
    # proc = subprocess.Popen(
    #     ["xterm", "-hold", "-e", "~/ryu/ryu/app/cf_apps/scripts/minimal_ryu.sh"],
    #     stdout=subprocess.PIPE,
    #     stderr=subprocess.PIPE)
    # proc.poll()
    #
    # time.sleep(6)





if __name__ == '__main__':
    setLogLevel( 'info' )
    stopSwitches()

