# telegram-voice-chat-bot
telegram voice chat
import os
import telebot
import requests
from gtts import gTTS
from io import BytesIO
import openai

# 🔐 دریافت توکن‌ها از متغیرهای محیطی (بهتر برای GitHub)
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN)
openai.api_key = OPENAI_API_KEY


def speech_to_text(audio_file_path):
    with open(audio_file_path, "rb") as audio:
        transcript = openai.Audio.transcriptions.create(
            model="whisper-1",
            file=audio
        )
    return transcript.text


def generate_reply(user_text):
    response = openai.Chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful Persian-speaking voice assistant."},
            {"role": "user", "content": user_text}
        ]
    )
    return response.choices[0].message.content.strip()


def text_to_speech(text):
    tts = gTTS(text=text, lang="fa")
    voice_bytes = BytesIO()
    tts.write_to_fp(voice_bytes)
    voice_bytes.seek(0)
    return voice_bytes


@bot.message_handler(content_types=['voice'])
def handle_voice(message):
    try:
        file_info = bot.get_file(message.voice.file_id)
        downloaded_file = bot.download_file(file_info.file_path)

        voice_path = "user_voice.ogg"
        with open(voice_path, 'wb') as new_file:
            new_file.write(downloaded_file)

        user_text = speech_to_text(voice_path)
        bot.reply_to(message, f"🗣 گفتی: {user_text}")

        reply_text = generate_reply(user_text)
        bot.send_message(message.chat.id, f"🤖 پاسخ: {reply_text}")

        voice_bytes = text_to_speech(reply_text)
        bot.send_voice(message.chat.id, voice_bytes)

    except Exception as e:
        bot.send_message(message.chat.id, f"⚠️ خطا: {str(e)}")


@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "سلام 👋 من یه ربات چت صوتی هستم. برام ویس بفرست 🎤")


print("🤖 ربات روی GitHub فعال شد...")
bot.polling(non_stop=True)
