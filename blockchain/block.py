__author__          = 'agsvn'

import json

from time import time
from hashlib import sha256

from lib.binary import BinaryWriter
from blockchain.transaction import *

class block:
    def __init__(self, index, prevhash, transactions, timestamp=None, proof=0, hash=''):
        self.index = index
        self.prevhash = prevhash
        self.hash = hash
        self.proof = proof
        self.transactions = transactions
        self.timestamp = timestamp or int(time() * 1000.0)

    def __str__(self):
        return f"{ self.index }:{ self.prevhash }:{ json.dumps(self.transactions) }:{ self.timestamp }:{ self.proof }"

    def __bytes__(self):
        bw = BinaryWriter()
        bw.WriteBytes(b'blockdata')
        bw.WriteInt32(self.index)
        bw.WriteString(self.prevhash)
        bw.WriteString(self.hash)
        bw.WriteInt32(self.proof)
        bw.WriteInt32(len(self.transactions))
        for tx in self.transactions:
            txBytes = bytes(transaction(**tx))
            bw.WriteBytes(txBytes)
        bw.WriteInt64(self.timestamp)
        return bytes(bw)
    
    @staticmethod
    def read(br):
        index = br.ReadInt32()
        prevhash = br.ReadString()
        hash = br.ReadString()
        proof = br.ReadInt32()
        txCount = br.ReadInt32()

        txs = []
        for i in range(txCount):
            tx = transaction.read(br).dictify()
            txs.append(tx)

        timestamp = br.ReadInt64()

        return block(index, prevhash, txs, timestamp, proof, hash)

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