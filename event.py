import heapq
class Event():
    def __init__(self,eventTime,type,fromID,toID,object,at):
        '''
            -Total three types of events:
                --Txn: A sends B 5 BTC
                --Block: sends block or receives block
                        
            -eventTime : Scheduled time of event
            -type: "Block" or "Txn"
            -use of at:
                Ea is being executed
                generate new event for node a when at==fromID
            -messgae: contains object of the Transaction
        '''
        self.eventTime = eventTime
        self.type = type
        self.at = at
        self.fromID = fromID
        self.toID = toID
        self.message = object
        pass
    def __lt__(self,other):
        return self.eventTime<other.eventTime
class EventQueue():
    def __init__(self):
        '''
            -minq maintains events in minheap order
        '''
        self.minq = []
    def push(self,event):
        heapq.heappush(self.minq,event)
        pass
    def pop(self):
        return heapq.heappop(self.minq)
    def len(self):
        return len(self.minq)
