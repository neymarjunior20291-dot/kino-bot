import telebot
import sqlite3
import os

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = 8207056366

bot = telebot.TeleBot(BOT_TOKEN)

db = sqlite3.connect("movies.db", check_same_thread=False)
cursor = db.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS movies (
    code TEXT PRIMARY KEY,
    file_id TEXT
)
""")
db.commit()

temp_videos = {}

@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(
        message,
        "🎬 Kino botga xush kelibsiz!\n\nKino kodini yuboring."
    )

@bot.message_handler(content_types=['video'])
def add_video(message):
    if message.from_user.id != ADMIN_ID:
        return

    temp_videos[message.message_id] = message.video.file_id

    bot.reply_to(
        message,
        "✅ Video qabul qilindi.\n\nEndi shu videoga reply qilib kino kodini yuboring."
    )

@bot.message_handler(func=lambda m: True)
def messages(message):

    if (
        message.from_user.id == ADMIN_ID
        and message.reply_to_message
        and message.reply_to_message.message_id in temp_videos
    ):
        code = message.text.strip()
        file_id = temp_videos[message.reply_to_message.message_id]

        cursor.execute(
            "INSERT OR REPLACE INTO movies VALUES (?, ?)",
            (code, file_id)
        )
        db.commit()

        bot.reply_to(message, f"✅ Kino qo'shildi.\nKod: {code}")
        return

    code = message.text.strip()

    cursor.execute(
        "SELECT file_id FROM movies WHERE code=?",
        (code,)
    )

    movie = cursor.fetchone()

    if movie:
        bot.send_video(message.chat.id, movie[0])
    else:
        bot.reply_to(message, "❌ Bunday kino topilmadi.")

print("Bot ishga tushdi...")
bot.infinity_polling(skip_pending=True)
