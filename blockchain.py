from block import Block
from transaction import Transaction
import json
import hashlib

class Blockchain:
    def __init__(self, genesis_pubkey=None):
        self.chain = []
        self.pending_transactions = []
        self.spent_outputs = set()  # (tx_hash, output_index)
        self.difficulty = 2
        self.create_genesis_block(genesis_pubkey)

    def create_genesis_block(self, genesis_pubkey):
        # Genesis with coinbase
        if genesis_pubkey:
            genesis_tx = Transaction([], [{'amount': 100, 'script_pubkey': genesis_pubkey}])
        else:
            genesis_tx = Transaction([], [{'amount': 100, 'script_pubkey': 'genesis'}])
        genesis_block = Block(0, [genesis_tx], "0")
        genesis_block.mine_block(self.difficulty)
        self.chain.append(genesis_block)

    def get_last_block(self):
        return self.chain[-1]

    def add_transaction(self, transaction):
        # Prevent adding coinbase transactions (no inputs) via API
        if not transaction.inputs:
            raise ValueError("Cannot add coinbase transaction")
        if not transaction.is_valid(self):
            raise ValueError("Invalid transaction")
        # Prevent double-spend against already pending transactions
        for inp in transaction.inputs:
            for pending in self.pending_transactions:
                for pin in pending.inputs:
                    if pin['tx_hash'] == inp['tx_hash'] and pin['output_index'] == inp['output_index']:
                        raise ValueError("Input already used in pending transaction")
        # Check inputs not spent
        for inp in transaction.inputs:
            if (inp['tx_hash'], inp['output_index']) in self.spent_outputs:
                raise ValueError("Input already spent")
        # Check inputs exist
        for inp in transaction.inputs:
            found = False
            for block in self.chain:
                for tx in block.transactions:
                    if tx.hash == inp['tx_hash'] and len(tx.outputs) > inp['output_index']:
                        found = True
                        break
            if not found:
                raise ValueError("Input transaction not found")
        self.pending_transactions.append(transaction)

    def mine_pending_transactions(self, miner_pubkey):
        if not self.pending_transactions:
            return
        # Calculate fees: for each tx, inputs total - outputs total
        total_fees = 0
        for tx in self.pending_transactions:
            inputs_total = 0
            for inp in tx.inputs:
                out = self.get_output(inp['tx_hash'], inp['output_index'])
                if out:
                    inputs_total += out.get('amount', 0)
            outputs_total = sum(o.get('amount', 0) for o in tx.outputs)
            fee = inputs_total - outputs_total
            if fee < 0:
                raise ValueError("Transaction outputs exceed inputs")
            total_fees += fee
        # Add coinbase reward + fees
        block_reward = 1
        coinbase = Transaction([], [{'amount': block_reward + total_fees, 'script_pubkey': {'type': 'p2pkh', 'pubkey_hash': hashlib.sha256(miner_pubkey.encode()).hexdigest()}}])
        block = Block(len(self.chain), [coinbase] + self.pending_transactions, self.get_last_block().hash)
        block.mine_block(self.difficulty)
        self.chain.append(block)
        # Update spent
        for tx in self.pending_transactions + [coinbase]:
            for inp in tx.inputs:
                self.spent_outputs.add((inp['tx_hash'], inp['output_index']))
        self.pending_transactions = []
        self.save_chain()

    def get_balance(self, pubkey):
        utxos = self.get_utxos_for_pubkey(pubkey)
        return sum(u['amount'] for u in utxos)

    def get_utxos_for_pubkey(self, pubkey):
        utxos = []
        for block in self.chain:
            for tx in block.transactions:
                for i, out in enumerate(tx.outputs):
                    script = out.get('script_pubkey')
                    if isinstance(script, dict) and script.get('type') == 'p2pkh':
                        pub_hash = script.get('pubkey_hash')
                        if pub_hash == hashlib.sha256(pubkey.encode()).hexdigest():
                            utxo_key = (tx.hash, i)
                            if utxo_key not in self.spent_outputs:
                                utxos.append({'tx_hash': tx.hash, 'output_index': i, 'amount': out['amount']})
                    elif isinstance(script, str) and script == pubkey:
                        utxo_key = (tx.hash, i)
                        if utxo_key not in self.spent_outputs:
                            utxos.append({'tx_hash': tx.hash, 'output_index': i, 'amount': out['amount']})
        return utxos

    def get_output(self, tx_hash, index):
        for block in self.chain:
            for tx in block.transactions:
                if tx.hash == tx_hash:
                    if 0 <= index < len(tx.outputs):
                        return tx.outputs[index]
        return None

    def is_chain_valid(self):
        for i in range(1, len(self.chain)):
            current = self.chain[i]
            previous = self.chain[i-1]
            if current.hash != current.calculate_hash():
                return False
            if current.previous_hash != previous.hash:
                return False
        return True

    def save_chain(self, filename='blockchain.json'):
        chain_data = []
        for block in self.chain:
            block_data = {
                'index': block.index,
                'timestamp': block.timestamp,
                'transactions': [tx.to_dict() for tx in block.transactions],
                'previous_hash': block.previous_hash,
                'nonce': block.nonce,
                'hash': block.hash
            }
            chain_data.append(block_data)
        with open(filename, 'w') as f:
            json.dump(chain_data, f, indent=4)

    def __str__(self):
        return f"Blockchain with {len(self.chain)} blocks"