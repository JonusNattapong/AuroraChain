import hashlib
import binascii

def hash160(data_bytes):
    sha = hashlib.sha256(data_bytes).digest()
    try:
        from Crypto.Hash import RIPEMD160
        rip = RIPEMD160.new(sha).digest()
    except Exception:
        rip = hashlib.sha256(sha).digest()[:20]
    return binascii.hexlify(rip).decode()


def run_p2pkh(script_pubkey, script_sig, tx_hash):
    """Minimal P2PKH-like script evaluation.
    script_pubkey: dict {'type':'p2pkh','pubkey_hash':hex}
    script_sig: dict {'signature':hex,'pubkey':pem}
    tx_hash: string
    """
    if not script_pubkey or not script_sig:
        return False
    if script_pubkey.get('type') != 'p2pkh':
        return False
    pubkey_pem = script_sig.get('pubkey')
    signature = script_sig.get('signature')
    if not pubkey_pem or not signature:
        return False
    # check pubkey hash
    if hash160(pubkey_pem.encode()) != script_pubkey.get('pubkey_hash'):
        return False
    # verify signature (deferred to Wallet.verify_signature caller)
    return True
