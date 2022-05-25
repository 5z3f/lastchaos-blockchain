__author__          = 'agsvn'

import sys
import threading

from flask import Flask, jsonify, request
from time import time, sleep
from uuid import uuid4

from blockchain.chain import *
from blockchain.transaction import *

from account.wallet import *
from account.inventory import item

blockchain = chain()
blockchain.options['name'] = 'mainnet'
blockchain.options['create_block_every'] = 10 # s
blockchain.options['binary'] = True

app = Flask(__name__)

@app.route('/')
def route_app():
    return jsonify({ "title": "LastChaos Blockchain!" })

@app.route('/chain', methods=['GET'])
def route_chain():
    return blockchain.dictify()

@app.route('/block/<index>')
def route_block(index):
    try:
        index = int(index)
    except ValueError:
        return { "error": "invalid block index" }

    block = blockchain.find(type='block', id=index)
    return block.dictify() if block else { 'error': 'not found' }

@app.route('/tx/<txid>')
def route_tx(txid):
    tx = blockchain.find(type='transaction', id=txid)
    return tx.dictify() if tx else { 'error': 'not found' }

@app.route('/tx/pending')
def route_unconfirmed_transactions():
    return {
        'message': f'Will be included in the next block',
        'blockId': blockchain.nextBlockId(),
        'transactions': blockchain.current_transactions
    }

@app.route('/tx/add', methods=['POST'])
def route_tx_add():
    data = request.get_json()
    
    tx = transaction(
        sender=data['sender']['address'],
        recipient=data['recipient'],
        data=data['data'],
        publicKey=data['sender']['publicKey'],
        signature=data['sender']['signature']
    )
    
    result = blockchain.add(type='transaction', data=tx)
    return result

@app.route('/wallet/generate', methods=['GET'])
def route_wallet_generate():
    return wallet.generate()

@app.route('/wallet/<address>', methods=['GET'])
def route_wallet(address):
    return jsonify(wallet.search(chain=blockchain, address=address))

@app.route('/wallet/<address>/balance', methods=['GET'])
def route_wallet_balance(address):
    return wallet.balance(chain=blockchain, address=address)

@app.route('/wallet/<address>/inventory', methods=['GET'])
def route_wallet_inventory(address):
    return jsonify(wallet.inventory(chain=blockchain, address=address))

@app.route('/wallet/<address>/assets', methods=['GET'])
def route_wallet_assets(address):
    return jsonify({ 'currency': wallet.balance(chain=blockchain, address=address), 'inventory': wallet.inventory(chain=blockchain, address=address) })

def test_transactions():
    sleep(2)
    print('blockchain :: testing transactions...')

    # initialize wallets from private keys
    wallet1 = wallet(privateKey='85175d1ce944c01e44afcdbaf49c840cabc72974c741aecfbfa249a41f67b185', chain=blockchain)
    wallet2 = wallet(privateKey='9893ea79001d4e24de2616b4e8f5e6d90941123b0147b8c6bda6b2fc70bce9ba', chain=blockchain)

    # mine genesis block and send 1.000.000 gold to wallet1
    tx = transaction(sender='genesis', recipient=wallet1.address, data={
        'type': 'transfer',
        'entity': 'gold',
        'amount': 1000000,
    })
    
    response = blockchain.add(type='transaction', data=tx)

    if response['success']:
        print('\ntest transactions :: mined genesis block and sent 1.000.000 gold to wallet1')
        print('Wallet 1', wallet1.assets())
        print('Wallet 2', wallet2.assets())

    # create test transactions after genesis block is mined and coinbase is created
    sleep(blockchain.options['create_block_every'] + 1)
    
    # send 550.000 gold from wallet1 to wallet2
    tx = transaction(sender=wallet1.address, recipient=wallet2.address, data={
        'type': 'transfer',
        'entity': 'gold',
        'amount': 550000,
    })

    tx.publicKey = wallet1.publicKey
    tx.signature = wallet1.sign(tx.message())
    
    response = blockchain.add(type='transaction', data=tx)

    if response['success']:
        print('\ntest transactions :: sent 550.000 gold from wallet1 to wallet2')
        print('Wallet 1', wallet1.assets())
        print('Wallet 2', wallet2.assets())

    # send 200.000 gold from wallet1 to wallet2
    tx = transaction(sender=wallet1.address, recipient=wallet2.address, data={
        'type': 'transfer',
        'entity': 'gold',
        'amount': 200000,
    })

    tx.publicKey = wallet1.publicKey
    tx.signature = wallet1.sign(tx.message())
    
    response = blockchain.add(type='transaction', data=tx)
    
    if response['success']:
        print('\ntest transactions :: sent 200.000 gold from wallet1 to wallet2')
        print('Wallet 1', wallet1.assets())
        print('Wallet 2', wallet2.assets())

    # create some more test transactions after wallet_test2 receives the first transaction
    sleep(blockchain.options['create_block_every'] + 1)

    # send 153.293 gold from wallet2 to wallet1
    tx = transaction(sender=wallet2.address, recipient=wallet1.address, data={
        'type': 'transfer',
        'entity': 'gold',
        'amount': 153293,
    })

    tx.publicKey = wallet2.publicKey
    tx.signature = wallet2.sign(tx.message())

    response = blockchain.add(type='transaction', data=tx)

    if response['success']:
        print('\ntest transactions :: sent 153.293 gold from wallet2 to wallet1')
        print('Wallet 1', wallet1.assets())
        print('Wallet 2', wallet2.assets())

    # send 200.000 gold from wallet2 to wallet1
    tx = transaction(sender=wallet2.address, recipient=wallet1.address, data={
        'type': 'transfer',
        'entity': 'gold',
        'amount': 200000
    })

    tx.publicKey = wallet2.publicKey
    tx.signature = wallet2.sign(tx.message())

    response = blockchain.add(type='transaction', data=tx)

    if response['success']:
        print('\ntest transactions :: sent 200.000 gold from wallet2 to wallet1')
        print('Wallet 1', wallet1.assets())
        print('Wallet 2', wallet2.assets())

    # generate 1.000 cash and send it to wallet1
    tx = transaction(sender='genesis', recipient=wallet1.address, data={
        'type': 'transfer',
        'entity': 'cash',
        'amount': 1000,
    })
    
    response = blockchain.add(type='transaction', data=tx)

    if response['success']:
        print('\ntest transactions :: mined 1.000 cash and sent it to wallet1')
        print('Wallet 1', wallet1.assets())
        print('Wallet 2', wallet2.assets())

    # send 200 cash from wallet1 to wallet2
    tx = transaction(sender=wallet1.address, recipient=wallet2.address, data={
        'type': 'transfer',
        'entity': 'cash',
        'amount': 200,
    })

    tx.publicKey = wallet1.publicKey
    tx.signature = wallet1.sign(tx.message())

    response = blockchain.add(type='transaction', data=tx)

    if response['success']:
        print('\ntest transactions :: sent 200 cash from wallet1 to wallet2')
        print('Wallet 1', wallet1.assets())
        print('Wallet 2', wallet2.assets())

    itemUuid = str(uuid4())
    itemId = 614
    itemName = 'Conqueror Dual Sword'

    # generate item and send it to wallet1
    itemObj = item(id=itemId, uuid=itemUuid, source={
        'type': 'monster',
        'id': 64, # Ghoul
        'localization': {
            'zone': 9, # Procyon
            'x': 144,
            'y': 291,
        },
        'timestamp': int(time() * 1000.0)
    })

    tx = transaction(sender='genesis', recipient=wallet1.address, data={
        'type': 'transfer',
        'entity': 'item',
        'amount': 1,
        'data': itemObj.dictify()
    })

    response = blockchain.add(type='transaction', data=tx)

    if response['success']:
        print('\ntest transactions :: mined item and sent it to wallet1')
        print('Wallet 1', wallet1.assets())
        print('Wallet 2', wallet2.assets())

    # send the same item to wallet2
    itemObj = item(id=itemId, uuid=itemUuid, source={
        'type': 'player',
        'id': 1,
        'localization': {
            'zone': 0, # Juno
            'x': 644,
            'y': 201,
        },
        'timestamp': int(time() * 1000.0)
    })

    tx = transaction(sender=wallet1.address, recipient=wallet2.address, data={
        'type': 'transfer',
        'entity': 'item',
        'amount': 1,
        'data': itemObj.dictify()
    })

    tx.publicKey = wallet1.publicKey
    tx.signature = wallet1.sign(tx.message())

    response = blockchain.add(type='transaction', data=tx)

    if response['success']:
        print('\ntest transactions :: sent item from wallet1 to wallet2')
        print('Wallet 1', wallet1.assets())
        print('Wallet 2', wallet2.assets())

def main():
    blockchain.load()

    # mine block every minute (if there are pending transactions)
    thread = threading.Thread(target=blockchain.mineBlock, daemon=True)
    thread.start()
    
    # create genesis block and test transactions
    # thread = threading.Thread(target=test_transactions, daemon=True)
    # thread.start()

    print('blockchain :: starting server...')

    cli = sys.modules['flask.cli']
    cli.show_server_banner = lambda *x: None
    
    app.config['JSON_SORT_KEYS'] = False
    app.run(host='127.0.0.1', port=4444)

main()