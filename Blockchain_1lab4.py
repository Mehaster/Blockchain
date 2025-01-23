import tkinter as tk
from tkinter import messagebox
import time


# Блок құрылымы
class Block:
    def __init__(self, index, timestamp, data, previous_hash=""):
        self.index = index
        self.timestamp = timestamp
        self.data = data
        self.previous_hash = previous_hash
        self.hash = self.calculate_hash()

    def calculate_hash(self):
        content = str(self.index) + self.timestamp + self.data + self.previous_hash
        return simple_hash(content)


# Блокчейн құрылымы
class Blockchain:
    def __init__(self):
        self.chain = [self.create_genesis_block()]

    def create_genesis_block(self):
        return Block(0, time.ctime(), "Genesis Block", "0")

    def get_latest_block(self):
        return self.chain[-1]

    def add_block(self, data):
        new_block = Block(
            len(self.chain),
            time.ctime(),
            data,
            self.get_latest_block().hash,
        )
        self.chain.append(new_block)

    def is_chain_valid(self):
        for i in range(1, len(self.chain)):
            current_block = self.chain[i]
            previous_block = self.chain[i - 1]

            # Тек ағымдағы блоктың хэші дұрыс па?
            if current_block.hash != current_block.calculate_hash():
                return False

            # Алдыңғы блоктың хэші дұрыс па?
            if current_block.previous_hash != previous_block.hash:
                return False

        return True


# Қарапайым хэш функциясы
def simple_hash(input_string):
    hash_value = 0
    prime = 31
    for char in input_string:
        hash_value = (hash_value * prime + ord(char)) % (2**32)
    return hex(hash_value)


# Блокчейн GUI
class BlockchainExplorer:
    def __init__(self, root):
        self.blockchain = Blockchain()  # Блокчейн объектісі
        self.root = root
        self.root.title("Blockchain Explorer")

        # Интерфейстің элементтері
        self.add_block_frame = tk.Frame(self.root)
        self.add_block_frame.pack(pady=10)

        self.data_entry = tk.Entry(self.add_block_frame, width=50)
        self.data_entry.pack(side=tk.LEFT, padx=10)

        self.add_block_button = tk.Button(
            self.add_block_frame, text="Add Block", command=self.add_block
        )
        self.add_block_button.pack(side=tk.LEFT)

        self.validate_button = tk.Button(
            self.root, text="Validate Blockchain", command=self.validate_chain
        )
        self.validate_button.pack(pady=10)

        self.block_list = tk.Listbox(self.root, width=100, height=20)
        self.block_list.pack(pady=10)

        # Генезис блогын көрсету
        self.update_block_list()

    def add_block(self):
        data = self.data_entry.get()
        if not data:
            messagebox.showwarning("Input Error", "Please enter data for the block!")
            return

        self.blockchain.add_block(data)
        self.update_block_list()
        self.data_entry.delete(0, tk.END)

    def validate_chain(self):
        if self.blockchain.is_chain_valid():
            messagebox.showinfo("Blockchain Validation", "The blockchain is valid!")
        else:
            messagebox.showerror(
                "Blockchain Validation", "The blockchain is INVALID!"
            )

    def update_block_list(self):
        self.block_list.delete(0, tk.END)  # Блок тізімін тазалау

        for block in self.blockchain.chain:
            block_info = (
                f"Index: {block.index}, "
                f"Timestamp: {block.timestamp}, "
                f"Data: {block.data}, "
                f"Hash: {block.hash}, "
                f"Previous Hash: {block.previous_hash}"
            )
            self.block_list.insert(tk.END, block_info)


# Негізгі бағдарлама
if __name__ == "__main__":
    root = tk.Tk()
    app = BlockchainExplorer(root)
    root.mainloop()
