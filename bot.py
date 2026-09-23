import telebot
import time
from flask import Flask
from threading import Thread
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardRemove
from pymongo import MongoClient

# ==========================================
# AAPKE DETAILS EKDUM SAHI HAIN
API_TOKEN = '8071350385:AAHVnOVTSiSoez-Sr99NMlpHuUwbsLB8gNw'
ADMIN_ID = 8293930284

CHANNEL_ID = '-1003174608918'
CHANNEL_LINK = 'https://t.me/+Ta3mYPpo4L02NTU1'

MONGO_URL = "mongodb+srv://kisankunayak143_db_user:O5sTopknwHsTzT9L@cluster0.g8mkyvd.mongodb.net/?appName=Cluster0"
# ==========================================

# MongoDB Setup
cluster = MongoClient(MONGO_URL)
db = cluster["bot_database"]
users_collection = db["users"]

bot = telebot.TeleBot(API_TOKEN)

# 24/7 Zinda Rakhne Wala Server
app = Flask(__name__)
@app.route('/')
def index():
    return "Bot Zinda Hai aur Database Connected Hai!"

def run():
    app.run(host="0.0.0.0", port=8080)

def keep_alive():
    t = Thread(target=run)
    t.start()

# User ID sidha Database me save karna
def save_user(user_id):
    if users_collection.count_documents({"user_id": user_id}) == 0:
        users_collection.insert_one({"user_id": user_id})

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
    
    remove_kb = ReplyKeyboardRemove()
    
    if is_joined(user_id):
        welcome_text = f"👋 <b>Welcome Back, {first_name}!</b>\n\nYou are already a member of our channel.\n\nUse /help to see available commands."
        bot.send_message(message.chat.id, welcome_text, parse_mode='html', reply_markup=remove_kb)
    else:
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

# 3. Auto Approve Join Request
@bot.chat_join_request_handler()
def approve_join_request(request):
    try:
        bot.approve_chat_join_request(request.chat.id, request.from_user.id)
        text = f"✅ Join Request Approved!\n\nWelcome to 𝗣𝗥𝗘𝗗𝗜𝗖𝗧𝗢𝗥 APP 🚀, {request.from_user.first_name}! 🎉\n\nYou are now a member of the channel.\nStay tuned for the latest updates!\n\nUse /help to see available commands."
        remove_kb = ReplyKeyboardRemove()
        bot.send_message(request.from_user.id, text, reply_markup=remove_kb)
    except Exception as e:
        print(f"Approve Error: {e}")

# --- Text aur Video/Photo Caption se Buttons nikalne ka engine ---
def extract_text_and_buttons(raw_text):
    if not raw_text: return "", None
    lines = raw_text.split('\n')
    final_text = ""
    markup = InlineKeyboardMarkup(row_width=1)
    has_buttons = False
    
    for line in lines:
        if "##" in line:
            parts = line.split("##")
            if len(parts) >= 3:
                btn_name = parts[1].strip()
                btn_url = parts[2].strip()
                if not btn_url.startswith("http"): btn_url = "https://" + btn_url
                markup.add(InlineKeyboardButton(btn_name, url=btn_url))
                has_buttons = True
        else:
            final_text += line + "\n"
    return final_text.strip(), markup if has_buttons else None

# --- Channel Post (Ab Video/Photo bhi support karega) ---
@bot.message_handler(content_types=['text', 'photo', 'video', 'document'], func=lambda m: m.from_user.id == ADMIN_ID and ((m.text and m.text.startswith('/post')) or (m.caption and m.caption.startswith('/post'))))
def channel_post(message):
    try:
        raw_text = (message.text or message.caption).replace('/post', '', 1).strip()
        if not raw_text:
            bot.send_message(ADMIN_ID, "❌ Format galat hai. Likhne ka tarika:\n/post Message\n## Button 1 ## Link")
            return
            
        final_text, inline_markup = extract_text_and_buttons(raw_text)
        
        if message.content_type == 'text':
            bot.send_message(CHANNEL_ID, final_text, reply_markup=inline_markup)
        elif message.content_type == 'photo':
            bot.send_photo(CHANNEL_ID, message.photo[-1].file_id, caption=final_text, reply_markup=inline_markup)
        elif message.content_type == 'video':
            bot.send_video(CHANNEL_ID, message.video.file_id, caption=final_text, reply_markup=inline_markup)
        elif message.content_type == 'document':
            bot.send_document(CHANNEL_ID, message.document.file_id, caption=final_text, reply_markup=inline_markup)
            
        bot.send_message(ADMIN_ID, "✅ Post successfully channel me chali gayi!")
    except Exception as e:
        bot.send_message(ADMIN_ID, f"❌ Error: {e}")

# --- Smart Broadcast (Ab Video/Photo bhi support karega) ---
@bot.message_handler(content_types=['text', 'photo', 'video', 'document'], func=lambda message: message.from_user.id == ADMIN_ID)
def admin_broadcast(message):
    raw_text = message.text or message.caption
    if raw_text and raw_text.startswith('/'): return
        
    all_users = users_collection.find()
    total_users = users_collection.count_documents({})
    
    if total_users == 0:
        bot.send_message(ADMIN_ID, "❌ Database me koi user nahi hai.")
        return
        
    final_text, inline_markup = extract_text_and_buttons(raw_text)
    
    sent = 0
    bot.send_message(ADMIN_ID, f"⏳ Broadcasting started to {total_users} members...")
    for user_data in all_users:
        user = user_data["user_id"]
        if int(user) == ADMIN_ID: continue
        try:
            if message.content_type == 'text':
                bot.send_message(user, final_text, reply_markup=inline_markup)
            elif message.content_type == 'photo':
                bot.send_photo(user, message.photo[-1].file_id, caption=final_text, reply_markup=inline_markup)
            elif message.content_type == 'video':
                bot.send_video(user, message.video.file_id, caption=final_text, reply_markup=inline_markup)
            elif message.content_type == 'document':
                bot.send_document(user, message.document.file_id, caption=final_text, reply_markup=inline_markup)
            sent += 1
            time.sleep(0.05)
        except: continue
    bot.send_message(ADMIN_ID, f"✅ Broadcast sent to {sent} members.")

# Baaki logo ke normal messages ignore
@bot.message_handler(func=lambda message: message.from_user.id != ADMIN_ID)
def silence(message):
    pass

print("Bot is starting...")
bot.remove_webhook() 
time.sleep(1)
keep_alive()
bot.infinity_polling(allowed_updates=['message', 'chat_join_request'])
