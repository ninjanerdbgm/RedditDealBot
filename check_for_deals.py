#!/usr/bin/python3
import aiofiles
import asyncio
import math
import random
import telegram
import traceback

from datetime import datetime
from functools import wraps
from praw import Reddit
from pytz import timezone, utc
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, PicklePersistence, CallbackQueryHandler, CallbackContext
from threading import Thread
from time import sleep

class RedditDealsBot:

    def __init__(self):
        # See the README on how to fill out this section
        self.BOT_ID = ""
        self.CHAT_ID = ""
        self.reddit = Reddit(
                        client_id = "",
                        client_secret = "",
                        password = ",
                        user_agent = "DealsChecker Bot by /u/kn0wmad1c",
                        username = ""
                      )
        self.telegram = telegram.Bot(token=self.BOT_ID)
        self.persistence = PicklePersistence(filename="botdb")
        
        self.loop = asyncio.get_event_loop()
        self.game_list = list()
        self.match = None
        self.match_limit = 10 # in minutes
        self.userdata = {}
        self.rand_nums = [23, 42, 77, 90, 8] # Can be anything
        self.init = True

    def send_typing_action(func):
        # Creates
        @wraps(func)
        def command_func(self, update, context, *args, **kwargs):
            self.telegram.send_chat_action(chat_id=update.effective_message.chat_id, action=telegram.ChatAction.TYPING)
            return func(self, update, context, *args, **kwargs)

        return command_func

    @send_typing_action
    def AddItemToList(self, update, context):
        if len(" ".join(context.args[0:])) < 2: 
            update.message.reply_text("Add what?")
            return

        print(f"{update.message.from_user.first_name} {update.message.from_user.last_name} is trying to add {context.args[0]} to the list...".replace(" None", ""))

        cur_list = context.user_data.get("game_list", "not found")
        if cur_list == "not found": cur_list = self.game_list

        item_to_add = " ".join(context.args[0:])

        if "," in item_to_add:
            try:
                # Add to list
                cur_list.extend(item_to_add.replace(", ",",").replace(" ,", ",").split(","))

                # Update file
                #self.loop.run_until_complete(self.UpdateQueryList())

                print("Update complete.")
                message = "Added all to the list."

                update.message.reply_text(text=message, parse_mode=telegram.ParseMode.HTML)
                context.user_data["game_list"] = cur_list
                context.user_data["name"] = f"{update.message.from_user.first_name} {update.message.from_user.last_name}".replace(" None", "")

            except Exception as e:
                # Display error
                pass
        else:
            try:
                # Add to list
                cur_list.append(item_to_add.strip())

                # Update file
                #self.loop.run_until_complete(self.UpdateQueryList())

                print("Update complete")
                message = f"Added {item_to_add.strip()} to the list."

                update.message.reply_text(text=message, parse_mode=telegram.ParseMode.HTML)
                context.user_data["game_list"] = cur_list
                context.user_data["name"] = f"{update.message.from_user.first_name} {update.message.from_user.last_name}".replace(" None", "")
            except Exception as e:
                # Display error
                pass

    @send_typing_action
    def RemoveItemFromList(self, update, context):
        updater = None
        if update.message is not None:
            updater = update
        else: 
            updater = update.callback_query

        if len("".join(context.args[0:])) < 2: 
            updater.message.reply_text("Remove what?")
            return

        print(f"{updater.message.from_user.first_name} {updater.message.from_user.last_name} is trying to remove {context.args[0]} from their list...".replace(" None", ""))

        cur_list = context.user_data.get("game_list", "not found")
        if cur_list == "not found": cur_list = self.game_list

        item_to_remove = " ".join(context.args[0:])

        if "," in item_to_remove:
            # Remove from list
            for item in item_to_remove.replace(", ", ",").replace(" ,", ",").split(","):
                try:
                    cur_list.remove(item)
                        
                    message = f"The following have been removed:\n-----\n"
                    rem_list = "\n".join(item_to_remove.replace(", ", ",").split(","))
                    message = f"{message}{rem_list}\n-----"

                    updater.message.reply_text(text=message, parse_mode=telegram.ParseMode.HTML)
                    print("Update complete.")
                    context.user_data["game_list"] = cur_list
                    context.user_data["name"] = f"{updater.message.from_user.first_name} {updater.message.from_user.last_name}".replace(" None", "")
                except:
                    possibles = [i for i in cur_list if item in i]
                    if len(possibles) > 0:
                        reply_keyboard = [[telegram.InlineKeyboardButton(text=f"{possible}", callback_data=f"rem {possible}")] for possible in possibles]
                        no_match = [telegram.InlineKeyboardButton(text="None of These", callback_data="cancel")]
                        reply_keyboard.append(no_match)
                        message = f"I couldn't find \"{item}\" in your list. Did you mean one of these?"
                        reply_markup = telegram.InlineKeyboardMarkup(reply_keyboard, one_time_keyboard=True, input_field_placeholder=message)

                        updater.message.reply_text(text=message, reply_markup=reply_markup)                            
                    else:
                        message = f"I couldn't find \"{item}\" in your list. Type /list to see your current list if you need help."
                        updater.message.reply_text(text=message, parse_mode=telegram.ParseMode.HTML)

                #self.loop.run_until_complete(self.UpdateQueryList())
        else:
            try:
                cur_list.remove(item_to_remove)

                print("Update complete.")
                message = f"Removed {item_to_remove} from the list."
    
                updater.message.reply_text(text=message, parse_mode=telegram.ParseMode.HTML)
                context.user_data["game_list"] = cur_list
                context.user_data["name"] = f"{updater.message.from_user.first_name} {updater.message.from_user.last_name}".replace(" None", "")
            except:
                possibles = [i for i in cur_list if item_to_remove in i]
                if len(possibles) > 0:
                    reply_keyboard = [[telegram.InlineKeyboardButton(text=f"{possible}", callback_data=f"rem {possible}")] for possible in possibles]
                    no_match = [telegram.InlineKeyboardButton(text="None of These", callback_data="cancel")]
                    reply_keyboard.append(no_match)
                    message = f"I couldn't find \"{item_to_remove}\" in your list. Did you mean one of these?"
                    reply_markup = telegram.InlineKeyboardMarkup(reply_keyboard, one_time_keyboard=True, input_field_placeholder=message)

                    updater.message.reply_text(text=message, reply_markup=reply_markup)
                else:
                    message = f"I couldn't find \"{item_to_remove}\" in your list. Type /list to see your current list if you need help."                    
                    updater.message.reply_text(text=message, parse_mode=telegram.ParseMode.HTML)

                #self.loop.run_until_complete(self.UpdateQueryList())

    @send_typing_action
    def RemoveAll(self, update, context):
        print(f"{update.message.from_user.first_name} {update.message.from_user.last_name} is trying to remove all items from their list...".replace(" None", ""))

        cur_list = context.user_data.get("game_list", "not found")
        if cur_list == "not found": cur_list = self.game_list

        cur_list.clear()

        print("Update complete.")
        message = f"@{update.message.from_user.first_name}: Removed all items from your list."

        update.message.reply_text(text=message, parse_mode=telegram.ParseMode.HTML)
        context.user_data["game_list"] = cur_list
        context.user_data["name"] = f"{update.message.from_user.first_name} {update.message.from_user.last_name}".replace(" None", "")

    @send_typing_action
    def DisplayHelp(self, update, context):
        print(f"{update.message.from_user.first_name} {update.message.from_user.last_name} is requesting help...".replace(" None", ""))

        message = f"Hiya, {update.message.from_user.first_name}!  Here's a list of the current commands and what they do:\n\n"
        message = f"{message}<b>/start</b>\n"
        message = f"{message} => Start your bot session!  You won't receive messages until you do this...\n\n"
        message = f"{message}<b>/add &lt;item or comma-separated list of items&gt;</b>\n"
        message = f"{message} => Adds an item or comma-separated list of items to the watch-list\n"
        message = f"{message} <i>ex: /add earthbound</i>\n\n"
        message = f"{message}<b>/rem &lt;item or comma-separated list of items&gt;</b>\n"
        message = f"{message} => Removes an item or comma-separated list of items from the watch-list\n"
        message = f"{message} <i>ex: /rem earthbound, chrono trigger</i>\n\n"
        message = f"{message}<b>/remall</b>\n"
        message = f"{message} => Remove all items from your list.\n\n"
        message = f"{message}<b>/help</b>\n"
        message = f"{message} => Displays this message!\n\n"
        message = f"{message}<b>/list</b>\n"
        message = f"{message} => Displays the current watch-list items\n\n"
        message = f"{message}<b>/subs</b>\n"
        message = f"{message} => Displays all the subreddits this bot will search for updates\n\n"
        message = f"{message}<b>/suggested</b>\n"
        message = f"{message} => Displays a list of suggested adds for general use.\n\n"
        message = f"{message}-----\nHope that helps!"        

        update.message.reply_text(text=message, parse_mode=telegram.ParseMode.HTML)
        context.user_data["name"] = f"{update.message.from_user.first_name} {update.message.from_user.last_name}".replace(" None", "")

    @send_typing_action
    def ListSubreddits(self, update, context):
        print(f"{update.message.from_user.first_name} {update.message.from_user.last_name} is requesting the list of subreddits".replace(" None", ""))

        subscribed = list(self.reddit.user.subreddits(limit=None))
        sub_list = "\n".join(sub.display_name for sub in subscribed)

        message = f"Hi, {update.message.from_user.first_name}!\nHere's a list of the subreddit this bot will track:\n-----\n{sub_list}\n-----"        

        update.message.reply_text(text=message, parse_mode=telegram.ParseMode.HTML)
        context.user_data["name"] = f"{update.message.from_user.first_name} {update.message.from_user.last_name}".replace(" None", "")

    @send_typing_action
    def DisplayList(self, update, context):
        print(f"{update.message.from_user.first_name} {update.message.from_user.last_name} is requesting the list of items...".replace(" None", ""))

        cur_list = context.user_data.get("game_list", "not found")
        if cur_list == "not found": cur_list = self.game_list

        message = f"Hi, {update.message.from_user.first_name}!\nHere's a list of your current search filters:\n-----\n"
        current_list = "\n".join(cur_list)
        message = f"{message}{current_list}\n-----"

        update.message.reply_text(text=message, parse_mode=telegram.ParseMode.HTML)
        context.user_data["game_list"] = cur_list
        context.user_data["name"] = f"{update.message.from_user.first_name} {update.message.from_user.last_name}".replace(" None", "")

    @send_typing_action
    def ListSuggestedTags(self, update, context):
        print(f"{update.message.from_user.first_name} {update.message.from_user.last_name} is requesting a list of suggested adds...".replace(" None", ""))

        message = f"Hi, {update.message.from_user.first_name}!\nHere are some suggestions you may want to add to your list:\n-----\n"
        message = f"{message}<b>Video Games</b>\n[Steam]\n[Green Man Gaming]\n[GameStop]\n[eShop/US]\n\n"
        message = f"{message}<b>PC Parts</b>\n[Case]\n[Cooler]\n[Fan]\n[HDD]\n[Keyboard]\n[Mouse]\n[RAM]\n[Mobo]\n[Prebuilt]\n[Controller]\n[CPU]\n[GPU]\n[Headphones]\n[Monitor]\n[PSU]\n[SSD - M2]\n[SSD - Sata]\n[VR]\n\n"
        message = f"{message}<b>General</b>\n[Amazon]\n-----\n"

        update.message.reply_text(text=message, parse_mode=telegram.ParseMode.HTML)
        context.user_data["name"] = f"{update.message.from_user.first_name} {update.message.from_user.last_name}".replace(" None", "")

    def ButtonPress(self, update, context):
        query = update.callback_query
        query.answer()

        query.message.from_user = query.from_user
        if "rem" in query.data:
            self.telegram.delete_message(chat_id=query.message.chat.id, message_id=query.message.message_id)
            item_to_remove = query.data.split("rem ")[1]

            # Remove an item
            print(f"Attempting to remove {item_to_remove}")
            context.args = [item_to_remove]
            self.RemoveItemFromList(update, context)
        elif "stats" in query.data:
            reddit_post = query.data.split("stats ")[1]

            submission = self.reddit.submission(id=reddit_post)
            self.UpdatePost(submission, query.message, query.inline_message_id)

    def dbg(self, update, context):
        print("\n\n\nDEBUG\n\n")
        print(f"INFO\n-----\nCHAT ID: {update.message.chat.id}\n-----\n\n")
        for user in self.userdata.items():
            print(f"USER INFO\n-----\nName: {user[1]['name']}\nID: {user[0]}\n-----")        

    def RegisterName(self, update, context):
        if context.user_data["name"] is not None: return

        print(f"Registering {update.message.from_user.first_name} {update.message.from_user.last_name}.".replace(" None", ""))
        context.user_data["name"] = f"{update.message.from_user.first_name} {update.message.from_user.last_name}".replace(" None", "")

    def StartBot(self, update, context):
        print(f"{update.message.from_user.first_name} {update.message.from_user.last_name} is starting a bot session...".replace(" None", ""))

        cur_list = context.user_data.get("game_list", "not found")
        if cur_list == "not found": 
            message = f"Hi, {update.message.from_user.first_name}!\nYou've been registered."
            cur_list = self.game_list
        else:
            message = f"Welcome back, {update.message.from_user.first_name}!\n"

            if update.message.chat.id != self.CHAT_ID:
                message = f"{message}\nI'll go ahead and /list for you:"
                update.message.reply_text(text=message, parse_mode=telegram.ParseMode.HTML)
                self.DisplayList(update, context)
                message = "Don't forget to use /help for a list of commands."
                update.message.reply_text(text=message, parse_mode=telegram.ParseMode.HTML)
            else:
                message = f"{message}\nYou can use /help for a list of commands."
                update.message.reply_text(text=message, parse_mode=telegram.ParseMode.HTML)

        context.user_data["game_list"] = cur_list
        context.user_data["name"] = f"{update.message.from_user.first_name} {update.message.from_user.last_name}".replace(" None", "")

    def InitTelegramBot(self):
        updater = Updater(self.BOT_ID, persistence=self.persistence, use_context=True, request_kwargs={"read_timeout": 15, "connect_timeout": 15})
        dp = updater.dispatcher
    
        # Commands
        dp.add_handler(CommandHandler('start', self.StartBot))
        dp.add_handler(CommandHandler('add', self.AddItemToList))
        dp.add_handler(CommandHandler('rem', self.RemoveItemFromList))
        dp.add_handler(CommandHandler('help', self.DisplayHelp))
        dp.add_handler(CommandHandler('list', self.DisplayList))
        dp.add_handler(CommandHandler('remall', self.RemoveAll))
        dp.add_handler(CommandHandler('subs', self.ListSubreddits))
        dp.add_handler(CommandHandler('suggested', self.ListSuggestedTags))

        # DEBUG
        dp.add_handler(CommandHandler('dbg', self.dbg))

        # Callbacks
        dp.add_handler(CallbackQueryHandler(self.ButtonPress))

        # Regular chat
        dp.add_handler(MessageHandler(Filters.text & ~Filters.command, self.RegisterName))

        self.userdata = self.persistence.get_user_data()

        updater.start_polling()
#       updater.idle()

    def SetMatch(self, term):
        self.match = term
        return True

    def GetTimeInPST(self, date_format="%m/%d/%Y.%H:%M:%S"):
        date = datetime.now(tz=utc)
        date = date.astimezone(timezone("US/Pacific"))
        pst_dt = date.strftime(date_format)
        return pst_dt

    def GetTimeDeltaString(self, created, check_limit = False, short_string=False):
        if short_string:
            date_format="%m/%d/%Y.%H:%M"
            date = datetime.fromtimestamp(created)           
            date = date.astimezone(timezone("US/Pacific"))
            pst_dt = date.strftime(date_format)
            return pst_dt

        # Do some futzing to generate a colloquial string describing how long ago the post was made.
        now = (datetime.utcnow() - datetime(1970,1,1)).total_seconds()
        then = created

        timedelta_text = "minutes ago"
        time_ago = round((now - then) / 60)
        
        if time_ago > self.match_limit and check_limit: 
            return False
 
        if time_ago > 59:
            hours_ago = math.floor(time_ago / 60)
            hours_text = "an hour" if hours_ago == 1 else f"{hours_ago} hours"
       
            minute_delta = time_ago - (hours_ago * 60)  
            minute_text = f" and {minute_delta} minutes ago" if minute_delta > 0 else ""
    
            if time_ago >= 60 * 24:
                days_ago = math.floor(time_ago / (60 * 24))
                days_text = "a day" if days_ago == 1 else f"{days_ago} days"
    
                hours_ago = hours_ago - (days_ago * 24)
                hours_text = "" if hours_ago == 0 else ", 1 hour" if hours_ago == 1 else f", {hours_ago} hours"
    
                minute_delta = time_ago - ((days_ago * 24 * 60) + (hours_ago * 60))
                minute_text = f", and {minute_delta} minutes ago" if minute_delta > 0 else ""
    
                timedelta_text = f"about {days_text}{hours_text}{minute_text}"
            else:    
                timedelta_text = f"about {hours_text}{minute_text}"
        else:
            timedelta_text = f"about {time_ago} minutes ago"

        return timedelta_text

    def InitDone(self):
        sleep(10)
        print("Init done.")
        self.init = False

    def UpdatePost(self, submission, message, inline_id):
        new_timedelta = self.GetTimeDeltaString(submission.created_utc, short_string=True)

        refresh_stats = telegram.InlineKeyboardButton(text=f"🕒: {new_timedelta} 🔄\n⬆️: {submission.score} | 💬: {submission.num_comments}", callback_data=f"stats {submission.id}")
        reply_keyboard = [[refresh_stats]]
        reply_markup = telegram.InlineKeyboardMarkup(reply_keyboard, one_time_keyboard=True)

        try:
            self.telegram.edit_message_reply_markup(chat_id=message.chat.id, message_id=message.message_id, inline_message_id=inline_id, reply_markup=reply_markup)
        except telegram.error.BadRequest:
            pass

    async def GetQueryList(self):
        print("Getting query list.")
        async with aiofiles.open("games","r") as f:
            for line in await f.readlines():
                self.game_list.append(line.strip())

    async def UpdateQueryList(self):
        print("Updating query list.")
        async with aiofiles.open("games","w") as file:
            file.seek(0)
            file.write(f"{(item.strip() for item in self.game_list)}\r\n")
            file.close()
        print("Done")    

    async def ConstructTelegramMessage(self, submission, timedelta_text, user_id):
        if "$" in submission.title and "$0" not in submission.title and self.match is not None:
            # Highlight from the result to the price in the title
            title_part_with_match = submission.title.lower().split(self.match.lower())[1]
            if "$" in title_part_with_match:
                price_part = f"${title_part_with_match.split('$')[1]}"
                if "." in price_part:
                    price_part = f"{price_part.split('.')[0]}.{price_part.split('.')[1][:2]}"

                submission_pieces = submission.title.lower().split(self.match.lower())
                piece_with_price = f"<pre>{submission_pieces[0]}</pre><b><i><u>{self.match.upper()}{submission_pieces[1].split(price_part)[0].upper()}{price_part.upper()}</u></i></b><pre>{submission_pieces[1].split(price_part)[1].lower()}</pre>"

                message = f"<b>{self.match.upper()}</b> (/r/{submission.subreddit.display_name})\n----------------\n{piece_with_price}"
                self.match = None
            else:
                message = f"<b>{self.match.upper()}</b> (/r/{submission.subreddit.display_name})\n----------------\n<pre>{(submission.title.lower().replace(self.match.lower(), f'</pre><b><i><u>{self.match.upper()}</u></i></b><pre>'))}</pre>"
        elif self.match is not None:
            message = f"<b>{self.match.upper()}</b> (/r/{submission.subreddit.display_name})\n----------------\n<pre>{(submission.title.lower().replace(self.match.lower(), f'</pre><b><i><u>{self.match.upper()}</u></i></b><pre>'))}</pre>"
            self.match = None
        else:
            message = f"<b>Random Deal (so you know the bot is doing stuff)</b> (/r/{submission.subreddit.display_name})\n----------------\n<pre>{submission.title.lower()}</pre>"            

        message = f"{message}\n\n<b><a href='{submission.url}'>Link to Sale</a></b> | <b><a href='https://www.reddit.com{submission.permalink}'>View Reddit Comments</a></b>\n\n-----"

        new_timedelta = self.GetTimeDeltaString(submission.created_utc, short_string=True)
        refresh_stats = telegram.InlineKeyboardButton(text=f"🕒: {new_timedelta} 🔄\n⬆️: {submission.score} | 💬: {submission.num_comments}", callback_data=f"stats {submission.id}")
        reply_keyboard = [[refresh_stats]]
        reply_markup = telegram.InlineKeyboardMarkup(reply_keyboard, one_time_keyboard=True)

        if user_id is None:
            self.telegram.send_message(chat_id=self.CHAT_ID, text=message, parse_mode=telegram.ParseMode.HTML, timeout=15, reply_markup=reply_markup)
        else:
            try:
                self.telegram.send_message(chat_id=user_id, text=message, parse_mode=telegram.ParseMode.HTML, timeout=15, reply_markup=reply_markup)
            except AttributeError as e:
                print(f"Unable to send message as intended: {type(e).__name__} ::: {e}")
                traceback.print_exc()
            except Exception as e:
                message = f"{message}\n----------\n<b>If you want to get these in a private message instead, start a chat with @RedditDealBot directly.</b>"
                self.telegram.send_message(chat_id=self.CHAT_ID, text=message, parse_mode=telegram.ParseMode.HTML, timeout=15, reply_markup=reply_markup)

    def ListenForDeals(self):
        loop = asyncio.get_event_loop()

        loop.run_until_complete(self.GetQueryList())

        # Get the subs that the bot is joined to
        print("Building multi-reddit...")
        subscribed = list(self.reddit.user.subreddits(limit=None))
        subscribed_as_string = "+".join(sub.display_name for sub in subscribed)

        multireddit = self.reddit.subreddit(subscribed_as_string)
        print("Done")

        try:
            thread = Thread(target=self.InitDone)    
            thread.start()

            # iterate over each of them
            for submission in multireddit.stream.submissions():
                print(f"[{self.GetTimeInPST()}] ::: Searching for matches in posts. Last detected post:", end=" ")
                
                found_match = False
                randomly_sent_to_chat = False
                self.SetMatch(None)
                self.userdata = self.persistence.get_user_data()

                for user in self.userdata.items():
                    if user[1]["game_list"] is None: continue
                    if any(phrase.strip().lower() in submission.title.lower() and self.SetMatch(phrase.strip()) for phrase in user[1]["game_list"]):
                        timedelta_text = self.GetTimeDeltaString(submission.created_utc, True)                        
                        if not timedelta_text: continue

                        print(f"\n{('(UNKNOWN USER)' if user[1]['name'] is None else '(' + user[1]['name'] + ')')} ==> Keyword match found!\n :: Keyword: {self.match}\n  :: {submission.title}\n  :: posted {timedelta_text}\n---\n\n")
    
                        # Do Match Stuff Here
                        found_match = True
                        loop.run_until_complete(self.ConstructTelegramMessage(submission, timedelta_text, user[0]))
            
                if random.randint(0,200) in self.rand_nums and not self.init: # 2.5% chance
                    timedelta_text = self.GetTimeDeltaString(submission.created_utc)
                    randomly_sent_to_chat = True

                    # Send random deal to main chat
                    loop.run_until_complete(self.ConstructTelegramMessage(submission, timedelta_text, None))

                if not found_match:
                    timedelta_text = self.GetTimeDeltaString(submission.created_utc)
                    print(f"{('RANDOM DISPLAY: ' if randomly_sent_to_chat else '')}/r/{submission.subreddit.display_name} => {submission.title}, posted {timedelta_text}")
        
        except Exception as e:
            print(f"Error in reddit stream: {e}")
            sleep(60)
            self.init = True
            self.ListenForDeals()

if __name__ == "__main__":
    dealbot = RedditDealsBot()
    dealbot.InitTelegramBot()
    dealbot.ListenForDeals()
