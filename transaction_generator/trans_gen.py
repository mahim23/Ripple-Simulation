import os
from Crypto.PublicKey import RSA
from Crypto import Random
from Crypto.Signature import PKCS1_v1_5
from Crypto.Hash import SHA
import random
import time
import csv
import math
from base64 import b64encode, b64decode

class User:

	def __init__(self, id = None, balance = 1000, public_key = None, private_key = None):
		self.id = id
		self.nonce = 0
		self.balance = balance
		self.public_key = public_key
		self.private_key = private_key

class Generator:

	def __init__(self, num_users = 10, num_clients = 8, num_blocks = 10, init_balance = 1000):
		self.num_users=num_users
		self.num_clients = num_clients
		self.num_blocks  = num_blocks
		self.init_balance = init_balance
		self.users = []
		self.invalid_count = 0

	def generate_users(self):

		rows = []
		fields = ["user-id", "public_key", "private_key"]
		for i in range(self.num_users):
			key = RSA.generate(2048)
			private_key = b64encode(key.export_key('PEM')).decode()
			public_key = b64encode(key.publickey().exportKey('PEM')).decode()
			self.users.append(User(i,self.init_balance,public_key,private_key))
			rows.append([i, public_key, private_key])

		with open("data/keys.csv",'w') as csvfile: 
			csvwriter = csv.writer(csvfile)
			csvwriter.writerow(fields) 
			csvwriter.writerows(rows)


	def generate_transactions(self, block_size = 10):
		trans_list = [[] for _ in range(self.num_clients)]
		for block in range(self.num_blocks):
			for _ in range(block_size):
				send = random.randint(0, self.num_users-1)
				timestamp = time.asctime()
				to = random.randint(0, len(self.users)-1)
				while to == send:
					to = random.randint(0, len(self.users)-1)
				# value = random.randint(0, math.ceil(1.05*self.users[send].balance))
				ran = random.random()
				if ran > 0.95:
					value = math.ceil(1.1 * self.users[send].balance)
					invalid_flag = True
					print("Balance: ", self.users[send].nonce, send, to, value)
					self.invalid_count += 1
				else:
					if self.users[send].balance > 50:
						value = random.randint(1, math.ceil(0.2 * self.users[send].balance))
					else:
						value = 2
					self.users[send].balance -= value
					self.users[to].balance += value
					self.users[send].nonce += 1
					invalid_flag=False

				rand_num_clients = random.randint(1, self.num_clients)
				clients = random.sample(range(0, self.num_clients), rand_num_clients)
				enc = ""
				if not invalid_flag:
					r = random.randint(1,100)
					if r > 97 :
						enc += ":P"
						self.users[send].nonce -= 1
						self.users[send].balance += value
						self.users[to].balance -= value
						print("Signature: ", self.users[send].nonce, send, to, value)
						self.invalid_count += 1
				enc += str(self.users[send].nonce) + str(send) + str(to) + str(value) 
				rsa_private_key = RSA.importKey(b64decode(self.users[send].private_key.encode()))
				rsa_private_key = PKCS1_v1_5.new(rsa_private_key)
				hash = SHA.new()
				hash.update(enc.encode())
				sign = b64encode(rsa_private_key.sign(hash)).decode()
				for cl in clients:
					trans_list[cl].append([self.users[send].nonce, timestamp, send, to, value, sign, block])

		filename_base = "data/client-"
		fields = ["nonce", "timestamp", "from", "to", "value", "signature", "block_index"]
		for c in range(self.num_clients):
			with open(filename_base+str(c)+".csv",'w') as csvfile: 
				csvwriter = csv.writer(csvfile)
				csvwriter.writerow(fields) 
				csvwriter.writerows(trans_list[c])

g = Generator(num_users = 10, num_clients = 10, num_blocks = 220)
g.generate_users()
g.generate_transactions(block_size = 10)
print("Count:", g.invalid_count)
