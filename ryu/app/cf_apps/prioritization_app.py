from ryu.lib.packet.packet import Packet
from ryu.lib.packet.ethernet import ethernet
from ryu.lib.packet.ipv4 import ipv4
from ryu.controller import ofp_event
from ryu.ofproto import ofproto_v1_3
from ryu.app.cf_apps.disaster_monitor_libs.event import EventDisasterInSitu
from ryu.controller.handler import set_ev_cls, MAIN_DISPATCHER
from ryu.app.cf_apps.libs.logging import Loggable
from ryu.base import app_manager
from ryu.app.cf_apps.mod_learning_switch import L2LearningSwitch

from ryu.topology.api import get_all_switch
from ryu.topology.switches import Switches

ECS_METER_ID = 1
DISASTER_METER_ID = 2
OTHER_METER_ID = 3

ECS_RATE = 20 * 1000  # KBPS
DISASTAR_RATE = 50 * 1000
OTHER_RATE = 30 * 1000

ECS_ID = 1
DISASTER_ID = 2
OTHER_ID = 3

METER_TABLE = 10
ROUTING_TABLE = 20


# # enum ofp_meter_flags
# OFPMF_KBPS = 1 << 0     # Rate value in kb/s (kilo-bit per second).
# OFPMF_PKTPS = 1 << 1    # Rate value in packet/sec.
# OFPMF_BURST = 1 << 2    # Do burst size.
# OFPMF_STATS = 1 << 3    # Collect statistics.

# apply meters
class PrioritizationApp(app_manager.RyuApp, Loggable):
    OFP_VERSIONS = [ofproto_v1_3.OFP_VERSION]
    _CONTEXTS = {'switches': Switches,
                 'mod_learning_switch': L2LearningSwitch}  # name has to be the same in all contexts

    def __init__(self, *args, **kwargs):
        super(PrioritizationApp, self).__init__(*args, **kwargs)
        self.print_verbose_log("Started app")

        self.switches_app = kwargs['switches']  # to obtain switch info
        self.learning_switch_app = kwargs['mod_learning_switch']  # to obtain table id of routing

    @set_ev_cls(EventDisasterInSitu)
    def disaster_in_situ_handler(self, event):
        self.print_verbose_log("Received event: " + str(event))

        switches_list = get_all_switch(self.switches_app)  # request list of switches, own copy

        # prioritize
        # set meters
        self.set_default_meters(switches_list)
        # set flows go to
        self.set_default_meter_flows(switches_list)

    def set_default_meters(self, switches_list):
        for switch in switches_list:
            datapath = switch.dp

            self.set_meter(datapath, OTHER_METER_ID, OTHER_RATE)
            self.set_meter(datapath, DISASTER_METER_ID, DISASTAR_RATE)
            self.set_meter(datapath, ECS_METER_ID, ECS_RATE)

    def set_meter(self, datapath, meter_id, meter_rate):
        parser = datapath.ofproto_parser
        ofproto = datapath.ofproto

        # Meter for OTHER_ID
        band = parser.OFPMeterBandDrop(rate=meter_rate, burst_size=0)
        bands = [band]

        meter_mod = parser.OFPMeterMod(datapath,
                                       command=ofproto.OFPMC_ADD,
                                       flags=ofproto.OFPMF_KBPS,
                                       meter_id=meter_id,
                                       bands=bands)

        # print(meter_mod)

        datapath.send_msg(meter_mod)


    def set_default_meter_flows(self, switches_list):
        for switch in switches_list:
            datapath = switch.dp

            self.set_meter_flow(datapath, OTHER_ID, OTHER_METER_ID)
            self.set_meter_flow(datapath, DISASTER_ID, DISASTER_METER_ID)
            self.set_meter_flow(datapath, ECS_ID, ECS_METER_ID)


    def set_meter_flow(self, datapath, id, meter_id):
        parser = datapath.ofproto_parser
        ofproto = datapath.ofproto

        # flow for OTHER_ID
        match = parser.OFPMatch(tunnel_id=id)
        instruction_meter = parser.OFPInstructionMeter(meter_id=meter_id)
        instruction_goto = parser.OFPInstructionGotoTable(table_id=ROUTING_TABLE)

        instruction_list = list()
        instruction_list.append(instruction_meter)
        instruction_list.append(instruction_goto)

        flow_mod = parser.OFPFlowMod(datapath,
                                     table_id=METER_TABLE,
                                     command=ofproto.OFPFC_ADD,
                                     priority=0,
                                     match=match,
                                     instructions=instruction_list)

        # print(flow_mod)

        datapath.send_msg(flow_mod)
