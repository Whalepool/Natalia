# Natalia, a Telegram Administrative assistant bot by @whalepoolbtc - https://whalepool.io   

A simple telegram bot to help with the moderation of the telegram channels utilizing [python-telegram-bot](https://github.com/python-telegram-bot/python-telegram-bot)

### Features  
- Start / Welcome console with a selection of prebuild simple messages/pages  
- Message logging to mongo db   
- Fetch/Display top stickers from rooms  
- Fetch/Display top gifs posted from rooms  
- Name and Shame the top gif posts in rooms  
- Generate a wordcloud from the last days worth of chat in rooms  
- Generate a wordcloud from the last days top contributing users  
- Promotots - a global room messaging function for messaging all your rooms/broadcast channels with a specific message/sticker etc  
- Shill - A global room messaging shilling command   
- Command Stats - See stats on the lasts months worth of command requests from the bot  
- Join Stats - See stats on the last months worth of joins to your rooms  
- Welcome new users to your rooms with a message or select from a pool of welcome messages to keep it varief & fun  
- Automatically restrict new users in certain rooms to read only/no gif privledges for x amount of time etc  
- Forward private messages sent to the bot to the bot owner to see where users are going wrong in interacting with the bot  
- Live feed outputting int the console of the messages the bot is seeing come through  
- Identify photo messages with specific hash tags to forward them to your broadcast rooms  
- Automatically delete uncompressed images posted into rooms and request a compressed image be used instead  
- Scan links that users post for affiliate links, remove their post, replace with a message with your own appropriate affiliate link, ban the user  
- Forward urls posted to rooms from specific websites matching regex to your feed channels  
  

### Requirements
1) Mongodb  
2) Install pip requirements `sudo pip3.6 install -r requirements.pip`    

### Setup config
`cp config.sample.yaml config.yaml`  
Edit the config.yaml file accordingly  
You will have to edit/set some of the rooms under `natalia.py` for your room id's and feed room ids etc  

### Run
To run:  
`python3.6 natalia.py`

For more info join [@whalepoolbtc](https://t.me/whalepoolbtc) on telegram   

![Profile pic](http://i.imgur.com/iIUSRDG.jpg)