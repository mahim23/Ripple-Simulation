from django.http import JsonResponse
from .enums import Phases
from dotenv import load_dotenv, find_dotenv
import os
from time import sleep, asctime
from .serializers import serialize_block, serialize_transaction
from .blockchain import Blockchain
import threading
import json
import ast


load_dotenv(find_dotenv(), override=True)
PHASE_TIME = int(os.getenv("PHASE_TIME"))
NUM_BLOCKS = int(os.getenv("NUM_BLOCKS"))

phase = Phases.IDLE

def update_phase():
    global phase
    global blockchain
    cur_time = asctime().split(" ")[3]
    cur_secs = int(cur_time.split(":")[2])
    sleep(10 - (cur_secs % 10))
    blocks = 0
    while True:
        if blocks >= NUM_BLOCKS:
            blockchain.save_num_transactions()
            break
        print("Phase: {}".format(phase.name))
        cur_time = asctime().split(" ")[3]
        cur_secs = int(cur_time.split(":")[2])
        next_zero = 10 - (cur_secs % 10)
        sleep(next_zero)
        phase = phase.next()
        if phase == Phases.FINALIZE:
            blockchain.finalize_block()
            blockchain.reset_consensus()

thread = threading.Thread(target=update_phase)
thread.start()

blockchain = Blockchain()


def get_current_phase(request):
    return JsonResponse({"phase": phase.value}, status=200)

def add_node(request):
    node = request.POST['node_id']
    print("Node ID: {}".format(node))
    if not blockchain.add_node(node):
        return JsonResponse({"message": "Node already present"}, status=400)
    return JsonResponse({"message": "Node added"}, status=200)

def get_blockchain(request):
    chain = []
    for block in blockchain.chain:
        chain.append(serialize_block(block))
    return JsonResponse({"blockchain": chain}, status=200)

def get_latest_block(request):
    latest_block = serialize_block(blockchain.chain[-1])
    return JsonResponse({"latest_block": latest_block}, status=200)

def merge_transactions(request, node):
    if phase != Phases.MERGE:
        return JsonResponse({"message": "This method is only allowed in MERGE phase"}, status=400)
    transactions = json.loads(request.body)["transactions"]
    if not blockchain.merge_transactions(node, transactions):
        return JsonResponse({"message": "Transactions not recorded - Node not in UNL or already sent transactions"},
            status=400)
    return JsonResponse({"message": "Merged"}, status=200)

def get_transactions(request, node):
    if phase != Phases.VOTING:
        return JsonResponse({"message": "This method is only allowed in VOTING phase"}, status=400)
    candidate_transactions = blockchain.get_candidate_transactions(node)
    transactions = []
    for transaction, _ in candidate_transactions.values():
        transactions.append(serialize_transaction(transaction))
    return JsonResponse({"transactions": transactions}, status=200)

def add_vote(request, node):
    if phase != Phases.VOTING:
        return JsonResponse({"message": "This method is only allowed in VOTING phase"}, status=400)
    votes = json.loads(request.body)["votes"]
    if not blockchain.add_node_vote(node, votes):
        return JsonResponse({"message": "Vote not recorded - Node not in UNL or already voted"}, status=400)
    return JsonResponse({"message": "Vote recorded"}, status=200)
