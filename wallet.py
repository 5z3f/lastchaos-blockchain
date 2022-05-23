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
    def search(chain, address, type=None):
        transactions = []

        if address == 'genesis':
            return transactions

        # iterate through all blocks in the chain
        for block in chain.blocks:
            for tx in block['transactions']:
                if tx['sender'] == address or tx['recipient'] == address:
                    if tx['data']['type'] == type or type is None:
                        transactions.append(tx)

        # iterate through all pending transactions
        for tx in chain.current_transactions:
            if tx['sender'] == address or tx['recipient'] == address:
                if tx['data']['type'] == type or type is None:
                    transactions.append(tx)

        return transactions

    @staticmethod
    def balance(chain, address):
        currencies = {
            'gold': 0,
            'cash': 0
        }

        if address == 'genesis':
            return currencies

        txs = wallet.search(chain, address, 'transfer')

        for tx in txs:
            if tx['data']['entity'] in currencies.keys():
                if tx['sender'] == address:
                    currencies[tx['data']['entity']] -= tx['data']['amount']
                elif tx['recipient'] == address:
                    currencies[tx['data']['entity']] += tx['data']['amount']

        return currencies

    @staticmethod
    def inventory(chain, address):
        inventory = []

        txs = wallet.search(chain, address, 'transfer')

        for tx in txs:
            txData = tx['data']
            if tx['data']['entity'] == 'item':
                if tx['recipient'] == address:
                    inventory.append(txData['data'])
                elif tx['sender'] == address:
                    for item in inventory:
                        if item['uid'] == txData['data']['uid']:
                            inventory.remove(item)
                            break

        return inventory

    @staticmethod
    def hasItem(chain, address, uid):
        inventory = wallet.inventory(chain, address)

        for item in inventory:
            if item['uid'] == uid:
                return True

        return False