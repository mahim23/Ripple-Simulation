from hashlib import sha256
from time import asctime


class Transaction:
    def __init__(self, nonce=None, timestamp=None, from_addr=None, to_addr=None,
        value=None, signature=None):
        self.nonce = nonce
        self.timestamp = timestamp
        self.from_addr = from_addr
        self.to_addr = to_addr
        self.value = value
        self.signature = signature

    def __str__(self):
        return "{{Nonce: {}, From: {}, To: {}, Value: {}}}".format(
            self.nonce,
            self.from_addr,
            self.to_addr,
            self.value
        )


class Block:
    def __init__(self, index=None, timestamp=None, transactions=[], prev_hash=None):
        self.index = index
        self.timestamp = timestamp
        self.transactions = transactions
        self.hash = None
        self.prev_hash = prev_hash
    
    def __str__(self):
        return "\nBlock:-\nIndex: {}\nTransactions:-\n{}\nHash: {}\nPrev Hash: {}".format(
            self.index,
            [str(t) for t in self.transactions],
            self.hash,
            self.prev_hash
        )
    
    def calculate_hash(self, s):
        return sha256(s.encode()).hexdigest()
    
    def calculate_block_hash(self):
        s = str(self.index) + self.timestamp
        for transaction in self.transactions:
            s += str(transaction.signature)
        if self.prev_hash:
            s += self.prev_hash
        return self.calculate_hash(s)
    
    @staticmethod
    def generate_block(old_block, transactions):
        block = Block(index=old_block.index+1, transactions=transactions, prev_hash=old_block.hash)
        block.timestamp = asctime()
        block.hash = block.calculate_block_hash()
        return block
    
    def is_block_valid(self, old_block):
        if (old_block.index + 1 != self.index):
            return False
        if old_block.hash != self.prev_hash:
            return False
        if self.hash != self.calculate_block_hash():
            return False
        return True


class Blockchain:
    def __init__(self):
        self.chain = []
        self.unl = {}
        self.candidate_transactions = {}
        self.num_transactions = 0
        open("data/results.txt", 'w').close()
        self.create_genesis_block()
    
    def create_genesis_block(self):
        block = Block(index=0, timestamp=asctime(), transactions=[], prev_hash=None)
        block.hash = block.calculate_block_hash()
        self.chain.append(block)
        with open("data/results.txt", "a") as file:
            file.write(str(block) + "\n\n")
    
    def add_node(self, node):
        if node in self.unl:
            return False
        self.unl[node] = [0, 0]
        return True
    
    def merge_transactions(self, node, transactions):
        if node not in self.unl or self.unl[node][0] == 1:
            return False
        # print("In blockchain.merge_transactions")
        # print(transactions)
        for transaction in transactions:
            if transaction['signature'] not in self.candidate_transactions:
                transaction = Transaction(
                    transaction['nonce'],
                    transaction['timestamp'],
                    transaction['from_addr'],
                    transaction['to_addr'],
                    transaction['value'],
                    transaction['signature']
                )
                self.candidate_transactions[transaction.signature] = [transaction, 0]
        self.unl[node][0] = 1
        return True
    
    def get_candidate_transactions(self, node):
        if node not in self.unl:
            return None
        return self.candidate_transactions
    
    def add_node_vote(self, node, votes):
        if node not in self.unl or self.unl[node][1] == 1:
            return False
        for vote in votes:
            if vote in self.candidate_transactions:
                self.candidate_transactions[vote][1] += 1
        self.unl[node][1] = 1
        return True
    
    def finalize_block(self):
        for node in self.unl.values():
            if node == 0:
                return False
        transactions = []
        voted = [1 for node in self.unl.values() if node[1] == 1]
        if not voted:
            return
        threshold = 0.8 * len(voted)
        transaction_str = "\n"
        for transaction, votes in self.candidate_transactions.values():
            transaction_str += "\n{}\nVotes: {}".format(transaction, votes)
            if votes >= threshold:
                transactions.append(transaction)
        print(transaction_str)
        if not transactions:
            return
        self.num_transactions += len(transactions)
        block = Block.generate_block(self.chain[-1], transactions)
        self.chain.append(block)

        transaction_str += "\n\n"
        block_str = str(block)
        with open("data/results.txt", "a") as file:
            file.write(block_str)
            file.write(transaction_str)

        print(block)
        print()
        return block
    
    def reset_consensus(self):
        self.candidate_transactions = {}
        for node in self.unl.keys():
            self.unl[node] = [0, 0]
    
    def save_num_transactions(self):
        with open("data/results.txt", "a") as file:
            file.write("\nNumber of transactions: {}\n".format(self.num_transactions))
