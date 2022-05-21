__author__          = 'agsvn'

from time import time
from hashlib import sha256

class transaction:
    def __init__(self, sender, recipient, data, timestamp=None):
        self.timestamp = timestamp or time()
        self.sender = sender
        self.recipient = recipient
        self.data = data
        self.hash = sha256(f"{ self.data }:{ self.timestamp }".encode()).hexdigest()

    def dictify(self):
        return {
            'hash': self.hash,
            'sender': self.sender,
            'recipient': self.recipient,
            'data': self.data,
            'timestamp': self.timestamp
        }