class Transaction():
    def __init__(self, TxnID):
        self.TxnID = TxnID
        tokens = TxnID.split()
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
        pass
    def __repr__(self):
        data = (self.TxnID, self.fromID, self.toID, self.coins)
        return "<Txn %s: From=%s, To=%s, amount=%s>" %data