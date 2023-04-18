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

# python test launcher
#sudo -E python /home/ubuntu/Desktop/Experiments/Minimal-ECS-D-ND/test2.py
sudo -E python /home/ubuntu/ryu/ryu/app/cf_apps/scripts/traffic-test-minimal.py