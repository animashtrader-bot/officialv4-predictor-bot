import telebot
import os
import time
from flask import Flask
from threading import Thread
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardRemove

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
    
    # Har baar jab /start ho, kisi bhi purane reply keyboard ko hata do
    remove_kb = ReplyKeyboardRemove()
    
    if is_joined(user_id):
        # Already Joined: Seedha Welcome Back Message (No Button)
        welcome_text = f"👋 <b>Welcome Back, {first_name}!</b>\n\nYou are already a member of our channel.\n\nUse /help to see available commands."
        bot.send_message(message.chat.id, welcome_text, parse_mode='html', reply_markup=remove_kb)
    else:
        # Not Joined: Hello Name aur Join Button (No Reply Keyboard Button)
        join_text = f"👋 Hello {first_name}!\n\nTo use this bot, you need to join our channel first.\n\nHow to join?\n1️⃣ Click the button below\n2️⃣ Send join request\n3️⃣ You will be automatically approved! ✅\n\n👇 Click here:"
        
        inline_markup = InlineKeyboardMarkup()
        inline_markup.add(InlineKeyboardButton("📢 Join PREDICTOR APP 🚀", url=CHANNEL_LINK))
        bot.send_message(message.chat.id, join_text, reply_markup=inline_markup)

# 2. /help command
@bot.message_handler(commands=['help'])
def send_help(message):
    try:
        help_text = "🤖 <b>Available Commands</b>\n━━━━━━━━━━━━━━━━━━\n/start - Start the bot\n/help - This help message\n━━━━━━━━━━━━━━━━━━\n📞 <b>Need help? Contact admin!</b>"
        bot.send_message(message.chat.id, help_text, parse_mode='html')
    except Exception as e:
        print(f"Help Error: {e}")

# 3. Auto Approve Join Request (Instant Message, No Button)
@bot.chat_join_request_handler()
def approve_join_request(message):
    try:
        bot.approve_chat_join_request(CHANNEL_ID, message.from_user.id)
        
        # Approve hote hi exactly wahi message jo aapne manga
        text = f"✅ Join Request Approved!\n\nWelcome to 𝗣𝗥𝗘𝗗𝗜𝗖𝗧𝗢𝗥 APP 🚀, {message.from_user.first_name}! 🎉\n\nYou are now a member of the channel.\nStay tuned for the latest updates!\n\nUse /help to see available commands."
        
        # Koi button nahi lagaya hai
        remove_kb = ReplyKeyboardRemove()
        bot.send_message(message.from_user.id, text, reply_markup=remove_kb)
    except Exception as e:
        print(f"Approve Error: {e}")

# 4. Smart Broadcast System (Admin ke liye, Button laga bhi sakte hain aur nahi bhi)
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
    
    # Check if admin wants to add a button (Message || Button || Link)
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

# Baaki messages ko ignore karein
@bot.message_handler(func=lambda message: message.from_user.id != ADMIN_ID)
def silence(message):
    pass

print("Bot is starting...")
# Webhook ko delete karke polling start karna (Error 409 se bachne ke liye)
bot.remove_webhook() 
time.sleep(1)
keep_alive()
bot.infinity_polling()
