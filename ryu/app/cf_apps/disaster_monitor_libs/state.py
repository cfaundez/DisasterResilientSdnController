from abc import ABCMeta, abstractmethod

from ryu.app.cf_apps.disaster_monitor_libs.event import EventDisasterInSitu
from ryu.app.cf_apps.libs.logging import Loggable

# TODO should be user set, maybe read from config file?

# Configuration
ENTER_THRESHOLD = 0.7
EXIT_THRESHOLD = 0.8

# Testing
DISASTER_EX_SITU_EXIST = False # For testing
FORCE_DISASTER_ON_START = False # For testing


# Abstract class
class State(Loggable, object):  # CHANGED BASE CLASS
    __metaclass__ = ABCMeta  # ADDED

    def __init__(self, dis_monitor_app):
        self.dis_monitor_app = dis_monitor_app
        self.print_verbose_log("created")

    @abstractmethod
    def switch_enter_handler(self):
        pass

    @abstractmethod
    def switch_leave_handler(self):
        pass


class DisasterInSituState(State):

    def __init__(self, dis_monitor_app):
        super(DisasterInSituState, self).__init__(dis_monitor_app)
        #self.dis_monitor_app.send_disaster_in_situ_event()
        self.dis_monitor_app.send_state_event(EventDisasterInSitu())


    def switch_enter_handler(self):
        if self._should_exit_state() and not FORCE_DISASTER_ON_START:
            if DISASTER_EX_SITU_EXIST:  # TODO review this condition, should be function
                self.dis_monitor_app.set_state(DisasterExSituState(self.dis_monitor_app))
            else:
                self.dis_monitor_app.set_state(NormalOperationState(self.dis_monitor_app))

    def switch_leave_handler(self):  # Done
        pass  # More switches disconnecting do not change status

    ###

    def _should_exit_state(self):
        # analyze active switch ratio
        active_switch_ratio = self.dis_monitor_app.get_active_switch_ratio()
        return active_switch_ratio >= EXIT_THRESHOLD

    @staticmethod
    def should_activate_state(active_switch_ratio):
        return active_switch_ratio < ENTER_THRESHOLD



class DisasterExSituState(State):

    def switch_enter_handler(self):  # Done
        pass  # New switches connecting do not change state

    def switch_leave_handler(self):  # Done
        if DisasterInSituState.should_activate_state(self.dis_monitor_app.get_active_switch_ratio()):
            self.dis_monitor_app.set_state(DisasterInSituState(self.dis_monitor_app))

    ###


class NormalOperationState(State):

    def switch_enter_handler(self):  # Done

        if not FORCE_DISASTER_ON_START: # Testing
            pass # New switches connecting do not change state
        else:
            self.dis_monitor_app.set_state(DisasterInSituState(self.dis_monitor_app))

    def switch_leave_handler(self):  # Done
        if DisasterInSituState.should_activate_state(self.dis_monitor_app.get_active_switch_ratio()):
            # trigger disaster in situ state
            self.dis_monitor_app.set_state(DisasterInSituState(self.dis_monitor_app))

