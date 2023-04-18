from ryu.app.cf_apps.libs.logging import Loggable


class SwitchCounter(Loggable):

    def __init__(self):
        self.max_switches = 0
        self.active_switches = 0

    def log_current_switches(self, active_switch_list):
        active_switches_num = len(active_switch_list)
        # 1. Update max switch count
        self.max_switches = max(self.max_switches, active_switches_num)

    def log_switch_enter(self, switch):
        self.active_switches += 1
        self.max_switches = max(self.max_switches, self.active_switches)

        self.print_verbose_log("active switches = " + str(self.active_switches))

    def log_switch_leave(self, switch):
        self.active_switches -= 1

        self.print_verbose_log("active switches = " + str(self.active_switches))

    def get_active_switch_ratio(self):
        return float(self.active_switches) / self.max_switches

