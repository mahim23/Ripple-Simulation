import os
from Crypto.PublicKey import RSA
from Crypto import Random
from Crypto.Cipher import PKCS1_OAEP
import random
import time
import csv
import math

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

	def generate_users(self):

		rows = []
		fields = ["user-id", "public_key", "private_key"]
		for i in range(self.num_users):
			key = RSA.generate(2048)
			private_key = key.export_key('PEM')
			public_key = key.publickey().exportKey('PEM')		
			self.users.append(User(i,self.init_balance,public_key,private_key))
			rows.append([i, public_key, private_key])

		with open("keys.csv",'w') as csvfile: 
			csvwriter = csv.writer(csvfile)
			csvwriter.writerow(fields) 
			csvwriter.writerows(rows)


	def generate_transactions(self, block_size = 10):
		trans_list = [[] for _ in range(self.num_clients)]
		for block in range(self.num_blocks):
			for trans in range(block_size):
				send = random.randint(0, self.num_users-1)
				timestamp = time.asctime()
				to = random.randint(0, len(self.users)-1)
				while to == send:
					to = random.randint(0, len(self.users)-1)
				value = random.randint(0, math.ceil(1.05*self.users[send].balance))
				invalid_flag=False
				if ( self.users[send].balance - value > 0 ):
					self.users[send].balance -= value
					self.users[send].nonce += 1
				else:
					invalid_flag = True

				rand_num_clients = random.randint(0, 7)
				clients = random.sample(range(0, 8), rand_num_clients)
				for cl in clients:
					enc = ""
					if(not invalid_flag):
						r = random.randint(0,100)
						if r > 97 :
							enc += ":P"
					enc += str(self.users[send].nonce) + str(timestamp) + str(send) + str(to) + str(value) 
					rsa_public_key = RSA.importKey(self.users[send].public_key)
					rsa_public_key = PKCS1_OAEP.new(rsa_public_key)
					sign = rsa_public_key.encrypt(bytes(enc, 'utf-8'))
					trans_list[cl].append([self.users[send].nonce, timestamp, send, to, value, sign, block])

		filename_base = "client-"
		fields = ["nonce", "timestamp", "from", "to", "value", "signature", "block_index"]
		for c in range(self.num_clients):
			with open(filename_base+str(c)+".csv",'w') as csvfile: 
				csvwriter = csv.writer(csvfile)
				csvwriter.writerow(fields) 
				csvwriter.writerows(trans_list[c])

g = Generator(num_users = 10, num_clients = 8, num_blocks = 100+130 )
g.generate_users()
g.generate_transactions(block_size = 10)
