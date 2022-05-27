__author__          = 'agsvn'

import sys
import threading

from flask import Flask, jsonify, request, render_template
from time import time, sleep
from uuid import uuid4

from lib.util import *

from blockchain.chain import *
from blockchain.transaction import *

from account.wallet import *
from account.inventory import item

blockchain = chain()
blockchain.options['name'] = 'mainnet'
blockchain.options['create_block_every'] = 10 # s
blockchain.options['binary'] = True

app = Flask(__name__, template_folder='./frontend')

@app.route('/')
def route_app():

    blocks = []
    for block in blockchain.blocks:
        blocks.append(block.dictify())

    blocks.sort(key=lambda k : k['index'], reverse=True)

    txs = []
    holders = []
    for nblock in blockchain.blocks:
        for tx in nblock.transactions:
            if tx.sender not in holders and tx.sender != 'genesis':
                holders.append(tx.sender)
            if tx.recipient not in holders and tx.recipient != 'genesis':
                holders.append(tx.recipient)
            txs.append(tx.dictify())

    blockchain_stats = {
        'blocks': len(blockchain.blocks),
        'transactions': len(txs),
        'holders': len(holders)
    }

    return render_template('index.html', transactions=txs[::-1][:5], blocks=blocks[:5], stats=blockchain_stats, format_number=util.format_number, pretty_date=util.pretty_date, len=len)

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
    txs = []
    for tx in blockchain.current_transactions:
        txs.append(tx.dictify())

    return {
        'message': f'Will be included in the next block',
        'blockId': blockchain.nextBlockId(),
        'transactions': txs
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
        print('\ntest transactions :: mined genesis block and sent 1.000.000 gold (genesis >> wallet1)')
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

    tx.sign(publicKey=wallet1.publicKey, signature=wallet1.sign(tx))
    response = blockchain.add(type='transaction', data=tx)

    if response['success']:
        print('\ntest transactions :: sent 550.000 gold (wallet1 >> wallet2)')
        print('Wallet 1', wallet1.assets())
        print('Wallet 2', wallet2.assets())

    # send 200.000 gold from wallet1 to wallet2
    tx = transaction(sender=wallet1.address, recipient=wallet2.address, data={
        'type': 'transfer',
        'entity': 'gold',
        'amount': 200000,
    })

    tx.sign(publicKey=wallet1.publicKey, signature=wallet1.sign(tx))
    response = blockchain.add(type='transaction', data=tx)
    
    if response['success']:
        print('\ntest transactions :: sent 200.000 gold (wallet1 >> wallet2)')
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

    tx.sign(publicKey=wallet2.publicKey, signature=wallet2.sign(tx))
    response = blockchain.add(type='transaction', data=tx)

    if response['success']:
        print('\ntest transactions :: sent 153.293 gold (wallet2 >> wallet1)')
        print('Wallet 1', wallet1.assets())
        print('Wallet 2', wallet2.assets())

    # send 200.000 gold from wallet2 to wallet1
    tx = transaction(sender=wallet2.address, recipient=wallet1.address, data={
        'type': 'transfer',
        'entity': 'gold',
        'amount': 200000
    })

    tx.sign(publicKey=wallet2.publicKey, signature=wallet2.sign(tx))
    response = blockchain.add(type='transaction', data=tx)

    if response['success']:
        print('\ntest transactions :: sent 200.000 gold (wallet2 >> wallet1)')
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
        print('\ntest transactions :: mined 1.000 cash (genesis >> wallet1)')
        print('Wallet 1', wallet1.assets())
        print('Wallet 2', wallet2.assets())

    # send 200 cash from wallet1 to wallet2
    tx = transaction(sender=wallet1.address, recipient=wallet2.address, data={
        'type': 'transfer',
        'entity': 'cash',
        'amount': 200,
    })

    tx.sign(publicKey=wallet1.publicKey, signature=wallet1.sign(tx))
    response = blockchain.add(type='transaction', data=tx)

    if response['success']:
        print('\ntest transactions :: sent 200 cash (wallet1 >> wallet2)')
        print('Wallet 1', wallet1.assets())
        print('Wallet 2', wallet2.assets())

    # generate item and send it to wallet1
    itemUuid = str(uuid4())
    itemId = 614
    itemName = 'Conqueror Dual Sword'

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
        print('\ntest transactions :: mined item (genesis >> wallet1)')
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

    tx.sign(publicKey=wallet1.publicKey, signature=wallet1.sign(tx))
    response = blockchain.add(type='transaction', data=tx)

    if response['success']:
        print('\ntest transactions :: sent item (wallet1 >> wallet2)')
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