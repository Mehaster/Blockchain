import time

# Блок құрылымы
class Block:
    def __init__(self, index, timestamp, data, previous_hash=""):
        self.index = index  # Блоктың реттік нөмірі
        self.timestamp = timestamp  # Уақыт таңбасы
        self.data = data  # Блоктың деректері
        self.previous_hash = previous_hash  # Алдыңғы блоктың хэші
        self.hash = self.calculate_hash()  # Ағымдағы блоктың хэші

    def calculate_hash(self):
        # Хэшті есептеу үшін жоғарыда қарастырылған қарапайым хэш алгоритмі қолданылады
        content = str(self.index) + self.timestamp + self.data + self.previous_hash
        return simple_hash(content)


# Блокчейн құрылымы
class Blockchain:
    def __init__(self):
        self.chain = [self.create_genesis_block()]  # Генезис блогы тізбектің басталуы

    def create_genesis_block(self):
        return Block(0, time.ctime(), "Genesis Block", "0")

    def get_latest_block(self):
        return self.chain[-1]  # Соңғы блокты қайтару

    def add_block(self, new_block):
        # Жаңа блокты тізбекке қосу
        new_block.previous_hash = self.get_latest_block().hash
        new_block.hash = new_block.calculate_hash()
        self.chain.append(new_block)

    def is_chain_valid(self):
        # Блокчейннің дұрыстығын тексеру
        for i in range(1, len(self.chain)):
            current_block = self.chain[i]
            previous_block = self.chain[i - 1]

            # Ағымдағы блоктың хэші дұрыс па?
            if current_block.hash != current_block.calculate_hash():
                print(f"Block {i} has invalid hash.")
                return False

            # Алдыңғы блоктың хэші дұрыс па?
            if current_block.previous_hash != previous_block.hash:
                print(f"Block {i} has invalid previous hash.")
                return False

        return True


# Қарапайым хэш функциясы (жоғарыда жазылған)
def simple_hash(input_string):
    hash_value = 0
    prime = 31
    for char in input_string:
        hash_value = (hash_value * prime + ord(char)) % (2**32)
    return hex(hash_value)


# Тест
if __name__ == "__main__":
    # Блокчейнді құру
    blockchain = Blockchain()

    # Жаңа блоктарды қосу
    blockchain.add_block(Block(1, time.ctime(), "Block 1 Data"))
    blockchain.add_block(Block(2, time.ctime(), "Block 2 Data"))
    blockchain.add_block(Block(3, time.ctime(), "Block 3 Data"))

    # Блоктарды көрсету
    print("Blockchain:")
    for block in blockchain.chain:
        print(f"Index: {block.index}, Timestamp: {block.timestamp}, Data: {block.data}, Hash: {block.hash}, Previous Hash: {block.previous_hash}")

    # Тізбектің дұрыстығын тексеру
    print("\nIs blockchain valid?", blockchain.is_chain_valid())
