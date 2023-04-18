#!/bin/sh

# ./ryu/ryu/app/cf_apps/scripts/set_mininet.sh

alias sudo='sudo LD_LIBRARY_PATH="$LD_LIBRARY_PATH"'


#export PATH=$PATH:/usr/local/share/openvswitch/scripts
#export DB_SOCK=/usr/local/var/run/openvswitch/db.sock
#sudo ovs-vsctl --no-wait set Open_vSwitch . other_config:dpdk-init=true
#sudo /usr/local/share/openvswitch/scripts/ovs-ctl --no-ovsdb-server --db-sock="$DB_SOCK" start

sudo mn -c

sudo /usr/local/share/openvswitch/scripts/ovs-ctl stop

sudo /usr/local/share/openvswitch/scripts/ovs-ctl start

# works with set_bridges
#sudo mn --topo linear,4 --mac --controller remote --switch ovsk

#sudo -E python ~/Desktop/linear4.py

# works with set_bridges
sudo mn --topo=tree,depth=7,fanout=2 --mac --controller remote --switch ovsk



#sudo mn --custom ~/Desktop/regularGrid4.py --mac --controller remote --switch ovsk
#sudo -E python ~/Desktop/regularGrid4.py
