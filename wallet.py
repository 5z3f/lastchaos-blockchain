__author__          = 'agsvn'

import json
import ecdsa
import hashlib
import codecs
import base58
import binascii

class wallet:
    def generate(entropy=None):
        priv = ecdsa.SigningKey.generate(curve=ecdsa.SECP256k1) if entropy is None else ecdsa.SigningKey.from_string(codecs.decode(entropy, 'hex'), curve=ecdsa.SECP256k1)
        pub = priv.get_verifying_key()
        pub_uncompressed = (b'04' + codecs.encode(pub.to_string(), 'hex')).decode("utf-8")

        # Checking if the last byte is odd or even
        pub_compressed = '02' if not ord(bytearray.fromhex(pub_uncompressed[-2:])) % 2 else '03'

        # Add bytes 0x02 to the X of the key if even or 0x03 if odd
        pub_compressed += pub_uncompressed[2:66]

        return {
            'masterkey': priv.to_string().hex(),
            'pub': {
                'uncompressed': pub_uncompressed,
                'compressed': pub_compressed
            },
            'wif': {
                'uncompressed': wallet.create_wif(priv.to_string().hex(), compressed=False),
                'compressed': wallet.create_wif(priv.to_string().hex(), compressed=True)
            },
            'address': {
                'uncompressed': wallet.create_address(pub_uncompressed),
                'compressed': wallet.create_address(pub_compressed)
            }
        }

    def create_address(pubkey):
        sha0 = hashlib.sha256(bytearray.fromhex(pubkey))

        ripemd = hashlib.new('ripemd160')
        ripemd.update(sha0.digest())

        keyhash = "00" + ripemd.hexdigest()

        sha256x2 = hashlib.sha256(hashlib.sha256(bytearray.fromhex(keyhash)).digest()).hexdigest()
        checksum = sha256x2[:8]

        return base58.b58encode(bytes(bytearray.fromhex(keyhash + checksum))).decode('utf-8')

    def create_wif(privkey, compressed=False):
        mainnet_privkey = '80' + privkey if not compressed else '80' + privkey + '01'
        sha256x2 = hashlib.sha256(binascii.unhexlify(hashlib.sha256(binascii.unhexlify(mainnet_privkey)).hexdigest())).hexdigest()

        return base58.b58encode(binascii.unhexlify(mainnet_privkey + sha256x2[:8])).decode('utf-8')

    def load(name):
        with open(f'{ name }_wallet.json') as f:
            return json.load(f)

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
