from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, CommandHandler, ContextTypes
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


ghLink = 'https://github.com/jackcasstlesjones/telegram-rag-bot'


async def code(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(f'The link is: {ghLink}')


async def echo(update: Update, _) -> None:
    await update.message.reply_text(update.message.text)

app = ApplicationBuilder().token(
    os.getenv("TELEGRAM_API_TOKEN")).build()


app.add_handler(CommandHandler("code", code))
app.add_handler(MessageHandler(None, echo))

app.run_polling()
