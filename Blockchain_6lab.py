import time
import hashlib
import random
import tkinter as tk
from tkinter import messagebox, scrolledtext
from ecdsa import SigningKey, VerifyingKey, SECP256k1

# Хэш функция (SHA-256)
def sha256_hash(data):
    return hashlib.sha256(data.encode()).hexdigest()

# Транзакция
class Transaction:
    def __init__(self, sender, receiver, amount, fee, signature=""):
        self.sender = sender
        self.receiver = receiver
        self.amount = amount
        self.fee = fee
        self.timestamp = time.time()
        self.tx_id = sha256_hash(f"{self.sender}{self.receiver}{self.amount}{self.fee}{self.timestamp}")
        self.signature = signature
    
    def sign_transaction(self, private_key):
        message = sha256_hash(f"{self.sender}{self.receiver}{self.amount}{self.fee}{self.timestamp}")
        self.signature = private_key.sign(message.encode()).hex()

# Блок
class Block:
    def __init__(self, previous_hash, transactions, nonce=0):
        self.timestamp = time.time()
        self.previous_hash = previous_hash
        self.transactions = transactions
        self.nonce = nonce
        self.hash = self.compute_hash()
    
    def compute_hash(self):
        block_data = f"{self.timestamp}{self.previous_hash}{self.nonce}"
        for tx in self.transactions:
            block_data += tx.tx_id
        return sha256_hash(block_data)

# Узел блокчейна
class Node:
    def __init__(self, node_id):
        self.node_id = node_id
        self.chain = [self.create_genesis_block()]
        self.pending_transactions = []
        self.difficulty = 4
        self.mining_reward = 10
        self.stake_pool = {}  # Стейкинг қоры
    
    def create_genesis_block(self):
        return Block("0", [])
    
    def mine_block(self, miner_address):
        block = Block(self.chain[-1].hash, self.pending_transactions)
        while block.hash[:self.difficulty] != "0" * self.difficulty:
            block.nonce += 1
            block.hash = block.compute_hash()
        self.chain.append(block)
        self.pending_transactions = [Transaction("System", miner_address, self.mining_reward, 0)]
    
    def add_transaction(self, transaction):
        self.pending_transactions.append(transaction)
    
    def stake(self, address, amount):
        if address in self.stake_pool:
            self.stake_pool[address] += amount
        else:
            self.stake_pool[address] = amount
    
    def select_staker(self):
        total_stake = sum(self.stake_pool.values())
        if total_stake == 0:
            return None
        pick = random.uniform(0, total_stake)
        current = 0
        for address, stake in self.stake_pool.items():
            current += stake
            if current > pick:
                return address
        return None
    
    def stake_mine_block(self):
        staker = self.select_staker()
        if staker:
            block = Block(self.chain[-1].hash, self.pending_transactions)
            self.chain.append(block)
            self.pending_transactions = [Transaction("System", staker, self.mining_reward, 0)]
            return staker
        return None

# GUI
class BlockchainGUI:
    def __init__(self, root):
        self.nodes = {f"Node {i+1}": Node(i+1) for i in range(3)}
        self.wallet = SigningKey.generate(curve=SECP256k1)
        self.public_key = self.wallet.verifying_key
        self.current_node = "Node 1"
        
        root.title("Блокчейн")
        tk.Label(root, text="Түйіндер:").pack()
        
        self.node_var = tk.StringVar(value=self.current_node)
        self.node_menu = tk.OptionMenu(root, self.node_var, *self.nodes.keys(), command=self.update_node)
        self.node_menu.pack()
        
        tk.Label(root, text="Алушы адресі:").pack()
        self.receiver_entry = tk.Entry(root)
        self.receiver_entry.pack()
        
        tk.Label(root, text="Сома:").pack()
        self.amount_entry = tk.Entry(root)
        self.amount_entry.pack()
        
        tk.Label(root, text="Комиссия:").pack()
        self.fee_entry = tk.Entry(root)
        self.fee_entry.pack()
        
        tk.Button(root, text="Транзакция Жіберу", command=self.send_transaction).pack()
        tk.Button(root, text="Майнинг Жүргізу", command=self.mine_block).pack()
        tk.Button(root, text="Стейкингке Қатысу", command=self.stake_funds).pack()
        tk.Button(root, text="Стейкинг арқылы Майнинг", command=self.stake_mining).pack()
        
        self.text_area = scrolledtext.ScrolledText(root, width=60, height=20)
        self.text_area.pack()
        
        self.update_blockchain_view()
    
    def update_node(self, value):
        self.current_node = value
        self.update_blockchain_view()
    
    def update_blockchain_view(self):
        self.text_area.delete(1.0, tk.END)
        node = self.nodes[self.current_node]
        for block in node.chain:
            self.text_area.insert(tk.END, f"Блок хэші: {block.hash}\n")
            self.text_area.insert(tk.END, f"Алдыңғы хэш: {block.previous_hash}\n")
            self.text_area.insert(tk.END, "Транзакциялар:\n")
            for tx in block.transactions:
                self.text_area.insert(tk.END, f"  {tx.sender[:10]}... -> {tx.receiver[:10]}... : {tx.amount} BTC\n")
            self.text_area.insert(tk.END, "-" * 50 + "\n")
    
    def send_transaction(self):
        receiver = self.receiver_entry.get()
        amount = int(self.amount_entry.get())
        fee = int(self.fee_entry.get())
        tx = Transaction(self.public_key.to_string().hex(), receiver, amount, fee)
        tx.sign_transaction(self.wallet)
        self.nodes[self.current_node].add_transaction(tx)
        messagebox.showinfo("Транзакция", "Транзакция сәтті жіберілді!")
        self.update_blockchain_view()
    
    def mine_block(self):
        self.nodes[self.current_node].mine_block(self.public_key.to_string().hex())
        messagebox.showinfo("Майнинг", "Блок табысты жасалды!")
        self.update_blockchain_view()
    
    def stake_funds(self):
        amount = int(self.amount_entry.get())
        self.nodes[self.current_node].stake(self.public_key.to_string().hex(), amount)
        messagebox.showinfo("Стейкинг", "Стейк сәтті қосылды!")
    
    def stake_mining(self):
        winner = self.nodes[self.current_node].stake_mine_block()
        if winner:
            messagebox.showinfo("Стейкинг Майнинг", f"Блок {winner} арқылы құрылды!")
        else:
            messagebox.showinfo("Стейкинг Майнинг", "Стейк жетіспейді!")
        self.update_blockchain_view()

root = tk.Tk()
app = BlockchainGUI(root)
root.mainloop()