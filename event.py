class Event():
    def __init__(self,eventTime,type,fromID,toID,object):
        '''
            -Total three types of events
            -eventTime : Scheduled time of event
            -type: "Block" or "Tnx"
        '''
        self.eventTime = eventTime
        self.type = type
        self.fromID = fromID
        self.toID = toID
        self.message = object
        pass