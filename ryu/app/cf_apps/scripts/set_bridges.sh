#!/bin/sh

# ./ryu/ryu/app/cf_apps/scripts/set_bridges.sh

alias sudo='sudo LD_LIBRARY_PATH="$LD_LIBRARY_PATH"'

sudo ovs-vsctl set bridge s1 protocols=OpenFlow13 datapath_type=netdev
sudo ovs-vsctl set bridge s2 protocols=OpenFlow13 datapath_type=netdev
sudo ovs-vsctl set bridge s3 protocols=OpenFlow13 datapath_type=netdev
sudo ovs-vsctl set bridge s4 protocols=OpenFlow13 datapath_type=netdev
sudo ovs-vsctl set bridge s5 protocols=OpenFlow13 datapath_type=netdev
sudo ovs-vsctl set bridge s6 protocols=OpenFlow13 datapath_type=netdev
sudo ovs-vsctl set bridge s7 protocols=OpenFlow13 datapath_type=netdev
sudo ovs-vsctl set bridge s8 protocols=OpenFlow13 datapath_type=netdev
sudo ovs-vsctl set bridge s9 protocols=OpenFlow13 datapath_type=netdev
sudo ovs-vsctl set bridge s10 protocols=OpenFlow13 datapath_type=netdev
sudo ovs-vsctl set bridge s11 protocols=OpenFlow13 datapath_type=netdev
sudo ovs-vsctl set bridge s12 protocols=OpenFlow13 datapath_type=netdev
sudo ovs-vsctl set bridge s13 protocols=OpenFlow13 datapath_type=netdev
sudo ovs-vsctl set bridge s14 protocols=OpenFlow13 datapath_type=netdev
sudo ovs-vsctl set bridge s15 protocols=OpenFlow13 datapath_type=netdev