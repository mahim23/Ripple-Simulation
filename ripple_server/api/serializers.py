def serialize_block(block):
    new_block = {
        "index": block.index,
        "timestamp": block.timestamp,
        "hash": block.hash,
        "prev_hash": block.prev_hash,
        "transactions": []
    }
    for transaction in block.transactions:
        new_block["transactions"].append(serialize_transaction(transaction))
    return new_block

def serialize_transaction(transaction):
    new_transaction = {
        "nonce": transaction.nonce,
        "timestamp": transaction.timestamp,
        "from_addr": transaction.from_addr,
        "to_addr": transaction.to_addr,
        "value": transaction.value,
        "signature": str(transaction.signature)
    }
    return new_transaction
