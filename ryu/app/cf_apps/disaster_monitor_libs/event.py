from ryu.controller import event


class EventDisasterInSitu(event.EventBase):

    def __init__(self):
        super(EventDisasterInSitu, self).__init__()


# TODO: Event Disaster ended? No disaster?
# class DisasterEndedEvent(event.EventBase):
#     _asd = True
