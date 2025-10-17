# Advanced Blockchain Project (Prototype)

This repository is an educational prototype of a Bitcoin-like blockchain written in Python. It implements key concepts needed for a realistic cryptocurrency while keeping the code compact and easy to follow.
## Key Features (implemented)

- UTXO model for transactions (inputs/outputs)
- Wallets with ECDSA key pairs (PEM format)
- P2PKH-like script support (minimal script VM for signature checks)
- Transaction signing and full signature verification against referenced UTXOs
- Transaction fees: pending transactions can include fees; miners collect fees in coinbase
- Proof-of-Work mining with adjustable difficulty
- Double-spend protection (checks pending and spent UTXOs)
- Persistence: chain saved to `blockchain.json`
- Flask REST API for interaction (basic endpoints)
- Unit tests (pytest) covering UTXO flows, invalid signatures, and double-spend
## Requirements

Install dependencies into your virtual environment:
```powershell
D:/GitHub/Blockchain-two/.venv/Scripts/python.exe -m pip install -r requirements.txt
```
## Quick start

Run the demo (creates wallets, sends transactions, mines blocks):
```powershell
D:/GitHub/Blockchain-two/.venv/Scripts/python.exe main.py
```
Start the API server:

```powershell
D:/GitHub/Blockchain-two/.venv/Scripts/python.exe api.py
# Server available at http://127.0.0.1:5000
```
Run the unit tests:

```powershell
D:/GitHub/Blockchain-two/.venv/Scripts/python.exe -m pytest -q
```
## Project layout

- `block.py` — Block structure, hashing, mining
- `transaction.py` — UTXO Transaction model, signing, and script verification
- `wallet.py` — Wallet key generation, signing, helper to build transactions
- `script_vm.py` — Minimal script helpers (hash160, P2PKH check)
- `blockchain.py` — Chain management, UTXO tracking, mining, fees
- `api.py` — Flask endpoints for chain, transactions, mining, balances
- `main.py` — Console demo
- `tests/` — Pytest tests

## API Endpoints
- `GET /chain` — returns the full chain
- `POST /add_transaction` — submit signed transaction JSON
- `POST /mine` — mine pending transactions (provide miner public key)
- `GET /pending` — list pending transactions
- `GET /balance/<public_key>` — retrieve balance for a public key (PEM)

Example transaction payload for `/add_transaction`:
```json
{
	"inputs": [{"tx_hash": "...", "output_index": 0, "script_sig": {"signature": "...", "pubkey": "-----BEGIN PUBLIC KEY-----..."}}],
	"outputs": [{"amount": 10, "script_pubkey": {"type":"p2pkh","pubkey_hash":"..."}}]
}
```
## Next improvements (roadmap)

1. Script VM expansion — full stack-based interpreter (OP_HASH160, OP_CHECKMULTISIG, OP_RETURN)
2. Dynamic difficulty adjustment (auto-tune to target block time)
3. P2P networking and longest-chain consensus (peer discovery, gossip)
4. Wallet encrypted keystore (AES + PBKDF2) and key management UI
5. Web UI (React) with live chain/tx/mining dashboard

If you want, I can start implementing any of the roadmap items. Recommended next steps: expand the Script VM, then add dynamic difficulty, then P2P networking.
## Notes

This project is a learning prototype and not suitable for production use. Security, persistence, and network behaviour are simplified for clarity.

---
_Updated: Oct 17, 2025_
# Advanced Blockchain Project

This is an advanced implementation of a blockchain in Python, featuring digital signatures, wallets, persistence, and a REST API.

## Features

- **Digital Signatures**: Transactions are signed using ECDSA for security.
- **Wallets**: Generate public/private key pairs for secure transactions.
- **Proof-of-Work**: Mining with adjustable difficulty.
- **Transaction Validation**: Ensures only valid signed transactions are added.
- **Persistence**: Save and load blockchain state to/from JSON.
- **REST API**: Interact with the blockchain via HTTP endpoints using Flask.
- **Chain Validation**: Verifies the integrity of the entire blockchain.

## Setup Instructions

1. Ensure you have Python 3.x installed.
2. Install dependencies: `pip install -r requirements.txt`
3. Run the demo: `python main.py`
4. For API: `python api.py` (runs on http://127.0.0.1:5000)

## Project Structure

- `blockchain.py`: Manages the blockchain, mining, and validation.
- `block.py`: Block class with hashing and mining.
- `transaction.py`: Transaction class with signature support.
- `wallet.py`: Wallet class for key management and signing.
- `api.py`: Flask REST API for blockchain interaction.
- `main.py`: Demo script showcasing advanced features.
- `requirements.txt`: Dependencies (cryptography, flask).
- `blockchain.json`: Saved blockchain state.

## API Endpoints

- `GET /chain`: Retrieve the full blockchain.
- `POST /add_transaction`: Add a signed transaction (JSON payload).
- `POST /mine`: Mine pending transactions (provide miner address).
- `GET /pending`: Get pending transactions.
- `GET /balance/<public_key>`: Get balance for a public key.

## Usage

Run `main.py` for a console demo with wallets and signed transactions.

Run `api.py` to start the web server and interact via API calls.

## Extending Further

- Add peer-to-peer networking
- Implement consensus algorithms (PoS, etc.)
- Add balance tracking and UTXO model
- Integrate with web frontend

## License

This project is for educational purposes.