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

from event import EventQueue
from simInit import InitializeSimulation


if __name__=="__main__":
    simulator = InitializeSimulation('config.txt')
    while(simulator.params.termination_time>simulator.global_time):
        event = simulator.q.pop()
        simulator.global_time = event.eventTime
        if event.type=="Txn":
            #print("Inside Txn event")
            new_events = simulator.nodes[event.at].receiveTransaction(event.message,simulator.global_time)
            if event.at == event.fromID:
                new_events.append(simulator.nodes[event.at].generateTransaction(simulator.params.N, simulator.global_time))
        else:
            #print("Inside block event")
            if event.at==event.fromID:
                new_events = simulator.nodes[event.at].generateBlock(event,simulator.global_time)
            else:
                new_events = simulator.nodes[event.at].receiveBlock(event.message,simulator.global_time)
        for each_event in new_events:
            simulator.q.push(each_event)
    print("Node","Non_ver_Tnx","Total_Tnx","Total_block_in_tree","Blockchain_len","Total_block_seen",sep="\t")
    count=0
    for node in simulator.nodes:
        print(count,len(node.non_verfied_transaction), len(node.all_transaction), len(node.block_tree), node.longest_chain[1], len(node.all_block_ids.keys()),sep='\t\t')
        #print(node.genesis_block.id)
        node.visualize()
        node.saveTime()
        count+=1