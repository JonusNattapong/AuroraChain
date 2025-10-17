from flask import Flask, request, jsonify
from blockchain import Blockchain
from transaction import Transaction

app = Flask(__name__)
blockchain = Blockchain()

@app.route('/chain', methods=['GET'])
def get_chain():
    chain_data = []
    for block in blockchain.chain:
        chain_data.append({
            'index': block.index,
            'timestamp': block.timestamp,
            'transactions': [tx.to_dict() for tx in block.transactions],
            'previous_hash': block.previous_hash,
            'hash': block.hash
        })
    return jsonify({'chain': chain_data, 'length': len(chain_data)})

@app.route('/add_transaction', methods=['POST'])
def add_transaction():
    data = request.get_json()
    sender = data['sender_public_key']
    receiver = data['receiver_public_key']
    amount = data['amount']
    signature = data['signature']
    tx = Transaction(sender, receiver, amount)
    tx.signature = signature
    try:
        blockchain.add_transaction(tx)
        return jsonify({'message': 'Transaction added'}), 201
    except ValueError as e:
        return jsonify({'error': str(e)}), 400

@app.route('/mine', methods=['POST'])
def mine():
    data = request.get_json()
    miner_address = data['miner_address']
    blockchain.mine_pending_transactions(miner_address)
    return jsonify({'message': 'Block mined'})

@app.route('/balance/<public_key>', methods=['GET'])
def get_balance(public_key):
    balance = blockchain.get_balance(public_key)
    return jsonify({'balance': balance})

if __name__ == '__main__':
    app.run(debug=True)