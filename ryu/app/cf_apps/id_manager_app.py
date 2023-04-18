from ryu.controller.handler import set_ev_cls
from ryu.app.cf_apps.disaster_monitor_libs.event import EventDisasterInSitu
from ryu.app.cf_apps.libs.logging import Loggable
from ryu.base import app_manager
from ryu.ofproto import ofproto_v1_3
from ryu.topology.api import get_all_switch
from ryu.topology.switches import Switches
from ryu.app.cf_apps.mod_learning_switch import L2LearningSwitch

from ryu.controller import ofp_event
from ryu.controller.handler import MAIN_DISPATCHER
from ryu.lib.packet import packet, ethernet, ipv4
from ryu.ofproto import ether
import array

from ryu.app.cf_apps.mod_learning_switch import DEFAULT_ROUTING_TABLE_ID  # CFAUNDEZ ADD

# TODO
# on start
# table 0: default togo to routing table

# OWNED_IPs_DB
# DISASTER_IPs_DB

# on disaster (in situ or ex situ)
# add default ECS flows, togo table 1 (prio table with meters)
#

# on disaster (in situ)
# add default id flows for owned IPs, togo table 1 (prio table with meters)
# add on demand id flows for not owned packets, togo table 1 (prio table with meters)

# on disaster (ex situ)
# add default id flows for disaster IPs if DB provided (??), togo table 1 (prio table with meters)
# add on demand id flows for not owned packets if DB provided (??), togo table 1 (prio table with meters)
#
from ryu.topology.event import EventSwitchEnter

# Table IDs
ID_ATTACHMENT_TABLE = 0
PRIORITIZATION_TABLE = 10  # TODO modify
ROUTING_TABLE = 20

ECS_ID = 1
DISASTER_ID = 2
NON_DISASTER_ID = 3

ECS_FLOW_PRIORITY = 2
DISASTER_FLOW_PRIORITY = 1
OTHER_FLOW_PRIORITY = 0  # lowest

# Priority of flow entries
HAS_ID_FLOW_ENTRY_PRIO = 10
ATTACH_ECS_ID_FLOW_ENTRY_PRIO = 9
ATTACH_DISASTER_ID_FLOW_ENTRY_PRIO = 8
ATTACH_NON_DISASTER_ID_FLOW_ENTRY_PRIO = 7
NO_ID_FLOW_ENTRY_PRIO = 1
TABLE_MISS_FLOW_ENTRY_PRIO = 0

# Controller ID
CONTROLLER_ID = 0


# Manages ID attachment table
class IdManagerApp(app_manager.RyuApp, Loggable):
    OFP_VERSIONS = [ofproto_v1_3.OFP_VERSION]
    _CONTEXTS = {'switches': Switches,
                 'mod_learning_switch': L2LearningSwitch}  # name has to be the same in all contexts

    ECS_DB = ["10.0.0.1"]

    DISASTER_IP_ADDRESS_DB = ["10.0.0.2"]
    # DISASTER_IP_ADDRESS_DB = []

    def __init__(self, *args, **kwargs):
        super(IdManagerApp, self).__init__(*args, **kwargs)
        self.print_verbose_log("Started app")

        # 1. define reference to other apps
        self.switches_app = kwargs['switches']  # to obtain switch info
        self.learning_switch_app = kwargs['mod_learning_switch']  # to obtain table id of routing

        self.assignment_mode = False

    # Ready
    @set_ev_cls(EventSwitchEnter)
    def switch_enter_handler(self, event):
        self.print_verbose_log("Received event: EventSwitchEnter")
        datapath = event.switch.dp
        # set table miss flow
        self.set_flow_entry_table_miss(datapath)
        # if it connected when assignment mode already started, set the default flows
        if self.assignment_mode:
            self.start_assignment_mode_for_dp(datapath)

    # Ready
    @set_ev_cls(EventDisasterInSitu)
    def disaster_in_situ_handler(self, ev):
        self.print_verbose_log("Received event: EventDisasterInSitu")
        if not self.assignment_mode:
            self.assignment_mode = True
            self.start_assignment_mode()

            # add host db into disaster db

    @set_ev_cls(ofp_event.EventOFPPacketIn, MAIN_DISPATCHER)
    def packet_in_handler(self, ev):
        pkt_in = ev.msg

        if self.packet_in_ignore(pkt_in):
            return

        datapath = pkt_in.datapath
        ofp = datapath.ofproto
        ofp_parser = datapath.ofproto_parser

        pkt = packet.Packet(pkt_in.data)
        print ("Packet in")
        # print (str(pkt))

        ip = pkt.get_protocol(ipv4.ipv4)

        self.set_dynamic_flow_entry(datapath, ip.src, ip.dst)

    # Determines if a packet-in message received should be processed
    def packet_in_ignore(self, pkt_in):

        # Ignore if packet-in was not emitted by ID attachment table
        if pkt_in.table_id != ID_ATTACHMENT_TABLE:
            return True

        # Ignore if not in assignment mode (should not reach this case)
        if not self.assignment_mode:
            self.print_verbose_log("Warning: Received packet-in from IP attachment table in non-assigment mode")
            return True

        pkt = packet.Packet(pkt_in.data)
        eth = pkt.get_protocols(ethernet.ethernet)[0]

        # Ignore if packet was non IP (should not reach this case)
        if eth.ethertype != ether.ETH_TYPE_IP:
            self.print_verbose_log("Warning: Ignored non IP packet-in from IP attachment table")
            return True

        # Should be processed, do not ignore
        return False




    # TODO other event changes


    # Ready
    def start_assignment_mode(self):
        switches_list = get_all_switch(self.switches_app)  # request list of switches, own copy

        for switch in switches_list:
            datapath = switch.dp
            self.start_assignment_mode_for_dp(datapath)

    # Ready
    def start_assignment_mode_for_dp(self, datapath):
        self.set_flow_entries_has_id(datapath)
        self.set_flow_entries_attach_ecs_id(datapath)
        self.set_flow_entry_no_id(datapath)

    # Ready
    def set_flow_entry_table_miss(self, datapath):
        parser = datapath.ofproto_parser
        match = parser.OFPMatch()  # matches everything
        instruction1 = parser.OFPInstructionGotoTable(table_id=ROUTING_TABLE)
        instruction_list = list()
        instruction_list.append(instruction1)
        flow_mod = self.create_flow_mod(datapath, match, instruction_list, TABLE_MISS_FLOW_ENTRY_PRIO)

        datapath.send_msg(flow_mod)

        self.print_verbose_log("Table miss flow entry set")

    # Ready
    def set_flow_entries_has_id(self, datapath):
        parser = datapath.ofproto_parser
        match_ecs = parser.OFPMatch(tunnel_id=ECS_ID)
        match_disaster = parser.OFPMatch(tunnel_id=DISASTER_ID)
        match_non_disaster = parser.OFPMatch(tunnel_id=NON_DISASTER_ID)

        instruction = parser.OFPInstructionGotoTable(table_id=PRIORITIZATION_TABLE)
        instruction_list = list()
        instruction_list.append(instruction)

        has_id_ecs_flow_mod = self.create_flow_mod(datapath, match_ecs, instruction_list, HAS_ID_FLOW_ENTRY_PRIO)
        has_id_disaster_flow_mod = self.create_flow_mod(datapath, match_disaster, instruction_list,
                                                        HAS_ID_FLOW_ENTRY_PRIO)
        has_id_non_disaster_flow_mod = self.create_flow_mod(datapath, match_non_disaster, instruction_list,
                                                            HAS_ID_FLOW_ENTRY_PRIO)

        datapath.send_msg(has_id_ecs_flow_mod)
        datapath.send_msg(has_id_disaster_flow_mod)
        datapath.send_msg(has_id_non_disaster_flow_mod)

        self.print_verbose_log("Has ID flow entries set")

    # Ready
    def set_flow_entries_attach_ecs_id(self, datapath):
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser

        for ecs_ipv4_address in self.ECS_DB:
            match_src = parser.OFPMatch(eth_type=0x0800, ipv4_src=ecs_ipv4_address)
            match_dst = parser.OFPMatch(eth_type=0x0800, ipv4_dst=ecs_ipv4_address)

            action_list = [parser.OFPActionSetField(tunnel_id=ECS_ID)]  # set ECS ID

            instruction1 = parser.OFPInstructionActions(ofproto.OFPIT_APPLY_ACTIONS, action_list)  # apply set ECS ID
            instruction2 = parser.OFPInstructionGotoTable(table_id=PRIORITIZATION_TABLE)

            instruction_list = [instruction1, instruction2]

            src_flow_mod = self.create_flow_mod(datapath, match_src, instruction_list, ATTACH_ECS_ID_FLOW_ENTRY_PRIO)
            dst_flow_mod = self.create_flow_mod(datapath, match_dst, instruction_list, ATTACH_ECS_ID_FLOW_ENTRY_PRIO)

            datapath.send_msg(src_flow_mod)
            datapath.send_msg(dst_flow_mod)

        self.print_verbose_log("Attach ECS ID flow entries set. Total IPs: " + str(len(self.ECS_DB)))

    # Ready
    def set_flow_entry_no_id(self, datapath):
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser
        match = parser.OFPMatch(eth_type=0x0800)  # matches everything ipv4
        action_list = [parser.OFPActionOutput(ofproto.OFPP_CONTROLLER)]  # send packet in
        instruction_list = [parser.OFPInstructionActions(ofproto.OFPIT_APPLY_ACTIONS, action_list)]

        flow_mod = self.create_flow_mod(datapath, match, instruction_list, NO_ID_FLOW_ENTRY_PRIO)

        datapath.send_msg(flow_mod)

        self.print_verbose_log("No ID flow entry set")

    # Ready
    def set_dynamic_flow_entry(self, datapath, src_ip, dst_ip):
        none_in_disaster_db = True

        if self.ip_in_disaster_ip_db(src_ip):
            self.set_dynamic_flow_entry_attach_disaster_id(datapath, src_ip)
            none_in_disaster_db = False
        if self.ip_in_disaster_ip_db(dst_ip):
            self.set_dynamic_flow_entry_attach_disaster_id(datapath, dst_ip)
            none_in_disaster_db = False

        # Only if both ips are non disaster we set the dynamic flow entry non disaster,
        # otherwise if a different flow that has one known non-disaster ip but another unknown
        # ip will not generate a packet-in to analyze the unknown one
        if none_in_disaster_db:
            self.set_dynamic_flow_entry_attach_non_disaster_id(datapath, src_ip, dst_ip)

    # Ready
    def set_dynamic_flow_entry_attach_disaster_id(self, datapath, ip):
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser

        match_src = parser.OFPMatch(eth_type=0x0800, ipv4_src=ip)
        match_dst = parser.OFPMatch(eth_type=0x0800, ipv4_dst=ip)

        action_list = [parser.OFPActionSetField(tunnel_id=DISASTER_ID)]  # set DISASTER ID

        instruction1 = parser.OFPInstructionActions(ofproto.OFPIT_APPLY_ACTIONS, action_list)  # apply set DISASTER ID
        instruction2 = parser.OFPInstructionGotoTable(table_id=PRIORITIZATION_TABLE)

        instruction_list = [instruction1, instruction2]

        src_flow_mod = self.create_flow_mod(datapath, match_src, instruction_list, ATTACH_DISASTER_ID_FLOW_ENTRY_PRIO)
        dst_flow_mod = self.create_flow_mod(datapath, match_dst, instruction_list, ATTACH_DISASTER_ID_FLOW_ENTRY_PRIO)

        datapath.send_msg(src_flow_mod)
        datapath.send_msg(dst_flow_mod)

    # Ready
    def set_dynamic_flow_entry_attach_non_disaster_id(self, datapath, src_ip, dst_ip):
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser

        match = parser.OFPMatch(eth_type=0x0800, ipv4_src=src_ip, ipv4_dst=dst_ip) # match both ips

        action_list = [parser.OFPActionSetField(tunnel_id=NON_DISASTER_ID)]  # set NON DISASTER ID

        instruction1 = parser.OFPInstructionActions(ofproto.OFPIT_APPLY_ACTIONS, action_list)  # apply set NON DISASTER ID
        instruction2 = parser.OFPInstructionGotoTable(table_id=PRIORITIZATION_TABLE)

        instruction_list = [instruction1, instruction2]

        flow_mod = self.create_flow_mod(datapath, match, instruction_list, ATTACH_NON_DISASTER_ID_FLOW_ENTRY_PRIO)

        datapath.send_msg(flow_mod)

    # Modify if disaster ip db changes structure
    def ip_in_disaster_ip_db(self, ip):
        return ip in self.DISASTER_IP_ADDRESS_DB


    # ---------


    def create_flow_mod(self, datapath, match, instruction_list, flow_priority):
        ofp = datapath.ofproto
        ofproto_parser = datapath.ofproto_parser
        flow_mod = ofproto_parser.OFPFlowMod(datapath,
                                             table_id=ID_ATTACHMENT_TABLE,
                                             command=ofp.OFPFC_ADD,
                                             priority=flow_priority,
                                             match=match,
                                             instructions=instruction_list)
        return flow_mod






