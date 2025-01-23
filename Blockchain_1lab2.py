import time

# Қарапайым блок құрылымы
class Block:
    def __init__(self, index, timestamp, data, previous_hash=""):
        self.index = index  # Блоктың реттік нөмірі
        self.timestamp = timestamp  # Уақыт таңбасы
        self.data = data  # Блоктың деректері
        self.previous_hash = previous_hash  # Алдыңғы блоктың хэші
        self.hash = self.calculate_hash()  # Ағымдағы блоктың хэші

    def calculate_hash(self):
        # Блок хэшін есептеу үшін қарапайым хэш алгоритмі
        content = str(self.index) + self.timestamp + self.data + self.previous_hash
        return simple_hash(content)  # Жоғарыда жазылған `simple_hash` функциясын қолданамыз


# Генезис блогын құру функциясы
def create_genesis_block():
    return Block(0, time.ctime(), "Genesis Block", "0")


# Алдыңғы хэш алгоритмін осында қолданамыз
def simple_hash(input_string):
    hash_value = 0
    prime = 31
    for char in input_string:
        hash_value = (hash_value * prime + ord(char)) % (2**32)
    return hex(hash_value)  # Хэшті он алтылық форматта беру


# Тест
if __name__ == "__main__":
    # Генезис блогын құру
    genesis_block = create_genesis_block()

    print("Genesis Block:")
    print(f"Index: {genesis_block.index}")
    print(f"Timestamp: {genesis_block.timestamp}")
    print(f"Data: {genesis_block.data}")
    print(f"Previous Hash: {genesis_block.previous_hash}")
    print(f"Hash: {genesis_block.hash}")
