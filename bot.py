import telebot
import os
import time
from flask import Flask
from threading import Thread
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove

API_TOKEN = '8071350385:AAE7_FgUoz4zdnI1auiCqS9ANqR0yi6xOIs'
ADMIN_ID = 8293930284

CHANNEL_ID = '-1003174608918'
CHANNEL_LINK = 'https://t.me/+pFPksaKxcf1jODFl'

bot = telebot.TeleBot(API_TOKEN)

# 24/7 Zinda Rakhne Wala Server
app = Flask(__name__)
@app.route('/')
def index():
    return "Bot Zinda Hai aur 24/7 chal raha hai!"

def run():
    app.run(host="0.0.0.0", port=8080)

def keep_alive():
    t = Thread(target=run)
    t.start()

# User ID save karna
def save_user(user_id):
    if not os.path.exists("users.txt"):
        with open("users.txt", "w") as f: pass
    with open("users.txt", "r+") as f:
        users = f.read().splitlines()
        if str(user_id) not in users:
            f.write(str(user_id) + "\n")

# Check karna ki user channel me hai ya nahi
def is_joined(user_id):
    try:
        status = bot.get_chat_member(CHANNEL_ID, user_id).status
        if status in ['creator', 'administrator', 'member']:
            return True
        return False
    except:
        return False

# 1. /start command
@bot.message_handler(commands=['start'])
def send_welcome(message):
    user_id = message.from_user.id
    first_name = message.from_user.first_name
    save_user(user_id)
    
    if is_joined(user_id):
        # Agar user joined hai, toh aapka purana wala pasandida welcome message
        markup = ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add(KeyboardButton("Start Hack 🧩"))
        welcome_text = f"👋 <b>Welcome Back, {first_name}!</b>\n\nYou are already a member of our channel.\n\nUse /help to see available commands."
        bot.send_message(message.chat.id, welcome_text, parse_mode='html', reply_markup=markup)
    else:
        # Naye user ke liye force sub
        remove_kb = ReplyKeyboardRemove()
        join_text = f"👋 Hello {first_name}!\n\nTo use this bot, you need to join our channel first.\n\nHow to join?\n1️⃣ Click the button below\n2️⃣ Send join request\n3️⃣ You will be automatically approved! ✅"
        bot.send_message(message.chat.id, join_text, reply_markup=remove_kb)
        
        inline_markup = InlineKeyboardMarkup()
        inline_markup.add(InlineKeyboardButton("📢 Join PREDICTOR APP 🚀", url=CHANNEL_LINK))
        bot.send_message(message.chat.id, "👇 Click here:", reply_markup=inline_markup)

# 2. /help command (Jo main bhool gaya tha, ab add kar diya hai)
@bot.message_handler(commands=['help'])
def send_help(message):
    try:
        help_text = "🤖 <b>Available Commands</b>\n━━━━━━━━━━━━━━━━━━\n/start - Start the bot\n/help - This help message\n━━━━━━━━━━━━━━━━━━\n📞 <b>Need help? Contact admin!</b>"
        bot.send_message(message.chat.id, help_text, parse_mode='html')
    except Exception as e:
        print(f"Help Error: {e}")

# 3. Auto Approve Join Request
@bot.chat_join_request_handler()
def approve_join_request(message):
    try:
        bot.approve_chat_join_request(CHANNEL_ID, message.from_user.id)
        markup = ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add(KeyboardButton("Start Hack 🧩"))
        text = f"✅ Join Request Approved!\n\nWelcome to PREDICTOR APP 🚀, {message.from_user.first_name}! 🎉\n\nYou are now a member of the channel."
        bot.send_message(message.from_user.id, text, reply_markup=markup)
    except Exception as e:
        print(f"Approve Error: {e}")

# 4. Start Hack Button
@bot.message_handler(func=lambda message: message.text == "Start Hack 🧩")
def handle_hack_button(message):
    user_id = message.from_user.id
    if is_joined(user_id):
        bot.send_message(message.chat.id, "Prediction 4.0 Server connected! 🌐 (Aage ka code yahan aayega)")
    else:
        send_welcome(message)

# 5. Smart Broadcast (Button ke sath)
@bot.message_handler(func=lambda message: message.from_user.id == ADMIN_ID)
def admin_broadcast(message):
    if message.text.startswith('/'):
        return
        
    if not os.path.exists("users.txt"):
        bot.send_message(ADMIN_ID, "❌ Koi user nahi hai.")
        return
        
    with open("users.txt", "r") as f:
        users = f.read().splitlines()
        
    broadcast_text = message.text
    inline_markup = None
    
    if "||" in message.text:
        parts = message.text.split("||")
        if len(parts) >= 3:
            broadcast_text = parts[0].strip()
            btn_name = parts[1].strip()
            btn_url = parts[2].strip()
            
            inline_markup = InlineKeyboardMarkup()
            inline_markup.add(InlineKeyboardButton(btn_name, url=btn_url))

    sent = 0
    bot.send_message(ADMIN_ID, "⏳ Broadcasting started...")
    
    for user in users:
        if int(user) == ADMIN_ID:
            continue
        try:
            bot.send_message(user, broadcast_text, reply_markup=inline_markup)
            sent += 1
            time.sleep(0.05)
        except:
            continue
            
    bot.send_message(ADMIN_ID, f"✅ Broadcast sent to {sent} members.")

# Baaki logo ke normal messages ignore
@bot.message_handler(func=lambda message: message.from_user.id != ADMIN_ID and message.text != "Start Hack 🧩")
def silence(message):
    pass

print("Bot is starting...")
keep_alive()
bot.infinity_polling()
