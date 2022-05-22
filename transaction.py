__author__          = 'agsvn'

import json
import random

from time import time
from hashlib import sha256

class transaction:
    def __init__(self, sender, recipient, data=None, publicKey=None, signature=None, timestamp=None, txid=None):
        self.txid = txid or sha256(str(random.getrandbits(128)).encode()).hexdigest()
        self.timestamp = timestamp or time()
        self.sender = sender
        self.recipient = recipient
        self.data = data
        self.publicKey = publicKey
        self.signature = signature

    def __str__(self):
        return f"{ self.txid }:{ self.sender }:{ self.recipient }:{ json.dumps(self.data) }:{ self.publicKey }:{ self.signature }:{ self.timestamp }"

    def __bytes__(self):
        pass

    def message(self):
        return f"{ self.sender }:{ self.recipient }:{ json.dumps(self.data) }"
    
    def dictify(self):            
        return {
            'txid': self.txid,
            'sender': self.sender,
            'recipient': self.recipient,
            'data': self.data,
            'publicKey': self.publicKey,
            'signature': self.signature,
            'timestamp': self.timestamp
        }