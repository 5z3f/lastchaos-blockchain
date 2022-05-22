__author__          = 'agsvn'

import json
import random

from time import time
from hashlib import sha256
from lib.binary import BinaryWriter

class transaction:
    def __init__(self, sender, recipient, data=None, publicKey='', signature='', timestamp=None, txid=None):
        self.txid = txid or sha256(str(random.getrandbits(128)).encode()).hexdigest()
        self.sender = sender
        self.recipient = recipient
        self.data = data
        self.publicKey = publicKey
        self.signature = signature
        self.timestamp = timestamp or int(time() * 1000.0)

    def __str__(self):
        return f"{ self.txid }:{ self.sender }:{ self.recipient }:{ json.dumps(self.data) }:{ self.publicKey }:{ self.signature }:{ self.timestamp }"

    def __bytes__(self):
        bw = BinaryWriter()
        bw.WriteString(self.txid)
        bw.WriteString(self.sender)
        bw.WriteString(self.recipient)
        bw.WriteString(json.dumps(self.data))
        bw.WriteString(self.publicKey)
        bw.WriteString(self.signature)
        bw.WriteInt64(self.timestamp)
        return bytes(bw)

    @staticmethod
    def read(br):
        txid = br.ReadString()
        sender = br.ReadString()
        recipient = br.ReadString()
        data = json.loads(br.ReadString())
        publicKey = br.ReadString()
        signature = br.ReadString()
        timestamp = br.ReadInt64()
        return transaction(sender, recipient, data, publicKey, signature, timestamp, txid)

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