import hashlib
import time
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QTextEdit, QLineEdit, QLabel
import sys

class Block:
    def __init__(self, index, previous_hash, transactions, difficulty, miner):
        self.index = index
        self.previous_hash = previous_hash
        self.transactions = transactions
        self.timestamp = time.time()
        self.difficulty = difficulty
        self.nonce = 0
        self.miner = miner
        self.hash = self.mine_block()
    
    def calculate_hash(self):
        block_data = f"{self.index}{self.previous_hash}{self.transactions}{self.timestamp}{self.nonce}{self.difficulty}{self.miner}"
        return hashlib.sha256(block_data.encode()).hexdigest()
    
    def mine_block(self):
        prefix = '0' * self.difficulty
        while True:
            self.nonce += 1
            block_hash = self.calculate_hash()
            if block_hash.startswith(prefix):
                return block_hash

# Блокчейн классы
class Blockchain:
    def __init__(self, difficulty=4, reward=50, fee=5):
        self.difficulty = difficulty  # Ең алдымен difficulty орнату керек!
        self.reward = reward
        self.fee = fee
        self.pending_transactions = []
        self.miners = {}
        self.chain = [self.create_genesis_block()]  # Енді difficulty анықталған!

    def create_genesis_block(self):
        return Block(0, "0", "Genesis Block", self.difficulty, "Genesis")
    
    def add_transaction(self, transaction):
        self.pending_transactions.append(transaction)
    
    def mine_pending_transactions(self, miner_address):
        # Жүлде мен комиссия механизмі
        total_fees = len(self.pending_transactions) * self.fee
        reward_transaction = {"from": "network", "to": miner_address, "amount": self.reward + total_fees}
        self.pending_transactions.append(reward_transaction)
        
        new_block = Block(len(self.chain), self.chain[-1].hash, self.pending_transactions, self.difficulty, miner_address)
        
        if miner_address in self.miners:
            self.miners[miner_address].append(new_block)
        else:
            self.miners[miner_address] = [new_block]
        
        self.resolve_conflict()
    
    def resolve_conflict(self):
        # Миннинг сценарийлері: longest chain ережесі
        longest_chain = sorted(self.miners.values(), key=len, reverse=True)[0]
        self.chain = longest_chain
        self.pending_transactions = []
    
    def print_chain(self):
        for block in self.chain:
            print(f"Index: {block.index}, Hash: {block.hash}, Previous: {block.previous_hash}, Nonce: {block.nonce}, Miner: {block.miner}")

class BlockchainGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.blockchain = Blockchain()
        self.initUI()
    
    def initUI(self):
        self.setWindowTitle("Blockchain PoW GUI")
        self.setGeometry(100, 100, 600, 400)
        
        layout = QVBoxLayout()
        
        self.log = QTextEdit()
        self.log.setReadOnly(True)
        layout.addWidget(self.log)
        
        self.tx_input = QLineEdit()
        self.tx_input.setPlaceholderText("Введите транзакцию (Пример: Alice -> Bob: 10)")
        layout.addWidget(self.tx_input)
        
        self.add_tx_button = QPushButton("Добавить транзакцию")
        self.add_tx_button.clicked.connect(self.add_transaction)
        layout.addWidget(self.add_tx_button)
        
        self.miner_input = QLineEdit()
        self.miner_input.setPlaceholderText("Введите имя майнера")
        layout.addWidget(self.miner_input)
        
        self.mine_button = QPushButton("Майнить блок")
        self.mine_button.clicked.connect(self.mine_block)
        layout.addWidget(self.mine_button)
        
        self.setLayout(layout)
        self.update_log()
    
    def add_transaction(self):
        tx_text = self.tx_input.text()
        if "->" in tx_text and ":" in tx_text:
            parts = tx_text.split("->")
            sender = parts[0].strip()
            receiver, amount = parts[1].split(":")
            self.blockchain.add_transaction({"from": sender, "to": receiver.strip(), "amount": int(amount)})
            self.log.append(f"Транзакция добавлена: {tx_text}")
            self.tx_input.clear()
            self.update_log()
        else:
            self.log.append("Ошибка: неверный формат транзакции!")
    
    def mine_block(self):
        miner = self.miner_input.text().strip()
        if miner:
            self.blockchain.mine_pending_transactions(miner)
            self.log.append(f"Блок замайнен майнером {miner}")
            self.update_log()
        else:
            self.log.append("Ошибка: введите имя майнера!")
    
    def update_log(self):
        self.log.append("\nАктуальная цепочка блоков:")
        for block in self.blockchain.chain:
            self.log.append(f"Блок {block.index} | Хеш: {block.hash[:10]}... | Предыдущий: {block.previous_hash[:10]}... | Майнер: {block.miner}")
        self.log.append("--------------------------------")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    gui = BlockchainGUI()
    gui.show()
    sys.exit(app.exec())
