from ryu.app.cf_apps.disaster_monitor_libs.switch_counter import SwitchCounter
from ryu.app.cf_apps.libs.logging import Loggable
from ryu.app.cf_apps.disaster_monitor_libs.event import EventDisasterInSitu
from ryu.app.cf_apps.disaster_monitor_libs.state import NormalOperationState

from ryu.base import app_manager
from ryu.controller.handler import set_ev_cls


# Interface of interest to users
from ryu.topology.event import EventSwitchEnter, EventSwitchLeave
from ryu.topology.api import get_all_switch
from ryu.topology.switches import Switches


class DisasterMonitorApp(app_manager.RyuApp, Loggable):
    _EVENTS = [EventDisasterInSitu]  # list of events this app raises
    _CONTEXTS = {'switches': Switches}  # name has to be the same in all contexts

    def __init__(self, *args, **kwargs):
        super(DisasterMonitorApp, self).__init__(*args, **kwargs)
        self.print_verbose_log("Started app")

        self._state = None
        self.set_state(NormalOperationState(self))

        self.switches_app = kwargs['switches']

        self.switch_counter = SwitchCounter()

    def set_state(self, new_state):
        self._state = new_state
        self.print_verbose_log("Applied new state")

    def get_active_switch_ratio(self):
        return self.switch_counter.get_active_switch_ratio()

    @set_ev_cls(EventSwitchEnter)
    def switch_enter_handler(self, event):
        self.print_verbose_log("Received event: EventSwitchEnter")
        self.print_verbose_log(str(event.switch))
        self.switch_counter.log_switch_enter(event.switch)

        self._state.switch_enter_handler()

        switches_list = get_all_switch(self.switches_app)  # requested list of switches, own copy
        # print(switches_list)

    @set_ev_cls(EventSwitchLeave)
    def switch_leave_handler(self, event):
        self.print_verbose_log("Received event: EventSwitchLeave")
        self.print_verbose_log(str(event.switch))
        self.switch_counter.log_switch_leave(event.switch)

        self._state.switch_leave_handler()

    #
    #

    def send_state_event(self, event):
        self.send_event_to_observers(event)
        self.print_verbose_log("Raised event: " + str(event))

    @set_ev_cls(EventDisasterInSitu)
    def disaster_in_situ_handler(self, ev):
        self.print_verbose_log("Received event disaster started")


