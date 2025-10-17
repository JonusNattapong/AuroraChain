import hashlib
import json
from time import time

class Block:
    def __init__(self, index, transactions, previous_hash):
        self.index = index
        self.timestamp = time()
        self.transactions = transactions
        self.previous_hash = previous_hash
        self.nonce = 0
        self.hash = self.calculate_hash()

    def calculate_hash(self):
        # Serialize transactions to dict
        tx_data = [tx.to_dict() for tx in self.transactions]
        data = str(self.index) + str(self.timestamp) + json.dumps(tx_data, sort_keys=True) + self.previous_hash + str(self.nonce)
        return hashlib.sha256(data.encode()).hexdigest()

    def mine_block(self, difficulty):
        while self.hash[:difficulty] != '0' * difficulty:
            self.nonce += 1
            self.hash = self.calculate_hash()

    def __str__(self):
        return f"Block {self.index}: {self.hash}"