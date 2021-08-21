import hashlib
class Transaction():
    def __init__(self, Txn, timestamp):
        '''
            -Tnx: IDx sends IDy 10 BTC
            -timestamp: maintains Tnx creation time
            -fromID: Node that created the Tnx
            -toID: Dest Node ID
            -coins: amount of transaction
            -TnxID: Hash of (Tnx||timestamp)
                makes it unique
        ''' 
        self.Txn = Txn
        self.timestamp = timestamp
        tokens = Txn.split()
        self.fromID = None
        self.toID = None
        self.coins = None
        if tokens[1]=="mines":
            #IDx mines 10 BTC
            self.fromID = "coinbase"
            self.toID = tokens[0]
            self.coins = tokens[2]
        else:
            #IDx pays IDy 10 BTC
            self.fromID = tokens[0]
            self.toID = tokens[2]
            self.coins = tokens[3]
        self.TxnID = self.setID(Txn,timestamp)
        pass
    def setID(self, Txn, timestamp):
        concat_tnx = Txn+" "+str(timestamp)
        result = hashlib.sha256(concat_tnx)
        return result.hexdigest
    def __repr__(self):
        data = (self.TxnID, self.fromID, self.toID, self.coins)
        return "<Txn %s: From=%s, To=%s, amount=%s>" %data