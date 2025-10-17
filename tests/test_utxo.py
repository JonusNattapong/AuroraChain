import pytest
from wallet import Wallet
from blockchain import Blockchain
from transaction import Transaction


def test_happy_path(tmp_path):
    alice = Wallet()
    bob = Wallet()
    miner = Wallet()
    bc = Blockchain(alice.get_public_key_pem())

    # Alice has genesis UTXO
    alice_utxos = bc.get_utxos_for_pubkey(alice.get_public_key_pem())
    assert len(alice_utxos) == 1

    # Alice sends 10 to Bob with fee 1
    tx = alice.create_transaction(bob.get_public_key_pem(), 10, alice_utxos, fee=1)
    bc.add_transaction(tx)
    bc.mine_pending_transactions(miner.get_public_key_pem())

    assert bc.get_balance(bob.get_public_key_pem()) == 10
    assert bc.get_balance(alice.get_public_key_pem()) == 89  # 100 - 10 - 1 fee
    assert bc.get_balance(miner.get_public_key_pem()) == 2  # 1 coinbase + 1 fee


def test_invalid_signature_rejected():
    alice = Wallet()
    bob = Wallet()
    miner = Wallet()
    bc = Blockchain(alice.get_public_key_pem())

    alice_utxos = bc.get_utxos_for_pubkey(alice.get_public_key_pem())
    tx = alice.create_transaction(bob.get_public_key_pem(), 10, alice_utxos, fee=0)
    # Tamper with signature
    tx.inputs[0]['script_sig']['signature'] = '00' * 64
    with pytest.raises(ValueError):
        bc.add_transaction(tx)


def test_double_spend_rejected():
    alice = Wallet()
    bob = Wallet()
    miner = Wallet()
    bc = Blockchain(alice.get_public_key_pem())

    alice_utxos = bc.get_utxos_for_pubkey(alice.get_public_key_pem())
    tx1 = alice.create_transaction(bob.get_public_key_pem(), 10, alice_utxos, fee=0)
    tx2 = alice.create_transaction(bob.get_public_key_pem(), 20, alice_utxos, fee=0)
    bc.add_transaction(tx1)
    # tx2 uses same UTXO -> should still be added to pending but mining will fail or spending check should reject
    with pytest.raises(ValueError):
        bc.add_transaction(tx2)