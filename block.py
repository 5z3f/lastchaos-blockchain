__author__          = 'agsvn'

from time import time
from hashlib import sha256

class block:
    def __init__(self, index, prevhash, transactions, timestamp=None, proof=0, hash=''):
        self.index = index
        self.hash = hash
        self.prevhash = prevhash
        self.transactions = transactions
        self.timestamp = timestamp or time()
        self.proof = proof

    def generate_hash(self):
        hash = sha256(self.__str__().encode()).hexdigest()

        # while hash not starts with 4c43
        while hash[:4] != '4c43':
            self.proof += 1
            hash = sha256(self.__str__().encode()).hexdigest()

        self.hash = hash
        return (self.proof, hash)


    def __str__(self):
        return f"{ self.index }:{ self.prevhash }:{ self.proof }:{ self.transactions }:{ self.timestamp }:{ self.proof }"

    def dictify(self):
        return {
            'index': self.index,
            'hash': self.hash,
            'prevhash': self.prevhash,
            'proof': self.proof,
            'transactions': self.transactions,
            'timestamp': self.timestamp,
        }