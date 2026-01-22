import asyncio
import logging
import os
from dotenv import load_dotenv

from aiogram import Bot, Dispatcher, types, F
from aiogram.filters.command import Command
from aiogram.enums import ParseMode
from openai import AsyncOpenAI

# 1. Setup Logging (Shows professionalism)
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(name)s - %(message)s")
logger = logging.getLogger(__name__)

# 2. Load Environment Variables (Security best practice)
load_dotenv()
TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# 3. Validation
if not TELEGRAM_TOKEN or not OPENAI_API_KEY:
    logger.critical("Error: TELEGRAM_BOT_TOKEN or OPENAI_API_KEY missing in .env file")
    exit(1)

# 4. Initialize Bot, Dispatcher, and OpenAI Client
# Using HTML parse mode for nice formatting
bot = Bot(token=TELEGRAM_TOKEN)
dp = Dispatcher()
# Using AsyncOpenAI client for non-blocking I/O
openai_client = AsyncOpenAI(api_key=OPENAI_API_KEY)

# --- Handlers ---

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    """
    Handler for the /start command.
    """
    await message.answer(
        "👋 <b>Hello! I'm an AI Support Demo Bot.</b>\n\n"
        "I demonstrate how to integrate <code>aiogram</code> with OpenAI API "
        "in an asynchronous way.\n\n"
        "Just send me any question, and I'll answer using GPT-3.5 Turbo!",
        parse_mode=ParseMode.HTML
    )

async def generate_ai_response(prompt_text: str) -> str:
    """
    Function to call OpenAI API asynchronously.
    """
    try:
        response = await openai_client.chat.completions.create(
            model="gpt-3.5-turbo", # Using 3.5 for cheaper demos, can be swapped for gpt-4
            messages=[
                {"role": "system", "content": "You are a helpful and concise technical support assistant."},
                {"role": "user", "content": prompt_text}
            ],
            max_tokens=300,
            temperature=0.7,
        )
        return response.choices[0].message.content
    except Exception as e:
        logger.error(f"OpenAI API Error: {e}")
        return "⚠️ Sorry, I encountered an error connecting to the AI brain. Please try again later."

@dp.message(F.text)
async def handle_user_message(message: types.Message):
    """
    Handler for all text messages. Sends user input to OpenAI and replies with the result.
    """
    user_id = message.from_user.id
    logger.info(f"Received message from User ID {user_id}: {message.text[:50]}...")

    # Send a "typing" action to improve UX while waiting for AI
    await bot.send_chat_action(chat_id=message.chat.id, action="typing")

    # Generate response asynchronously
    ai_reply = await generate_ai_response(message.text)

    # Reply to the user
    await message.reply(ai_reply)


# --- Main Execution ---
async def main():
    """
    Entry point. Starts polling.
    """
    logger.info("Starting bot polling...")
    # Drop pending updates to avoid spam on startup
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.info("Bot stopped!")
