# On-Chain-Battle-City


## Public Links:

- Smart contract: https://mumbai.polygonscan.com/address/0xa0e5b78f3b43c0dbfeb1da0b75b84dc07f8388c5


## Logic:

In order to start playing, you need to connect your metamask wallet to the website and then click "Play". Then it will be necessary to verify the transaction and after the transaction is written to the blockchain the game client will start. ***For spawn you need to pay 0.05 MATIC***

![1](https://user-images.githubusercontent.com/100310858/235586777-13938927-25b3-4eb6-b26b-4c6bbfb30a95.jpg)

Next, in the client of the game you need to click "Ready", after which there will be two options for the outcome: 

![2](https://user-images.githubusercontent.com/100310858/235587845-1e3e52e8-bd83-44e6-97ec-2b5c64f7fb57.jpg)

1. If there are no more players, you will have to wait for the second player and only then the map will be loaded and you will start playing
2. If someone is already waiting for his game, you just connect to his server and start playing the same way

![3](https://user-images.githubusercontent.com/100310858/235587969-2f3d00f2-e074-48db-85f2-64935c501b4d.jpg)
![4](https://user-images.githubusercontent.com/100310858/235588043-d901da57-a68f-40fa-aecd-cf34425c2bdb.jpg)

Once the game is started you need to destroy the enemy tank (***which also paid 0.05 MATIC for spawning***). To remember how to play or watch the gameplay itself you can watch this video:
https://youtu.be/Gbfht4ly-aM

![5](https://user-images.githubusercontent.com/100310858/235588653-52607d00-a998-4e3e-9ed2-40538f9ffb49.jpg)
![6](https://user-images.githubusercontent.com/100310858/235588660-2ec8e0a5-6ef5-4c8c-9456-32f5f5048aa2.jpg)

Each tank is tied to a player's purse, that is, after there is only one player - the server automatically exits the main game cycle, shows the winner's purse and sends a transaction in a smart contract with the address of the winner and loser. 

<img width="1414" alt="contract" src="https://user-images.githubusercontent.com/100310858/235589493-23de91e8-b690-4ee1-ada3-e578f26df8fd.png">

This way you can see several test transactions: 
- The first two transactions are deposits from the first and second player at 0.05 MATIC
- Test transaction "AddUser" which is responsible for adding winner and loser and "Claim". These two transactions failed because only the owner can send the transaction "AddUser" and "Claim" only the winner, as in the following two transactions
