'''
while(some termination condition):
    event = q.pop()
    if event.type=="Tnx":
        nodes[event.at].receiveTransaction(event.message,global_time)
        if event.at==event.fromID:
            nodes[event.at].generateTransaction(global_time)
    else:
        if event.at==event.fromID:
            nodes[event.at].generateBlock(event,global_time)
        else:
            nodes[event.at].receiveBlock(event.message,global_time)
'''