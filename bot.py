import telebot
import os
import time
from flask import Flask
from threading import Thread

# Yahan Aapka Token Aur Admin ID Hai
API_TOKEN = '8071350385:AAE7_FgUoz4zdnI1auiCqS9ANqR0yi6xOIs'
ADMIN_ID = 8293930284

bot = telebot.TeleBot(API_TOKEN)

# 24/7 Zinda Rakhne Wala Background Server
app = Flask(__name__)
@app.route('/')
def index():
    return "Bot Zinda Hai aur 24/7 chal raha hai!"

def run():
    app.run(host="0.0.0.0", port=8080)

def keep_alive():
    t = Thread(target=run)
    t.start()

# User ID save karne wala function
def save_user(user_id):
    if not os.path.exists("users.txt"):
        with open("users.txt", "w") as f: pass
    with open("users.txt", "r+") as f:
        users = f.read().splitlines()
        if str(user_id) not in users:
            f.write(str(user_id) + "\n")

# /start command
@bot.message_handler(commands=['start'])
def send_welcome(message):
    save_user(message.chat.id)
    try:
        user_name = message.from_user.first_name
        welcome_text = f"👋 <b>Welcome Back, {user_name}!</b>\n\nYou are already a member of our channel.\n\nUse /help to see available commands."
        bot.send_message(message.chat.id, welcome_text, parse_mode='html')
    except Exception as e:
        print(f"Start Error: {e}")

# /help command
@bot.message_handler(commands=['help'])
def send_help(message):
    try:
        help_text = "🤖 <b>Available Commands</b>\n━━━━━━━━━━━━━━━━━━\n/start - Start the bot\n/help - This help message\n━━━━━━━━━━━━━━━━━━\n📞 <b>Need help? Contact admin!</b>"
        bot.send_message(message.chat.id, help_text, parse_mode='html')
    except Exception as e:
        print(f"Help Error: {e}")

# Broadcast System (Sirf Admin bhejega)
@bot.message_handler(func=lambda message: message.from_user.id == ADMIN_ID)
def admin_broadcast(message):
    if message.text.startswith('/'):
        return
    if not os.path.exists("users.txt"):
        bot.send_message(ADMIN_ID, "❌ Abhi tak koi user nahi hai.")
        return
    with open("users.txt", "r") as f:
        users = f.read().splitlines()
    sent = 0
    for user in users:
        if int(user) == ADMIN_ID:
            continue
        try:
            bot.send_message(user, message.text)
            sent += 1
            time.sleep(0.05)
        except:
            continue
    bot.send_message(ADMIN_ID, f"✅ Message sent to {sent} members.")

# Baaki logo ke message ignore karna
@bot.message_handler(func=lambda message: message.from_user.id != ADMIN_ID)
def silence(message):
    pass

print("Bot is starting...")
keep_alive()
bot.infinity_polling()
