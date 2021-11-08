# RedditDealBot
Telegram-powered bot that listens for posted deals and notifies users when certain keywords are met.

# Setup
In order to get this bot to work, you'll need the following things:
 - Telegram Bot ID
 - Default Telegram Chat ID
 - Reddit Account Username
 - Reddit Account Password
 - Reddit API Client ID
 - Reddit API Client Secret

## Telegram Bot ID
1. Open your Telegram app and start a new chat with @Botfather.
2. Send "/newbot"
3. Follow the steps until @Botfather tells you "Done!"
4. Copy the token provided in that message and paste it in `check_for_deals.py` as the value for `self.BOT_ID`
5. If at any time you forget this token and need it again, message @Botfather and send "/token"

## Default Telegram Chat ID
1. Start a group chat with your new bot.
2. Send a message to the group chat while your bot is present.
3. Navigate to https://api.telegram.org/bot<BOT_TOKEN_YOU_GOT_FROM_THE_ABOVE_STEPS>/getUpdates
  - i.e. https://api.telegram.org/bot351861874:AAefaae8dda8bcb7274219sU/getUpdates 
4. In the JSON response that comes back, you should see `"chat": { "id": "..."`
5. Copy that ID and paste it in `check_for_deals.py` as the value for `self.CHAT_ID`.

## Reddit Account Username
1. Go to reddit and either create a new account for your bot or use an existing one.
2. Set the username in `check_for_deals.py` as the value for `username` in the Reddit constructor (line 28).

## Reddit Account
1. Set the password for the chosen account in `check_for_deals.py` as the value for `password` in the Reddit constructor (line 26).

## Reddit API Client ID
1. Go to https://www.reddit.com/prefs/apps while logged in as the account chosen for your bot.
2. Click the button to create an app.
3. Fill out the fields. "Personal Use Script", I believe, best describes this bot.
4. Once done, copy the value underneath the name of the app and paste it in `check_for_deals.py` as the value for `client_id` in the Reddit constructor (line 24)

## Reddit API Client Secret
1. Copy the value next to "secret" for your app on https://www.reddit.com/prefs/apps and paste it in `check_for_deals.py` as the value for `client_secret` in the Reddit constructor (line 25).

# Running the Bot
Once  you've completed the setup, all you need to do is run the script. This script is setup to run on Python 3+ in a Linux environment.  For Windows, there is one minor adjustment that needs to be made:

- Remove the shebang on the first line (`#!/usr/bin/python3`).  It's not needed for Windows.
