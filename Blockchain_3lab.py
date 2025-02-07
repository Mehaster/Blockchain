import time
import json
from Crypto.PublicKey import RSA
from Crypto.Signature import pkcs1_15
from Crypto.Hash import SHA256
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QTextEdit, QPushButton

# ----------------- 1. ХЭШ АЛГОРИТМІ -----------------

def simple_hash(data: str) -> str:
    """Қарапайым хэш алгоритмі (hashlib қолданбай)"""
    hash_value = 0x12345678
    for char in data:
        byte = ord(char)
        hash_value ^= byte
        hash_value = (hash_value << 5) | (hash_value >> 27)
        hash_value &= 0xFFFFFFFF
    return hex(hash_value)[2:]

# ----------------- 2. БЛОК ҚҰРЫЛЫМЫ -----------------

class Block:
    def __init__(self, transactions, previous_hash="0"):
        self.timestamp = time.time()
        self.transactions = transactions
        self.previous_hash = previous_hash
        self.merkle_root = self.calculate_merkle_root()
        self.hash = self.calculate_hash()

    def calculate_merkle_root(self):
        """Меркле түбірін есептеу"""
        hashes = [simple_hash(json.dumps(tx)) for tx in self.transactions]
        while len(hashes) > 1:
            temp = []
            for i in range(0, len(hashes), 2):
                if i + 1 < len(hashes):
                    temp.append(simple_hash(hashes[i] + hashes[i + 1]))
                else:
                    temp.append(hashes[i])
            hashes = temp
        return hashes[0] if hashes else "0"

    def calculate_hash(self):
        """Блок хэшін есептеу"""
        block_string = f"{self.timestamp}{self.previous_hash}{self.merkle_root}"
        return simple_hash(block_string)

# ----------------- 3. БЛОКЧЕЙН -----------------

class Blockchain:
    def __init__(self):
        self.chain = [Block([], "0")]
        self.utxo = {"Alice": 100}

    def add_block(self, transactions):
        """Жаңа блок қосу"""
        if not self.validate_transactions(transactions):
            return False
        previous_block = self.chain[-1]
        new_block = Block(transactions, previous_block.hash)
        self.chain.append(new_block)
        self.update_balances(transactions)
        return True

    def validate_transactions(self, transactions):
        """Транзакцияларды тексеру"""
        balances = self.utxo.copy()
        for tx in transactions:
            sender, recipient, amount = tx["sender"], tx["recipient"], tx["amount"]
            if sender != "SYSTEM":
                if sender not in balances or balances[sender] < amount:
                    return False
                balances[sender] -= amount
            balances[recipient] = balances.get(recipient, 0) + amount
        return True

    def update_balances(self, transactions):
        """UTXO жаңарту"""
        for tx in transactions:
            sender, recipient, amount = tx["sender"], tx["recipient"], tx["amount"]
            if sender != "SYSTEM":
                self.utxo[sender] -= amount
            self.utxo[recipient] = self.utxo.get(recipient, 0) + amount

# ----------------- 4. САНДЫҚ ҚОЛТАҢБА ЖӘНЕ АККАУНТТАР -----------------

class Wallet:
    def __init__(self):
        """Жеке және ашық кілттерді жасау (Аккаунт адресі - ашық кілт)"""
        self.key = RSA.generate(1024)
        self.private_key = self.key.export_key()
        self.public_key = self.key.publickey().export_key()

    def sign_transaction(self, transaction):
        """Транзакцияға қол қою (Жеке кілтпен)"""
        h = SHA256.new(json.dumps(transaction).encode())
        signature = pkcs1_15.new(self.key).sign(h)
        return signature.hex()

    @staticmethod
    def verify_signature(transaction, signature, public_key):
        """Қолтаңбаны тексеру (Ашық кілт арқылы)"""
        h = SHA256.new(json.dumps(transaction).encode())
        rsa_key = RSA.import_key(public_key)
        try:
            pkcs1_15.new(rsa_key).verify(h, bytes.fromhex(signature))
            return True
        except ValueError:
            return False

# ----------------- 5. ӘМИЯН GUI -----------------

class BlockchainGUI(QWidget):
    def __init__(self, blockchain):
        super().__init__()
        self.blockchain = blockchain
        self.init_ui()

    def init_ui(self):
        self.layout = QVBoxLayout()
        self.text_area = QTextEdit()
        self.button = QPushButton("Блоктарды көрсету")
        self.button.clicked.connect(self.show_blocks)
        self.layout.addWidget(self.text_area)
        self.layout.addWidget(self.button)
        self.setLayout(self.layout)

    def show_blocks(self):
        """Блокчейн ақпаратын GUI-да көрсету"""
        text = ""
        for i, block in enumerate(self.blockchain.chain):
            text += f"Блок {i}:\n"
            text += f"  Уақыт: {block.timestamp}\n"
            text += f"  Алдыңғы хэш: {block.previous_hash}\n"
            text += f"  Меркле түбірі: {block.merkle_root}\n"
            text += f"  Хэш: {block.hash}\n\n"
        self.text_area.setText(text)

# ----------------- 6. ТРАНЗАКЦИЯЛАРДЫҢ ВАЛИДАЦИЯСЫ -----------------

if __name__ == "__main__":
    bc = Blockchain()
    
    wallet1 = Wallet()
    wallet2 = Wallet()
    
    tx1 = {"sender": "Alice", "recipient": "Bob", "amount": 10}
    tx2 = {"sender": "Bob", "recipient": "Charlie", "amount": 5}
    tx3 = {"sender": "SYSTEM", "recipient": "Alice", "amount": 50}
    
    signature1 = wallet1.sign_transaction(tx1)
    signature2 = wallet2.sign_transaction(tx2)
    
    if Wallet.verify_signature(tx1, signature1, wallet1.public_key):
        print("Tx1 жарамды")
    if Wallet.verify_signature(tx2, signature2, wallet2.public_key):
        print("Tx2 жарамды")
    
    if bc.add_block([tx1, tx3]):
        print("Блок 1 қосылды!")
    if bc.add_block([tx2]):
        print("Блок 2 қосылды!")
    
    app = QApplication([])
    gui = BlockchainGUI(bc)
    gui.show()
    app.exec_()
