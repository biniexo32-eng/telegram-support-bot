import asyncio
import logging
import os
import sqlite3
from pathlib import Path

from aiogram import Bot, Dispatcher, F, Router
from aiogram.filters import CommandStart
from aiogram.types import Message
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN", "").strip()
OWNER_CHAT_ID = int(os.getenv("OWNER_CHAT_ID", "0"))
DB_PATH = Path(os.getenv("DB_PATH", "support.sqlite3"))

if not BOT_TOKEN or not OWNER_CHAT_ID:
    raise RuntimeError("Set BOT_TOKEN and OWNER_CHAT_ID in .env")

logging.basicConfig(level=logging.INFO)
router = Router()


def db():
    connection = sqlite3.connect(DB_PATH)
    connection.execute(
        "CREATE TABLE IF NOT EXISTS message_map (owner_message_id INTEGER PRIMARY KEY, user_id INTEGER NOT NULL)"
    )
    connection.commit()
    return connection


def remember(owner_message_id: int, user_id: int):
    with db() as connection:
        connection.execute(
            "INSERT OR REPLACE INTO message_map(owner_message_id, user_id) VALUES (?, ?)",
            (owner_message_id, user_id),
        )
        connection.commit()


def find_user(owner_message_id: int):
    with db() as connection:
        row = connection.execute(
            "SELECT user_id FROM message_map WHERE owner_message_id = ?",
            (owner_message_id,),
        ).fetchone()
    return row[0] if row else None


@router.message(CommandStart())
async def start(message: Message):
    await message.answer(
        "Welcome to support. Send your message here and our team will reply as soon as possible."
    )


@router.message(F.chat.id == OWNER_CHAT_ID, F.reply_to_message)
async def owner_reply(message: Message, bot: Bot):
    replied_id = message.reply_to_message.message_id
    user_id = find_user(replied_id)
    if not user_id:
        await message.reply("I couldn't identify the customer for this reply. Reply directly to a forwarded customer message.")
        return

    try:
        await bot.copy_message(
            chat_id=user_id,
            from_chat_id=OWNER_CHAT_ID,
            message_id=message.message_id,
        )
    except Exception:
        await message.reply("The reply could not be delivered. The customer may have blocked the bot.")


@router.message(F.chat.id == OWNER_CHAT_ID)
async def owner_help(message: Message):
    await message.reply("Reply to a forwarded customer message to send your response to that customer.")


@router.message()
async def customer_message(message: Message, bot: Bot):
    user = message.from_user
    if not user:
        return
    name = user.full_name or "Unknown"
    username = f"@{user.username}" if user.username else "No username"
    header = await bot.send_message(
        OWNER_CHAT_ID,
        f"📩 New support message\n\n👤 {name}\n🔗 {username}\n🆔 <code>{user.id}</code>\n\nReply to this message to answer the customer.",
        parse_mode="HTML",
    )
    remember(header.message_id, user.id)
    copied = await bot.copy_message(
        chat_id=OWNER_CHAT_ID,
        from_chat_id=message.chat.id,
        message_id=message.message_id,
    )
    remember(copied.message_id, user.id)
    await message.answer("✅ Your message was sent to support. We will reply here.")


async def main():
    bot = Bot(BOT_TOKEN)
    dispatcher = Dispatcher()
    dispatcher.include_router(router)
    await dispatcher.start_polling(bot, allowed_updates=dispatcher.resolve_used_update_types())


if __name__ == "__main__":
    asyncio.run(main())
