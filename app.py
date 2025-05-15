from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

async def echo(update: Update, _) -> None:
    await update.message.reply_text(update.message.text)

app = ApplicationBuilder().token(
    os.getenv("TELEGRAM_API_TOKEN")).build()

app.add_handler(MessageHandler(None, echo))

app.run_polling()
