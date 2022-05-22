__author__          = 'agsvn'

import json
import ecdsa
import hashlib
import base58

class wallet:
    def __init__(self, privateKey):
        self.privateKey = privateKey
        self.publicKey = ecdsa.SigningKey.from_string(bytes.fromhex(privateKey), curve=ecdsa.SECP256k1).get_verifying_key().to_string().hex()
        self.address = self.create_address(self.publicKey)

    def __str__(self):
        return f"{ self.privateKey }:{ self.publicKey }:{ self.address }"

    @staticmethod
    def generate(entropy=None):
        privateKey = ecdsa.SigningKey.generate(curve=ecdsa.SECP256k1) if entropy is None else ecdsa.SigningKey.from_string(bytes.fromhex(entropy), curve=ecdsa.SECP256k1)
        publicKey = privateKey.get_verifying_key().to_string().hex()

        return {
            'private_key': privateKey.to_string().hex(),
            'public_key': publicKey,
            'address': wallet.create_address(publicKey)
        }
    
    @staticmethod
    def create_address(publicKey):
        sha0 = hashlib.sha256(bytearray.fromhex('04' + publicKey))

        ripemd = hashlib.new('ripemd160')
        ripemd.update(sha0.digest())

        keyhash = "00" + ripemd.hexdigest()

        sha256x2 = hashlib.sha256(hashlib.sha256(bytearray.fromhex(keyhash)).digest()).hexdigest()
        checksum = sha256x2[:8]

        return 'lc' + base58.b58encode(bytes(bytearray.fromhex(keyhash + checksum))).decode('utf-8')
    
    def sign(self, message):
        sk = ecdsa.SigningKey.from_string(bytes.fromhex(self.privateKey), curve=ecdsa.SECP256k1, hashfunc=hashlib.sha256)
        messageHash = hashlib.sha256(message.encode()).hexdigest()
        signature = sk.sign(messageHash.encode(), hashfunc=hashlib.sha256).hex()
        return signature

    @staticmethod
    def verify(publicKey, signature, message):
        try:
            vk = ecdsa.VerifyingKey.from_string(bytes.fromhex(publicKey), curve=ecdsa.SECP256k1, hashfunc=hashlib.sha256)
            messageHash = hashlib.sha256(message.encode()).hexdigest()
            return vk.verify(bytes.fromhex(signature), messageHash.encode(), hashfunc=hashlib.sha256)
        except:
            return False

    @staticmethod
    def balance(chain, address):
        balance = 0

        for block in chain.blocks:
            for tx in block['transactions']:
                if tx['data']['entity'] == 'gold':
                    if tx['sender'] == address:
                        balance -= tx['data']['amount']
                    elif tx['recipient'] == address:
                        balance += tx['data']['amount']

        for tx in chain.current_transactions:
            if tx['data']['entity'] == 'gold':
                if tx['sender'] == address:
                    balance -= tx['data']['amount']
                elif tx['recipient'] == address:
                    balance += tx['data']['amount']

        return balance
