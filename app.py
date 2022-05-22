__author__          = 'agsvn'

import sys
import threading

from flask import Flask, jsonify, request
from time import sleep

from chain import *
from wallet import *
from transaction import *

blockchain = chain()
blockchain.options['name'] = 'mainnet'
blockchain.options['create_block_every'] = 10 # s

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

@app.route('/wallet/balance/<address>', methods=['GET'])
def route_wallet_balance(address):
    return jsonify({ 'type': 'gold', 'balance': wallet.balance(chain=blockchain, address=address) })

def test_transactions():
    # initialize wallets from private keys
    wallet1 = wallet(privateKey='85175d1ce944c01e44afcdbaf49c840cabc72974c741aecfbfa249a41f67b185')
    wallet2 = wallet(privateKey='9893ea79001d4e24de2616b4e8f5e6d90941123b0147b8c6bda6b2fc70bce9ba')

    # mine genesis block and send 1.000.000 gold to wallet1
    tx = transaction(sender='itself', recipient=wallet1.address, data={
        'type': 'standard',
        'entity': 'gold',
        'amount': 1000000,
    })
    
    response = blockchain.add(type='transaction', data=tx)
    print(response)

    # create test transactions after genesis block is mined and coinbase is created
    sleep(blockchain.options['create_block_every'] + 1)
    
    # send 550.000 gold from wallet1 to wallet2
    tx = transaction(sender=wallet1.address, recipient=wallet2.address, data={
        'type': 'standard',
        'entity': 'gold',
        'amount': 550000,
    })

    tx.publicKey = wallet1.publicKey
    tx.signature = wallet1.sign(tx.message())

    response = blockchain.add(type='transaction', data=tx)
    print(response)

    # send 200.000 gold from wallet1 to wallet2
    tx = transaction(sender=wallet1.address, recipient=wallet2.address, data={
        'type': 'standard',
        'entity': 'gold',
        'amount': 200000,
    })

    tx.publicKey = wallet1.publicKey
    tx.signature = wallet1.sign(tx.message())
    
    response = blockchain.add(type='transaction', data=tx)
    print(response)

    # create some more test transactions after wallet_test2 receives the first transaction
    sleep(blockchain.options['create_block_every'] + 1)

    # send 153.293 gold from wallet2 to wallet1
    tx = transaction(sender=wallet2.address, recipient=wallet1.address, data={
        'type': 'standard',
        'entity': 'gold',
        'amount': 153293,
    })

    tx.publicKey = wallet2.publicKey
    tx.signature = wallet2.sign(tx.message())

    response = blockchain.add(type='transaction', data=tx)
    print(response)

    # send 200.000 gold from wallet2 to wallet1
    tx = transaction(sender=wallet2.address, recipient=wallet1.address, data={
        'type': 'standard',
        'entity': 'gold',
        'amount': 200000
    })

    tx.publicKey = wallet2.publicKey
    tx.signature = wallet2.sign(tx.message())

    response = blockchain.add(type='transaction', data=tx)
    print(response)

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