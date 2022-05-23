__author__          = 'agsvn'

import os
import json

from time import sleep

from block import *
from wallet import *
from transaction import *

from lib.binary import BinaryReader

class chain:
    def __init__(self):
        self.blocks = []
        self.current_transactions = []
        self.blocks_directory = os.getcwd() + '\\blocks'
        
        self.options = {
            'name': 'mainnet',
            'create_block_every': 10,
            'binary': True
        }

    def __str__(self):
        return json.dumps(self.dictify(), indent=4)

    def mineBlock(self):
        while True:
            if len(self.current_transactions) > 0:
                newBlock = self.add(type='block')
                print(f'blockchain :: created block { newBlock.index }')
            else:
                print(f'blockchain :: waiting for transactions')
                
            sleep(self.options['create_block_every'])

    def nextBlockId(self):
        return len(self.blocks)

    def load(self):
        files = [f for f in os.listdir(self.blocks_directory) if f.endswith('.bin' if self.options['binary'] else '.json')]
        print('blockchain :: found', len(files), 'blocks')
        for f in files:
            fname = f

            if self.options['binary']:
                try: 
                    with open(f'{ self.blocks_directory }/{ f }', 'rb') as f:
                        br = BinaryReader(f)
                                                
                        if br.ReadBytes(9) != b'blockdata':
                            raise Exception('invalid block file, file: ' + fname)
                        
                        data = block.read(br).dictify()
                        self.blocks.append(data)
                        print(f'blockchain :: loaded { fname } ({ data["index"] + 1 } of { len(files) })')
                except Exception as e:
                    print(f'blockchain :: error loading block { fname }: { e }')
                    continue
            else:
                with open(f'{ self.blocks_directory }/{ f }', 'r') as f:
                    try:
                        data = json.load(f)
                        self.blocks.append(data)
                        print(f'blockchain :: loaded { fname } ({ data["index"] + 1 } of { len(files) })')
                    except Exception as e:
                        print(f'blockchain :: error loading block { fname }: { e }')
                        continue

    def find(self, type, id):
        match type:
            case 'block':
                return block(**self.blocks[id])
            case 'transaction':
                for tx in self.current_transactions:
                    if tx['txid'] == id:
                        return transaction(**tx)
                for _block in self.blocks:
                    for tx in _block['transactions']:
                        if tx['txid'] == id:
                            return transaction(**tx)
                
    def add(self, type, data=None):
        match type:
            case 'block':
                # previous block
                previous_block_hash = block(**self.blocks[-1]).hash if len(self.blocks) > 0 else '0'

                # create block
                newBlock = block(index=len(self.blocks), prevhash=previous_block_hash, transactions=self.current_transactions)

                # compute hash for block
                newBlock.generate_hash()

                # append block to chain
                self.blocks.append(newBlock.dictify())

                if self.options['binary']:
                    # save block to file as binary
                    with open(f'./blocks/{ newBlock.index }.bin', 'wb') as f:
                        f.write(bytes(newBlock))
                
                else:
                    # save block to file as json
                    with open(f'./blocks/{ newBlock.index }.json', 'w') as f:
                        json.dump(newBlock.dictify(), f, indent=4)

                # empty current transactions
                self.current_transactions = []

                # return new block
                return newBlock

            case 'transaction':
                tx = data

                if tx.sender != 'genesis':
                    if not wallet.verify(publicKey=tx.publicKey, signature=tx.signature, message=tx.message()):
                        return {'success': False, 'message': 'could not verify transaction (invalid signature)' }

                    # verify that the sender address matches the address derived with public key
                    if wallet.create_address(publicKey=tx.publicKey) != tx.sender:
                        return {'success': False, 'message': 'could not verify transaction (invalid sender address)' }

                    if tx.data['type'] == 'transfer':
                        if tx.data['amount'] < 0:
                            return {'success': False, 'message': 'could not verify transaction (invalid amount)' }

                        if tx.data['entity'] == 'gold' or tx.data['entity'] == 'cash':                            
                            if tx.data['amount'] > wallet.balance(chain=self, address=tx.sender)[tx.data['entity']]:
                                return {'success': False, 'message': 'could not verify transaction (insufficient funds)' }
                        elif tx.data['entity'] == 'item':
                            if not wallet.hasItem(chain=self, address=tx.sender, uid=tx.data['data']['uid']):
                                return { 'success': False, 'message': 'could not verify transaction (sender does not have that item)' }
                
                self.current_transactions.append(tx.dictify())
                return { 'success': True, 'message': 'transaction added', 'tx': tx.dictify() }
    
    def validate(self):
        for i in range(1, len(self.blocks)):
            previousBlock = block(**self.blocks[i - 1])
            currentBlock = block(**self.blocks[i])
            
            currentBlockHash = sha256(str(currentBlock).encode()).hexdigest()
            if (currentBlock.prevhash != previousBlock.hash) or (currentBlock.hash != currentBlockHash):
                return False
        return True

    def dictify(self):
        return {
            'name': self.options['name'],
            'valid': self.validate(),
            'block_mined_every': self.options['create_block_every'],
            'txs_pending': self.current_transactions,
            'blocks': self.blocks
        }