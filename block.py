__author__          = 'agsvn'

import json

from time import time
from hashlib import sha256

class block:
    def __init__(self, index, prevhash, transactions, timestamp=None, proof=0, hash=''):
        self.index = index
        self.prevhash = prevhash
        self.hash = hash
        self.transactions = transactions
        self.timestamp = timestamp or time()
        self.proof = proof

    def __str__(self):
        return f"{ self.index }:{ self.prevhash }:{ json.dumps(self.transactions) }:{ self.timestamp }:{ self.proof }"

    def generate_hash(self):
        hash = sha256(self.__str__().encode()).hexdigest()

        # block hash must start with '4c43' (LC) to be valid
        while hash[:4] != '4c43':
            self.proof += 1
            hash = sha256(self.__str__().encode()).hexdigest()

        self.hash = hash
        return (self.proof, hash)

    def dictify(self):
        return {
            'index': self.index,
            'prevhash': self.prevhash,
            'hash': self.hash,
            'proof': self.proof,
            'transactions': self.transactions,
            'timestamp': self.timestamp
        }