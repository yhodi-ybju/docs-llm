import os
import django
from dotenv import load_dotenv

load_dotenv()
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'docs_llm.settings')
django.setup()

import logging
import asyncio
from pathlib import Path

from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command

from app.services import DocumentIndexingService

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
if not TELEGRAM_TOKEN:
    logger.error("TELEGRAM_TOKEN is not set in environment variables")
    exit(1)

bot = Bot(token=TELEGRAM_TOKEN)
dp = Dispatcher()

service = DocumentIndexingService()

UPLOADS_DIR = Path("uploads")
UPLOADS_DIR.mkdir(exist_ok=True)

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer(
        "Привет! Отправь PDF для индексации, потом задавай вопросы по документу."
    )

@dp.message(lambda message: message.document and message.document.mime_type == 'application/pdf')
async def handle_document(message: types.Message):
    file_name = message.document.file_name
    dest = UPLOADS_DIR / file_name
    file_id = message.document.file_id
    file_obj = await bot.get_file(file_id)
    await bot.download_file(file_obj.file_path, destination=str(dest))
    await message.answer("Документ получен, индексирую...")

    loop = asyncio.get_event_loop()
    try:
        num_chunks = await loop.run_in_executor(None, service.indexFile, str(dest))
        await message.answer(f"Индексация готова: {num_chunks} фрагментов.")
    except Exception as e:
        logger.exception("Indexing error")
        await message.answer(f"Ошибка индексации: {e}")

@dp.message(lambda message: message.text and not message.document)
async def handle_query(message: types.Message):
    question = message.text.strip()
    await message.answer("Ищу ответ...")
    loop = asyncio.get_event_loop()
    try:
        answer = await loop.run_in_executor(None, service.answerQuery, question)
        await message.answer(answer)
    except Exception as e:
        logger.exception("Answer error")
        await message.answer(f"Ошибка при ответе: {e}")

async def main():
    await dp.start_polling(bot, skip_updates=True)

if __name__ == "__main__":
    asyncio.run(main())
