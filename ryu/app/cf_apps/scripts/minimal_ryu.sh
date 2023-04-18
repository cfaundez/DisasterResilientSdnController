#!/bin/sh

# ./ryu/app/cf_apps/scripts/minimal_ryu.sh

export PYTHONPATH=$PYTHONPATH:.

cd ~/ryu

#./bin/ryu-manager --observe-links \
#ryu.app.cf_apps.disaster_monitor_app \
#ryu.app.cf_apps.id_manager_app \
#ryu.app.cf_apps.prioritization_app


./bin/ryu-manager --observe-links \
ryu.app.cf_apps.id_manager_app \
ryu.app.cf_apps.prioritization_app \
ryu.app.cf_apps.disaster_monitor_app