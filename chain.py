__author__          = 'agsvn'

import os
import json

from time import sleep

from block import *
from wallet import *

class chain:
    def __init__(self):
        self.blocks = []
        self.current_transactions = []
        self.blocks_directory = os.getcwd() + '\\blocks'
        
        self.options = {
            'name': 'mainnet',
            'create_block_every': 10,
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
        files = [f for f in os.listdir(self.blocks_directory) if f.endswith('.json')]
        for f in files:
            with open(f'{ self.blocks_directory }/{ f }', 'r') as f:
                data = json.load(f)
                self.blocks.append(data)
                
    def add(self, type, data=None):
        match type:
            case 'block':
                # previous block
                previous_block_hash = block(**self.blocks[-1]).hash if len(self.blocks) > 0 else 0

                # create block
                newBlock = block(index=len(self.blocks), prevhash=previous_block_hash, transactions=self.current_transactions)

                # compute hash for block
                newBlock.generate_hash()

                # append block to chain
                self.blocks.append(newBlock.dictify())

                # save block to file
                with open(f'./blocks/{ newBlock.index }.json', 'w') as f:
                    json.dump(newBlock.dictify(), f, indent=4)

                # empty current transactions
                self.current_transactions = []

                # return new block
                return newBlock

            case 'transaction':
                tx = data

                if tx.data['entity'] == 'gold' and wallet.balance(self, tx.sender) < tx.data['amount'] and tx.sender != None:
                    return { 'success': False, 'message': 'sender has insufficient funds' }
                
                self.current_transactions.append(data.dictify())
                return { 'success': True, 'message': 'transaction added', 'tx': data.dictify() }
    
    def validate(self):
        for i in range(1, len(self.blocks)):
            previous_block = block(**self.blocks[i - 1])
            current_block = block(**self.blocks[i])

            (_, current_block_generated_hash) = current_block.generate_hash()
            if (current_block.prevhash != previous_block.hash) or (current_block.hash != current_block_generated_hash):
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