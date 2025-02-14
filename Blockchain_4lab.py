import json
import time
import hashlib
import requests
import threading
from flask import Flask, request, jsonify
from flask_socketio import SocketIO, emit
import tkinter as tk
from tkinter import scrolledtext

app = Flask(__name__)
socketio = SocketIO(app)

class Blockchain:
    #Түйіндер
    def __init__(self):
        self.chain = []
        self.transactions = []
        self.nodes = set()
        self.create_block(proof=1, previous_hash='0')
    def create_block(self, proof, previous_hash):
        block = {
            'index': len(self.chain) + 1,
            'timestamp': time.time(),
            'transactions': self.transactions,
            'proof': proof,
            'previous_hash': previous_hash
        }
        self.transactions = []
        self.chain.append(block)
        return block
    def add_transaction(self, sender, receiver, amount):
        self.transactions.append({
            'sender': sender,
            'receiver': receiver,
            'amount': amount
        })
        return self.last_block['index'] + 1
    @staticmethod
    def hash(block):
        return hashlib.sha256(json.dumps(block, sort_keys=True).encode()).hexdigest()
    @property
    def last_block(self):
        return self.chain[-1]
blockchain = Blockchain()

# Әмиян интеграциясын қосу. 
@app.route('/transactions/new', methods=['POST'])
def new_transaction():
    data = request.get_json()
    index = blockchain.add_transaction(data['sender'], data['receiver'], data['amount'])
    return jsonify({'message': f'Transaction added to Block {index}'}), 201

@app.route('/mine', methods=['GET'])
def mine_block():
    last_block = blockchain.last_block
    last_proof = last_block['proof']
    proof = last_proof + 1  # Simple PoW example
    previous_hash = blockchain.hash(last_block)
    block = blockchain.create_block(proof, previous_hash)
    return jsonify({'message': 'Block Mined', 'block': block}), 200

#Блок Эксплорер жаңарту.
@app.route('/chain', methods=['GET'])
def full_chain():
    return jsonify({'chain': blockchain.chain, 'length': len(blockchain.chain)}), 200

@app.route('/nodes/register', methods=['POST'])
def register_nodes():
    data = request.get_json()
    nodes = data.get('nodes')
    if nodes is None:
        return jsonify({'message': 'Invalid node list'}), 400
    for node in nodes:
        blockchain.nodes.add(node)
    return jsonify({'message': 'Nodes added', 'total_nodes': list(blockchain.nodes)}), 201

# Блок құру 
@socketio.on('broadcast_block')
def broadcast_block(data):
    for node in blockchain.nodes:
        try:
            requests.post(f'http://{node}/chain', json={'block': data})
        except requests.exceptions.RequestException:
            pass

def start_server():
    socketio.run(app, host='0.0.0.0', port=5000)

threading.Thread(target=start_server, daemon=True).start()

# GUI
root = tk.Tk()
root.title("Blockchain GUI")

log = scrolledtext.ScrolledText(root, width=50, height=20)
log.pack()

def mine():
    response = requests.get("http://127.0.0.1:5000/mine").json()
    log.insert(tk.END, f"{response['message']}: {response['block']}\n")

def show_chain():
    response = requests.get("http://127.0.0.1:5000/chain").json()
    log.insert(tk.END, f"Blockchain: {response['chain']}\n")

tk.Button(root, text="Mine Block", command=mine).pack()
tk.Button(root, text="Show Chain", command=show_chain).pack()
root.mainloop()
