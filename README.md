# Last Chaos Blockchain
#### very simple prototype to make all game transactions transparent
#### features
- block is created every 10s by default (there must be at least 1 pending transaction)
- proof of work
- chain validation
- wallet (generate, check balance, sign/verify transaction)

# Routes
### `GET /chain`
get whole chain

### `GET /block/<index>`
get block details by index

##### response
```json
{
  "index": 1,
  "prevhash": "4c430c39887302bf31436e8dc4d5a82cdcd2c6fef4677353ae6644919797d029",
  "hash": "4c43f10884219c68e11b1d0362c504419bbc20e137df0e4f20e874338f8f7217",
  "proof": 120456,
  "transactions": [
    {
      "txid": "14d13056bf028b35003274e0a1d77fc33eef584bee50942cf6069b50e47a595c",
      "sender": "lc1NL4s5cguoPXS8PLNSnMDvLPR1sBpWBbdr",
      "recipient": "lc1NbwD67HEaRcbrJHczmY5XeR1QGpLy6b9",
      "data": {
        "type": "standard",
        "entity": "gold",
        "amount": 550000
      },
      "publicKey": "1ee1808321d18b73b3979ab3cc1604b5471606bfa297c48eb5a7f5e70a79dbff5a114dbaccf7616fb4b1aa724ac5ba1613b249af0a31e8240e1736b14cc5628d",
      "signature": "42de532cd2b6d7395bb9d2c4a76b6e3c6c0d338aeafeb3d62dc79e3ffcc80f355748f84af0bb48ecd95a1a364672e998f15e6d07da835fed2469dbb9f4073aa0",
      "timestamp": 1653204598.9890165
    },
    {
      "txid": "870bc2ac15dbaa5df2a80028ca10b5be95ce0c43d66b52ce8164a6035b19f28d",
      "sender": "lc1NL4s5cguoPXS8PLNSnMDvLPR1sBpWBbdr",
      "recipient": "lc1NbwD67HEaRcbrJHczmY5XeR1QGpLy6b9",
      "data": {
        "type": "standard",
        "entity": "gold",
        "amount": 200000
      },
      "publicKey": "1ee1808321d18b73b3979ab3cc1604b5471606bfa297c48eb5a7f5e70a79dbff5a114dbaccf7616fb4b1aa724ac5ba1613b249af0a31e8240e1736b14cc5628d",
      "signature": "e82b7773402301b975e6075b10778f3fc6c7bcfcd6e8dc16a385ba82706d953ba9787998513cc1095e912f231240a99fc9a5b3ad93e2837bfb88b680853bf347",
      "timestamp": 1653204598.992289
    }
  ],
  "timestamp": 1653204606.3088036
}
```

### `GET /tx/<txid>`
get transaction details by transaction id

##### payload
```json
{
  "txid": "14d13056bf028b35003274e0a1d77fc33eef584bee50942cf6069b50e47a595c",
  "sender": "lc1NL4s5cguoPXS8PLNSnMDvLPR1sBpWBbdr",
  "recipient": "lc1NbwD67HEaRcbrJHczmY5XeR1QGpLy6b9",
  "data": {
    "type": "standard",
    "entity": "gold",
    "amount": 550000
  },
  "publicKey": "1ee1808321d18b73b3979ab3cc1604b5471606bfa297c48eb5a7f5e70a79dbff5a114dbaccf7616fb4b1aa724ac5ba1613b249af0a31e8240e1736b14cc5628d",
  "signature": "42de532cd2b6d7395bb9d2c4a76b6e3c6c0d338aeafeb3d62dc79e3ffcc80f355748f84af0bb48ecd95a1a364672e998f15e6d07da835fed2469dbb9f4073aa0",
  "timestamp": 1653204598.9890165
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
		"signature": "42de532cd2b6d7395bb9d2c4a76b6e3c6c0d338aeafeb3d62dc79e3ffcc80f355748f84af0bb48ecd95a1a364672e998f15e6d07da835fed2469dbb9f4073aa0"
	},
    "recipient": "lc1NbwD67HEaRcbrJHczmY5XeR1QGpLy6b9",  // receiver wallet address
    "data": {
        "type": "standard",								// not used yet
        "entity": "gold",								// gold / item
        "amount": 200000
    }
}
```

##### response 
```json
{
	"success": true,
	"message": "transaction added",
	"tx": {
		"hash": "5a794492081b9b0f71e09ae833faf224c10609a1995a81d91f675c307ddd3f07",
		"sender": "16BYanz2meY7Detwd2gs43j1ifhsGZwW3D",
		"recipient": "1Jv9gzvm5SAbvk1EtUXbk2UfsNWjzG8utN",
		"data": {
			"type": "standard",
			"entity": "gold",
			"amount": 55555,
			"data": null
		},
		"timestamp": 1653116062.4855871
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
### `GET /wallet/balance/<address>`
get address balance

##### response
```json
{
  "type": "gold",
  "balance": 603293
}
```