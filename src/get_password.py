import hashlib

password = 'eisman'
hashed = hashlib.sha1(password).hexdigest()

print hashed
