import hashlib
import json
from time import time

class Transaction:
    def __init__(self, inputs, outputs):
        self.inputs = inputs  # list of {'tx_hash': str, 'output_index': int, 'script_sig': str}
        self.outputs = outputs  # list of {'amount': float, 'script_pubkey': str}
        self.timestamp = time()
        self.hash = self.calculate_hash()

    def calculate_hash(self):
        data = json.dumps({
            'inputs': [{'tx_hash': i['tx_hash'], 'output_index': i['output_index']} for i in self.inputs],
            'outputs': self.outputs,
            'timestamp': self.timestamp
        }, sort_keys=True)
        return hashlib.sha256(data.encode()).hexdigest()

    def sign(self, wallet):
        for i, inp in enumerate(self.inputs):
            # Assume script_pubkey is pubkey, sign the tx hash
            data = self.hash
            sig = wallet.sign_transaction(data)
            # For P2PKH we store signature + pubkey PEM in script_sig
            self.inputs[i]['script_sig'] = {
                'signature': sig,
                'pubkey': wallet.get_public_key_pem()
            }

    def is_valid(self, blockchain=None):
        """
        Validate the transaction by checking each input's signature against the referenced output's
        script_pubkey (treated as the public key PEM). Requires a `blockchain` instance to resolve
        referenced outputs for UTXO verification.
        """
        # Coinbase / no-input transactions are valid by definition
        if not self.inputs:
            return True
        if blockchain is None:
            # Without blockchain context we can only check presence of signatures
            return all('script_sig' in inp for inp in self.inputs)

        # Verify each input signature against the referenced output's pubkey or script
        from wallet import Wallet
        from script_vm import run_p2pkh
        for inp in self.inputs:
            if 'script_sig' not in inp:
                return False
            out = blockchain.get_output(inp['tx_hash'], inp['output_index'])
            if out is None:
                return False
            script_pub = out.get('script_pubkey')
            script_sig = inp.get('script_sig')
            if not script_pub or not script_sig:
                return False
            # support p2pkh-like scripts
            if isinstance(script_pub, dict) and script_pub.get('type') == 'p2pkh':
                pubkey_pem = script_sig.get('pubkey')
                sig = script_sig.get('signature')
                if not pubkey_pem or not sig:
                    return False
                # run p2pkh structural checks
                if not run_p2pkh(script_pub, script_sig, self.hash):
                    return False
                if not Wallet.verify_signature(self.hash, sig, pubkey_pem):
                    return False
            else:
                # Fallback: if script_pubkey is raw pubkey PEM
                pubkey_pem = script_pub if isinstance(script_pub, str) else None
                sig = script_sig.get('signature') if isinstance(script_sig, dict) else script_sig
                if pubkey_pem is None or sig is None:
                    return False
                if not Wallet.verify_signature(self.hash, sig, pubkey_pem):
                    return False
        return True

    def to_dict(self):
        return {
            'hash': self.hash,
            'inputs': self.inputs,
            'outputs': self.outputs,
            'timestamp': self.timestamp
        }

    def __str__(self):
        return f"Transaction {self.hash[:16]}...: {len(self.inputs)} inputs, {len(self.outputs)} outputs"