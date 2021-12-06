# Betting Game

Betting game is a blockchain project developed in Python3. Users will be able to register and bet JTN, the official token of the game. 

JTN is an ERC-20 token developed in Solidity.

Users will be able to bet 5 JTN, and when there are 4 bets from 4 different users a draw will take place transferring the money bet to the winner.

## Design

Two Python frameworks have been used for the implementation of the game:
- Brownie: For the development, testing and deployment of the JTN Token smart contract.
- Django: For the backend and interaction with JTN Token.

JTN Token smart contract will be deployed in a network created by Ganache. For this, Docker will be used to deploy the network along with the application.

For the deployment, Docker has been chosen.

Some of the most important folders and files are the following:
```bash
betting-game
├── game_app                  # Django project               
│   ├── game_app              # Betting game init project folder
│   ├── main                  # Main app
│   ├── accounts.json         # Addresses and keys from ganache network
│   ├── docker-compose.yml    # To deploy game app + ganache network
│   ├── Dockerfile            # Dockerfile of game app
│   ├── JtnToken.json         # Compiled Smart Contract info
│   ├── manage.py             # Script which manage Django application
│   └── requirements.txt      # Requirements
└── jtn_token                 # Brownie project
    ├── build                 # Compiled and deployed data
    ├── contracts             # Source code of JTN Token
    ├── scripts               # Deploy and useful scripts
    ├── tests                 # Test scripts
    └── brownie-config.yaml   # Brownie config
```

### JTN Token:
Brownie allows the compilation, deployment and testing of smart contracts.
The source code of the smart contract is at:
```bash
betting-game   
└── jtn_token                
    └── contracts
        └── JtnToken.sol
```

### Back-end
The application is developed with Django.

The operation is as follows. Once the smart contract is deployed on the Ganache network, a superuser must be created with the same address that owns the contract. 
From this point on, every time a new user registers, 100 JTN will be transferred to him/her to be able to play. When 4 users wager, the holds will be executed and the winner will be drawn, to whom the prize will be transferred equally to the amount wagered. Although the execution of the holds is done by the users who created it, the web provider will be able to do it since it has in the accounts.json file the addresses and private keys.

The application will store the number of bets per player to assign a different holdid to each bet and the number of holds that currently exist, in order to carry out the draw once 4 players have participated.
## Usage

### Play!

A demo of the application can be used at: 

[jatornahost.ddns.net:3500](jatornahost.ddns.net:3500)

Just register and bet! Once 4 different users have placed their bets the winner will be drawn!

### Deploy!

Requirements:
- Docker
- Brownie
- Django

First, deploy the application and Ganache-CLI network:
```bash
cd betting-game/game_app
docker-compose up -d
```

Second, the web database is created and the user, who will be the owner of the smart contract, is created.
```bash
python manage.py migrate
python manage.py create-superuser --email [email@email.com] --username [user] --password [pass] --address 0x90F8bf6A479f320ead074411a4B0e7944Ea8c9C1
```
NOTE: The superuser address is the first one provided by Ganache.

Then, add the ganache network to Brownie:
 ```bash
brownie networks add Ethereum ganache-docker host=http://localhost:7545 chainid=1337
```

Finally, deploy the JTN Token smart contract:

```bash
cd betting-game/jtn_token
brownie run scripts/deploy.py --network ganache-docker
```

Ready!

### Test
Brownie allows easy testing of smart contracts. In the script, test.py, the following functions are checked:

- compile()
- transfer()
- transferFrom():
- hold():
- holdFrom():
- executeHold():
- removeHold()

```bash
cd betting-game/jtn_token 
brownie test scripts/test_jtn_token.py
```

## Improvements

- Currently, the game would not be decentralized, since it is the owner who transfers the winner of the draw, and the users who execute the holds, although the transactions and holds of the token. A possible improvement would be to make another smart contract with the conditions of the game and it would be done automatically when X holds are performed.
- The accounts are provided by the web provider. It would be interesting to be able to register with a wallet such as Metamask. 
- A notification system once the draw is made. Only a message for the fourth player who bets is displayed.




