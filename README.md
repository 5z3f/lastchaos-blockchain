# Last Chaos Blockchain
#### very simple prototype to make all game transactions transparent
#### features
- block is created every 10s by default (there must be at least 1 pending transaction)
- proof of work
- chain validation
- binary/plain (json) block mode
- wallet
  - generate
  - sign/verify transaction
  - check for currency balance (gold, cash) and inventory items

# Routes
### `GET /chain`
get whole chain

##### response
```jsonc
{
  "name": "mainnet",
  "valid": true,
  "block_mined_every": 10,
  "txs_pending": [
    // ...   
  ],
  "blocks": [
    // ...
  ]
}
```

### `GET /block/<index>`
get block details by index

##### response
```json
{
    "index": 1,
    "prevhash": "4c43b2177fe9ca2094a36e58cc3f42a2d7cdd2fadb2d634e69fc35f5c92b6cc0",
    "hash": "4c43536e090e527d986f4cf2cc4c0a09557860644a33273e0b2f1b2f00e59813",
    "proof": 24913,
    "transactions": [
        {
            "txid": "972decd5fcde135fda31cd6b451d6bfc5de56d8f7035a8820ec4688c6111797a",
            "sender": "lc1NL4s5cguoPXS8PLNSnMDvLPR1sBpWBbdr",
            "recipient": "lc1NbwD67HEaRcbrJHczmY5XeR1QGpLy6b9",
            "data": {
                "type": "transfer",
                "entity": "gold",
                "amount": 550000
            },
            "publicKey": "1ee1808321d18b73b3979ab3cc1604b5471606bfa297c48eb5a7f5e70a79dbff5a114dbaccf7616fb4b1aa724ac5ba1613b249af0a31e8240e1736b14cc5628d",
            "signature": "c0ffecaf44be8d6ec274a673d8409044c2560bd7bd7fd057cea0fc7d5f63bcdbf38a0d682760c170a5e7d13674e966b3c0e8bc6cd07f01aba1f340592494a5e8",
            "timestamp": 1653273032802
        },
        {
            "txid": "d345aa89a93f62de6830dbf98924be25cd629e1122474a21497054565e24fa54",
            "sender": "lc1NL4s5cguoPXS8PLNSnMDvLPR1sBpWBbdr",
            "recipient": "lc1NbwD67HEaRcbrJHczmY5XeR1QGpLy6b9",
            "data": {
                "type": "transfer",
                "entity": "gold",
                "amount": 200000
            },
            "publicKey": "1ee1808321d18b73b3979ab3cc1604b5471606bfa297c48eb5a7f5e70a79dbff5a114dbaccf7616fb4b1aa724ac5ba1613b249af0a31e8240e1736b14cc5628d",
            "signature": "2474ab1830b3b6b60863364d27590021f267f340275900bcbc040fb6d2d6d5ac3013d718018287c2ec94199fd6af6931dc0772cd146f4482d86a39b1eb975baa",
            "timestamp": 1653273032802
        }
    ],
    "timestamp": 1653273032925
}
```

### `GET /tx/<txid>`
get transaction details by transaction id

##### payload
```json
{
    "txid": "972decd5fcde135fda31cd6b451d6bfc5de56d8f7035a8820ec4688c6111797a",
    "sender": "lc1NL4s5cguoPXS8PLNSnMDvLPR1sBpWBbdr",
    "recipient": "lc1NbwD67HEaRcbrJHczmY5XeR1QGpLy6b9",
    "data": {
        "type": "transfer",
        "entity": "gold",
        "amount": 550000
    },
    "publicKey": "1ee1808321d18b73b3979ab3cc1604b5471606bfa297c48eb5a7f5e70a79dbff5a114dbaccf7616fb4b1aa724ac5ba1613b249af0a31e8240e1736b14cc5628d",
    "signature": "c0ffecaf44be8d6ec274a673d8409044c2560bd7bd7fd057cea0fc7d5f63bcdbf38a0d682760c170a5e7d13674e966b3c0e8bc6cd07f01aba1f340592494a5e8",
    "timestamp": 1653273032802
}
```

### `GET /tx/pending`
get transactions that will be included in next block

##### response
```json
{
	"message": "Will be included in the next block",
	"blockId": 3,
	"transactions": []
}
```

### `POST /tx/add`
add transaction to pending transactions

##### payload
```jsonc
{
  "sender": {
    "address": "lc1NL4s5cguoPXS8PLNSnMDvLPR1sBpWBbdr",
    "publicKey": "1ee1808321d18b73b3979ab3cc1604b5471606bfa297c48eb5a7f5e70a79dbff5a114dbaccf7616fb4b1aa724ac5ba1613b249af0a31e8240e1736b14cc5628d", 
    // sign(privateKey, message=sha256("senderAddress:receiverAddress:json(data)"))
    "signature": "c0ffecaf44be8d6ec274a673d8409044c2560bd7bd7fd057cea0fc7d5f63bcdbf38a0d682760c170a5e7d13674e966b3c0e8bc6cd07f01aba1f340592494a5e8"
	},
  "recipient": "lc1NbwD67HEaRcbrJHczmY5XeR1QGpLy6b9", // receiver wallet address
  "data": {
      "type": "transfer", // not used yet
      "entity": "gold",   // gold / cash / item
      "amount": 550000
  }
}
```

##### response 
```json
{
	"success": true,
	"message": "transaction added",
	"tx": {
    "txid": "972decd5fcde135fda31cd6b451d6bfc5de56d8f7035a8820ec4688c6111797a",
    "sender": "lc1NL4s5cguoPXS8PLNSnMDvLPR1sBpWBbdr",
    "recipient": "lc1NbwD67HEaRcbrJHczmY5XeR1QGpLy6b9",
    "data": {
        "type": "transfer",
        "entity": "gold",
        "amount": 550000
    },
    "publicKey": "1ee1808321d18b73b3979ab3cc1604b5471606bfa297c48eb5a7f5e70a79dbff5a114dbaccf7616fb4b1aa724ac5ba1613b249af0a31e8240e1736b14cc5628d",
    "signature": "c0ffecaf44be8d6ec274a673d8409044c2560bd7bd7fd057cea0fc7d5f63bcdbf38a0d682760c170a5e7d13674e966b3c0e8bc6cd07f01aba1f340592494a5e8",
    "timestamp": 1653273032802
  }
}
```

### `GET /wallet/generate`
generate new wallet

##### response
```json
{
	"private_key": "85175d1ce944c01e44afcdbaf49c840cabc72974c741aecfbfa249a41f67b185",
	"public_key": "1ee1808321d18b73b3979ab3cc1604b5471606bfa297c48eb5a7f5e70a79dbff5a114dbaccf7616fb4b1aa724ac5ba1613b249af0a31e8240e1736b14cc5628d",
	"address": "lc1NL4s5cguoPXS8PLNSnMDvLPR1sBpWBbdr"
}
```

### `GET /wallet/<address>`
get all transactions for given address

##### response
```jsonc
[
  {
    "txid": "8f09d193ce25854de7bcd92100b153a799552f73b4ed725401491f7c273fc72d",
    "sender": "genesis",
    "recipient": "lc1NL4s5cguoPXS8PLNSnMDvLPR1sBpWBbdr",
    "data": {
      "type": "transfer",
      "entity": "gold",
      "amount": 1000000
    },
    "publicKey": "",
    "signature": "",
    "timestamp": 1653272976844
  },
  // ...
]
```

### `GET /wallet/<address>/balance`
get address balance

##### response
```json
{
  "gold": 603293,
  "cash": 800
}
```

### `GET /wallet/<address>/inventory`
get all items in the inventory for given address

##### response
```jsonc
[
  {
    "id": 614,
    "uid": "a582d7a7-b47b-47f7-804e-ecab4ee29526",
    "source": {
      "type": "player",
      "id": 1,
      "localization": 0,
      "timestamp": 1653272980888
    }
  }
  // ...
]
```