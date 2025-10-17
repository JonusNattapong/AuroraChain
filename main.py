from blockchain import Blockchain
from transaction import Transaction
from wallet import Wallet

def main():
    # Create wallets first
    alice_wallet = Wallet()
    bob_wallet = Wallet()
    miner_wallet = Wallet()

    print("Alice Public Key:", alice_wallet.get_public_key_pem()[:50] + "...")
    print("Bob Public Key:", bob_wallet.get_public_key_pem()[:50] + "...")
    print("Miner Public Key:", miner_wallet.get_public_key_pem()[:50] + "...")

    # Create a new blockchain with genesis to Alice
    blockchain = Blockchain(alice_wallet.get_public_key_pem())

    print("Genesis block created with 100 coins to Alice.")

    # Get Alice's UTXOs
    alice_utxos = blockchain.get_utxos_for_pubkey(alice_wallet.get_public_key_pem())
    print(f"Alice UTXOs: {alice_utxos}")

    # Create transaction from Alice to Bob
    tx1 = alice_wallet.create_transaction(bob_wallet.get_public_key_pem(), 10, alice_utxos)
    print("Transaction created.")

    # Add transaction
    try:
        blockchain.add_transaction(tx1)
        print("Transaction added successfully.")
    except ValueError as e:
        print(f"Error adding transaction: {e}")

    # Mine the pending transactions
    print("Mining block...")
    blockchain.mine_pending_transactions(miner_wallet.get_public_key_pem())

    # Print the blockchain
    print("\nBlockchain:")
    for block in blockchain.chain:
        print(f"  {block}")
        for tx in block.transactions:
            print(f"    {tx}")

    # Check validity
    print(f"\nIs blockchain valid? {blockchain.is_chain_valid()}")

    # Print balances
    print("\nBalances:")
    print(f"Alice: {blockchain.get_balance(alice_wallet.get_public_key_pem())}")
    print(f"Bob: {blockchain.get_balance(bob_wallet.get_public_key_pem())}")
    print(f"Miner: {blockchain.get_balance(miner_wallet.get_public_key_pem())}")

    # Save blockchain
    blockchain.save_chain()
    print("Blockchain saved to blockchain.json")

if __name__ == "__main__":
    main()