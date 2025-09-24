import os
import asyncio
import logging
from typing import Optional
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
import aiohttp

# Загружаем .env
load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")
LOG_FILE = os.getenv("LOG_FILE", "bot.log")
MANAGER_URL = os.getenv("MANAGER_URL")  # e.g. http://localhost:5000
BOT_ID = os.getenv("BOT_ID")  # numeric id assigned by manager

# Настраиваем логирование
logging.basicConfig(
    level=logging.INFO,  # Уровень логов (DEBUG для подробного вывода)
    format="%(asctime)s - [%(levelname)s] - %(name)s - %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE, encoding="utf-8"),  # Логи в файл
        logging.StreamHandler()  # Логи в консоль
    ]
)
logger = logging.getLogger(__name__)

# Создаем объекты бота и диспетчера
bot = Bot(token=TOKEN)
dp = Dispatcher()

async def post_message_to_manager(user_id: Optional[int], chat_id: Optional[int], text: str, msg_type: str = "text") -> None:
    if not MANAGER_URL or not BOT_ID:
        return
    url = f"{MANAGER_URL.rstrip('/')}/api/bots/{BOT_ID}/messages"
    headers = {"X-Bot-Token": TOKEN} if TOKEN else {}
    payload = {
        "user_id": user_id,
        "chat_id": chat_id,
        "text": text,
        "type": msg_type,
    }
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=payload, headers=headers, timeout=10) as resp:
                if resp.status >= 400:
                    logger.warning("Manager ingest failed: %s %s", resp.status, await resp.text())
    except Exception as e:
        logger.debug("Failed to send message to manager: %s", e)

# Хэндлер команды /start
@dp.message(Command("start"))
async def start_handler(message: types.Message):
    logger.info(f"Пользователь {message.from_user.id} запустил /start")
    await message.answer("Привет! Я бот с логированием 🤖123")
    await post_message_to_manager(message.from_user.id if message.from_user else None, message.chat.id if message.chat else None, "/start", "command")

# Эхо-бот: повторяет все сообщения
@dp.message()
async def echo_handler(message: types.Message):
    logger.info(f"Получено сообщение от {message.from_user.id}: {message.text}")
    await message.answer(f"Вы написали: {message.text}")
    await post_message_to_manager(message.from_user.id if message.from_user else None, message.chat.id if message.chat else None, message.text or "", "text")

async def main():
    logger.info("Бот запускается 🚀")
    try:
        await dp.start_polling(bot)
    except Exception as e:
        logger.exception(f"Ошибка при запуске бота: {e}")
    finally:
        logger.info("Бот остановлен ❌")

if __name__ == "__main__":
    asyncio.run(main())
