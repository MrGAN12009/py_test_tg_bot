import os
import asyncio
import logging
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command

# Загружаем .env
load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")
LOG_FILE = os.getenv("LOG_FILE", "bot.log")

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

# Хэндлер команды /start
@dp.message(Command("start"))
async def start_handler(message: types.Message):
    logger.info(f"Пользователь {message.from_user.id} запустил /start")
    await message.answer("Привет! Я бот с логированием 🤖")

# Эхо-бот: повторяет все сообщения
@dp.message()
async def echo_handler(message: types.Message):
    logger.info(f"Получено сообщение от {message.from_user.id}: {message.text}")
    await message.answer(f"Вы написали: {message.text}")

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
