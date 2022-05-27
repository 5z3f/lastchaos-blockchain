__author__          = 'agsvn'

import os
import json

from time import sleep

from lib.binary import BinaryReader

from blockchain.block import *
from blockchain.transaction import *
from account.wallet import *

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

        for file in files:
            try:
                nBlock = block.read(fileName=f'{ self.blocks_directory }/{ file }', binary=self.options['binary'])
                self.blocks.append(nBlock)
                print(f'blockchain :: loaded { file } ({ nBlock.index + 1 } of { len(files) })')
            except Exception as e:
                print(f'blockchain :: error loading block { file }: { e }')

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
                previous_block_hash = self.blocks[-1].hash if len(self.blocks) > 0 else '0'

                # create block
                newBlock = block(index=len(self.blocks), prevhash=previous_block_hash, transactions=self.current_transactions)

                # compute hash for block
                newBlock.generate_hash()

                # append block to chain
                self.blocks.append(newBlock)

                # save block to file
                newBlock.save(blockDirectory=self.blocks_directory, binary=self.options['binary'])

                # empty current transactions
                self.current_transactions = []

                # return new block
                return newBlock

            case 'transaction':
                tx = data

                if tx.sender != 'genesis':
                    if not tx.signed:
                        return { 'success': False, 'message': 'transaction not signed' }

                    if not wallet.verify(publicKey=tx.publicKey, signature=tx.signature, message=tx.message()):
                        return { 'success': False, 'message': 'could not verify signature' }

                    if wallet.create_address(publicKey=tx.publicKey) != tx.sender:
                        return { 'success': False, 'message': 'sender address does not match public key address' }

                    if tx.data['type'] == 'transfer':
                        if tx.data['amount'] < 0:
                            return { 'success': False, 'message': 'invalid amount' }

                        if tx.data['entity'] == 'gold' or tx.data['entity'] == 'cash':                            
                            if tx.data['amount'] > wallet.balance(chain=self, address=tx.sender)[tx.data['entity']]:
                                return { 'success': False, 'message': 'insufficient funds' }
                        elif tx.data['entity'] == 'item':
                            if not wallet.hasItem(chain=self, address=tx.sender, uuid=tx.data['data']['uuid']):
                                return { 'success': False, 'message': 'sender does not have item' }

                self.current_transactions.append(tx)
                return { 'success': True, 'message': 'transaction added', 'tx': tx.dictify() }
    
    def validate(self):
        for i in range(1, len(self.blocks)):
            previousBlock = self.blocks[i - 1]
            currentBlock = self.blocks[i]
            
            currentBlockHash = sha256(str(currentBlock).encode()).hexdigest()
            if (currentBlock.prevhash != previousBlock.hash) or (currentBlock.hash != currentBlockHash):
                return False
        return True

    def dictify(self):

        blocks = []
        for nblock in self.blocks:
            blocks.append(nblock.dictify())

        txs = []
        for tx in self.current_transactions:
            txs.append(tx.dictify())      

        return {
            'name': self.options['name'],
            'valid': self.validate(),
            'block_mined_every': self.options['create_block_every'],
            'txs_pending': txs,
            'blocks': blocks
        }