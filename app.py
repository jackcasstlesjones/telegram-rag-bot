from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, CommandHandler, ContextTypes
import os
from dotenv import load_dotenv
from openai import OpenAI

gh_link = 'https://github.com/jackcasstlesjones/telegram-rag-bot'

# Load environment variables from .env file
load_dotenv()


client = OpenAI(
    # This is the default and can be omitted
    api_key=os.environ.get("OPENAI_API_KEY"),
)


async def code(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(f'The link is: {gh_link}')


async def echo(update: Update, _) -> None:
    # Get user's message
    user_message = update.message.text

    # Generate response from OpenAI
    response = client.responses.create(
        model="gpt-4o",
        instructions="You are a coding assistant that talks like a surfer.",
        input=user_message
    )

    # Send the response back to the user
    await update.message.reply_text(response.output_text)

app = ApplicationBuilder().token(
    os.getenv("TELEGRAM_API_TOKEN")).build()

app.add_handler(CommandHandler("code", code))
app.add_handler(MessageHandler(None, echo))

app.run_polling()
