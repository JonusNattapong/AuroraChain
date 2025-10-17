from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives import serialization, hashes
import hashlib
import binascii
from hashlib import sha256
try:
    from Crypto.Hash import RIPEMD160
except Exception:
    RIPEMD160 = None

class Wallet:
    def __init__(self):
        self.private_key = ec.generate_private_key(ec.SECP256R1())
        self.public_key = self.private_key.public_key()

    def get_public_key_pem(self):
        return self.public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        ).decode()

    def sign_transaction(self, transaction_data):
        signature = self.private_key.sign(
            transaction_data.encode(),
            ec.ECDSA(hashes.SHA256())
        )
        return signature.hex()

    def pubkey_hash(self):
        pem = self.get_public_key_pem().encode()
        h = sha256(pem).digest()
        if RIPEMD160:
            r = RIPEMD160.new(h).digest()
        else:
            # fallback to sha256 then truncated hex if ripemd not available
            r = sha256(h).digest()[:20]
        return binascii.hexlify(r).decode()

    @staticmethod
    def verify_signature(transaction_data, signature, public_key_pem):
        public_key = serialization.load_pem_public_key(public_key_pem.encode())
        try:
            public_key.verify(
                bytes.fromhex(signature),
                transaction_data.encode(),
                ec.ECDSA(hashes.SHA256())
            )
            return True
        except:
            return False

    def create_transaction(self, recipient_pubkey, amount, utxos, fee=0):
        # Select UTXOs to spend
        selected = []
        total = 0
        for utxo in utxos:
            if total >= amount + fee:
                break
            selected.append(utxo)
            total += utxo['amount']
        if total < amount + fee:
            raise ValueError("Insufficient UTXOs")
        # Create inputs
        inputs = [{'tx_hash': u['tx_hash'], 'output_index': u['output_index'], 'script_sig': {}} for u in selected]
        # Outputs: use P2PKH-like script_pubkey dict
        outputs = [{'amount': amount, 'script_pubkey': {'type': 'p2pkh', 'pubkey_hash': hashlib.sha256(recipient_pubkey.encode()).hexdigest()}}]
        change = total - amount - fee
        if change > 0:
            outputs.append({'amount': change, 'script_pubkey': {'type': 'p2pkh', 'pubkey_hash': hashlib.sha256(self.get_public_key_pem().encode()).hexdigest()}})
        from transaction import Transaction
        tx = Transaction(inputs, outputs)
        tx.sign(self)
        return tx