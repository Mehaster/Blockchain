def simple_hash(input_string):
    hash_value = 0  # Алғашқы хэш мәні
    prime = 31      # Кіші жай сан, хэштің тұрақтылығын қамтамасыз ету үшін

    for char in input_string:
        # Әр символдың ASCII мәнін пайдаланып хэштеу
        hash_value = (hash_value * prime + ord(char)) % (2**32)  # Хэшті 32 битпен шектеу
    
    return hash_value

# Тест
if __name__ == "__main__":
    test_string = "Hello, World!"
    print(f"Input string: {test_string}")
    print(f"Hash value: {simple_hash(test_string)}")
