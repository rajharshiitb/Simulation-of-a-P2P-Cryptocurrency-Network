'''
    3----5
    |
    |
    6
    block chain status: longest chain: 10
    Node 1 has mined a block 11th and far away and on the way
    Meanwhile 5 mined a block 11th
    Dynamic Graph:
        --Links break and Link join
        --New link created
    For eg:
        3 is fast node
        5 is also fast node and 6 is slow node
        Node 1 and 4 has mined 11th and 12th block
        Senario: Node 3 received 12th block prior than 11th block
'''
'''
    1. Can we say that all the transactions that are on the shorter chain are already present in longer chain??(TRUE)
    2. If 1, is true then it make sense to add new mined block in longer chain
    3. If 1, is false then then suppose a Txn k is proved to be non-valid on longer chain then should we discrad or keep it
       in hope that at some point one shorter chain will become longer in which k can be proved valid??
             ID20 :0      Id10 pays Id 20 100 BTC (12) --> Id 20 pays Id 1 10 BTC(12)(In real world it won't reject)
            12+delay = balance at 12 +100
            12+delay = balamce at 12-10
             Event: Heap

           -e(In the condition that a miner has accquired more CPU more)
    a-b-c-d-g-h
'''