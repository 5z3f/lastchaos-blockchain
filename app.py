__author__          = 'agsvn'

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
    data = None

    try:
        index = int(index)
    except ValueError:
        return { "error": "invalid block index" }

    for block in blockchain.blocks:
        if block['index'] == index:
            data = block

    return data if data else { 'error': 'not found' }

@app.route('/tx/<hash>')
def route_tx(hash):
    data = None
    for block in blockchain.blocks:
        for tx in block['transactions']:
            if tx['hash'] == hash:
                tx['block'] = {
                    'index': block['index'],
                    'hash': block['hash']
                }
                data = tx

    return data if data else { 'error': 'not found' }

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
    tx = transaction(sender=data['sender'], recipient=data['recipient'], data=data['data'])
    result = blockchain.add(type='transaction', data=tx)
    return result

@app.route('/wallet/generate', methods=['GET'])
def route_wallet_generate():
    return wallet.generate()

@app.route('/wallet/balance/<address>', methods=['GET'])
def route_wallet_balance(address):
    return jsonify({ 'type': 'gold', 'balance': wallet.balance(chain=blockchain, address=address) })

def test_transactions():
    wallet_test1 = wallet.load('test1')['address']['compressed']
    wallet_test2 = wallet.load('test2')['address']['compressed']

    # mine genesis block
    tx = transaction(sender=None, recipient=wallet_test1, data={
        'type': 'standard',
        'entity': 'gold',
        'amount': 1000000,
        'data': None
    })
    
    response = blockchain.add(type='transaction', data=tx)
    print(response)

    # create test transactions after first block is mined and coinbase is created
    sleep(blockchain.options['create_block_every'] + 1)
    
    tx = transaction(sender=wallet_test1, recipient=wallet_test2, data={
        'type': 'standard',
        'entity': 'gold',
        'amount': 550000,
        'data': None
    })
    
    response = blockchain.add(type='transaction', data=tx)
    print(response)

    tx = transaction(sender=wallet_test1, recipient=wallet_test2, data={
        'type': 'standard',
        'entity': 'gold',
        'amount': 200000,
        'data': None
    })

    response = blockchain.add(type='transaction', data=tx)
    print(response)

    # create some more test transactions after wallet_test2 receives the first transaction
    sleep(blockchain.options['create_block_every'] + 1)

    tx = transaction(sender=wallet_test2, recipient=wallet_test1, data={
        'type': 'standard',
        'entity': 'gold',
        'amount': 153293,
        'data': None
    })

    response = blockchain.add(type='transaction', data=tx)
    print(response)

    tx = transaction(sender=wallet_test2, recipient=wallet_test1, data={
        'type': 'standard',
        'entity': 'gold',
        'amount': 200000,
        'data': None
    })

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

    app.config['JSON_SORT_KEYS'] = False
    app.run(host='127.0.0.1', port=4444)

main()