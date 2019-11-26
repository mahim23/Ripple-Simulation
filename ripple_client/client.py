import csv
from dotenv import load_dotenv, find_dotenv
import os
import sys
from Crypto.PublicKey import RSA
from Crypto.Signature import PKCS1_v1_5
from Crypto.Hash import SHA
import ast
import requests
import json
from time import sleep, asctime
import random
from base64 import b64encode, b64decode


load_dotenv(find_dotenv(), override=True)
NUM_USERS = int(os.getenv("NUM_USERS"))
PHASE_TIME = int(os.getenv("PHASE_TIME"))
BASE_URL = os.getenv("BASE_URL")
NUM_BLOCKS = int(os.getenv("NUM_BLOCKS"))


class Block:
    def __init__(self, index=None, timestamp=None, transactions=[], hash=None, prev_hash=None):
        self.index = index
        self.timestamp = timestamp
        self.transactions = transactions
        self.hash = hash
        self.prev_hash = prev_hash


class User:
	def __init__(self, id=None, balance=1000, public_key=None):
		self.id = id
		self.nonce = 1
		self.balance = balance
		self.public_key = public_key


class Client:
    def __init__(self, id=None, malicious=False):
        self.id = id
        self.malicious = malicious
        self.blockchain = []
        self.transactions = [[] for _ in range(222)]
        self.users = []
        self.load_users()
        self.load_transactions()

    def load_users(self):
        self.users = [User(id=i) for i in range(NUM_USERS)]
        with open("../transaction_generator/data/keys-s.csv", newline="") as file:
            reader = csv.reader(file)
            reader.__next__()
            for row in reader:
                if not row:
                    continue
                # print(row)
                key = RSA.importKey(b64decode(row[1].encode()))
                self.users[int(row[0])].public_key = PKCS1_v1_5.new(key)
    
    def load_transactions(self):
        with open('../transaction_generator/data/client-s-{}.csv'.format(self.id), newline='') as csvfile:
            csvreader = csv.reader(csvfile)
            csvreader.__next__()
            for row in csvreader:
                if not row:
                    continue
                if int(row[-1]) + 1 >= len(self.transactions):
                    self.transactions.append([])
                # print(self.transactions)
                self.transactions[int(row[-1]) + 1].append({
                    "nonce": int(row[0]),
                    "timestamp": row[1],
                    "from_addr": int(row[2]),
                    "to_addr": int(row[3]),
                    "value": int(row[4]),
                    "signature": row[5]
                })

    def add_node(self):
        url = BASE_URL + "api/add_node/"
        data = {"node_id": self.id}
        ret = requests.post(url=url, data=data)
        print(ret.text)

    def is_transaction_valid(self, transaction, nonce, balance):
        # Check for nonce
        from_addr = transaction["from_addr"]
        if transaction["nonce"] != nonce[from_addr]:
            print("Nonce wrong: {} - {}".format(transaction["nonce"], nonce[from_addr]))
            return False
        
        # Check for balance
        if transaction["value"] > balance[from_addr]:
            print("Balance wrong: {} - {}".format(transaction["value"], balance[from_addr]))
            return False
        
        # Check for signature
        s = str(transaction["nonce"]) + str(transaction["from_addr"]) + \
            str(transaction["to_addr"]) + str(transaction["value"])
        hash = SHA.new()
        hash.update(s.encode())
        signature = b64decode(transaction["signature"].encode())
        if not self.users[from_addr].public_key.verify(hash, signature):
            print("Signature rejected")
            return False
        
        return True

    def merge_transactions(self):
        # global transactions
        if len(self.blockchain) == 0:
            self.get_blockchain()
        transactions = self.transactions[self.blockchain[-1].index + 1]
        url = "{}api/merge_transactions/{}/".format(BASE_URL, self.id)
        data = json.dumps({"transactions": transactions})
        # print(data)
        # exit(0)
        ret = requests.post(url=url, data=data)
        print(ret.text)
        # if ret.status_code != 200:
        #     print(ret.text)

    def get_transactions(self):
        # global transactions
        url = "{}api/get_transactions/{}/".format(BASE_URL, self.id)
        ret = requests.get(url=url)
        # print(ret.text)
        transactions = json.loads(ret.text)["transactions"]
        # for transaction in transactions:
        #     transaction["signature"] = codecs.escape_decode(transaction["signature"])[0][2:-1]
        return transactions

    def vote(self, transactions):
        votes = []
        transactions.sort(key=lambda transaction: (int(transaction["nonce"]), int(transaction["value"])))
        nonce = [user.nonce for user in self.users]
        balance = [user.balance for user in self.users]
        for transaction in transactions:
            # print(transaction)
            r = 0
            if self.malicious:
                r = random.random()
            if self.is_transaction_valid(transaction, nonce, balance):
                if r > 0.5:
                    continue

                votes.append(transaction["signature"])
                nonce[transaction["from_addr"]] += 1
                balance[transaction["from_addr"]] -= transaction["value"]
                balance[transaction["to_addr"]] += transaction["value"]
            elif r > 0.5:
                votes.append(transaction["signature"])

        url = "{}api/add_vote/{}/".format(BASE_URL, self.id)
        data = json.dumps({"votes": votes})
        ret = requests.post(url=url, data=data)
        print(ret.text)
        # if ret.status_code != 200:
        #     print(ret.text)

    def get_blockchain(self):
        url = BASE_URL + "api/get_blockchain/"
        ret = requests.get(url=url)
        print(ret.text)
        chain = json.loads(ret.text)["blockchain"]
        self.blockchain = []
        for block in chain:
            # for transaction in block["transactions"]:
            #     transaction["signature"] = codecs.escape_decode(transaction["signature"])[0][2:-1]
            block = Block(
                index=block["index"],
                timestamp=block["timestamp"],
                transactions=block["transactions"],
                hash=block["hash"],
                prev_hash=block["prev_hash"]
            )
            self.blockchain.append(block)

    def get_latest_block(self):
        url = BASE_URL + "api/get_latest_block/"
        ret = requests.get(url=url)
        # print(ret.text)
        block = json.loads(ret.text)["latest_block"]
        if len(self.blockchain) > 0 and block["index"] == self.blockchain[-1].index + 1:
            # print(block)
            # for transaction in block["transactions"]:
            #     transaction["signature"] = codecs.escape_decode(transaction["signature"])[0][2:-1]
            block = Block(
                index=block["index"],
                timestamp=block["timestamp"],
                transactions=block["transactions"],
                hash=block["hash"],
                prev_hash=block["prev_hash"]
            )
            self.blockchain.append(block)
            for transaction in block.transactions:
                self.users[transaction["from_addr"]].nonce += 1
                self.users[transaction["from_addr"]].balance -= transaction["value"]
                self.users[transaction["to_addr"]].balance += transaction["value"]
        elif len(self.blockchain) > 0 and block["index"] == self.blockchain[-1].index:
            pass
        else:
            self.get_blockchain()


def main():
    if len(sys.argv) not in [2, 3]:
        print("Usage: {} <client_id> [<malicious>]".format(sys.argv[0]))
        exit(1)
    
    malicious = False
    if len(sys.argv) == 3 and sys.argv[2] == "malicious":
        malicious = True
    
    client_id = int(sys.argv[1])
    client = Client(client_id, malicious)

    url = BASE_URL + "api/get_current_phase/"
    ret = requests.get(url=url)
    phase = int(json.loads(ret.text)["phase"])
    print("Phase:", phase)

    started = False
    if phase == 0 or phase == 3:
        started = True

    cur_time = asctime().split(" ")[3]
    cur_secs = int(cur_time.split(":")[2])
    next_zero = 10 - (cur_secs % 10) + 1
    sleep(((3 - phase) * 10) + next_zero)

    client.add_node()
    client.get_blockchain()

    phase = 0
    blocks = 0

    while True:
        if blocks > NUM_BLOCKS:
            break
        print("Phase:", phase)
        if phase == 0:
            client.get_latest_block()
            started = True
            blocks += 1
        elif phase == 1 and started:
            client.merge_transactions()
        elif phase == 2 and started:
            transactions = client.get_transactions()
            client.vote(transactions)
        elif phase == 3 and not started:
            started = True
        phase = (phase + 1) % 4
        cur_time = asctime().split(" ")[3]
        cur_secs = int(cur_time.split(":")[2])
        next_zero = 10 - (cur_secs % 10) + 1
        sleep(next_zero)

if __name__ == "__main__":
    main()

