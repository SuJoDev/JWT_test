import hashlib

sha256_hash = hashlib.new('sha256')

data = 'Hello, world!'
sha256_hash.update(data.encode())

print(data)

