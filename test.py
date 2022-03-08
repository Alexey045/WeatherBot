import asyncio
import logging
from os import getenv
from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.types import ContentType
from aiogram.utils import executor
import apscheduler
from apscheduler.schedulers.asyncio import AsyncIOScheduler

bot_token = getenv("BOT_TOKEN")
bot = Bot(token=bot_token)
scheduler = AsyncIOScheduler()
logging.basicConfig(level=logging.INFO)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)
jobs = {}
counter = 0


async def noon_print(text, id):
    await bot.send_message(id, text)


@dp.message_handler(commands="cancel_test", content_types=[ContentType.TEXT])
async def on_cancel(message: types.Message):
    scheduler.remove_job(jobs[message.chat.id][0])


@dp.message_handler(commands="start_test", content_types=[ContentType.TEXT])
async def on_startup(message: types.Message):
    text = message.text.split()[-1]
    scheduler.add_job(noon_print, trigger='interval', seconds=2, id=str(counter),
                      args=[text, message.chat.id])
    scheduler.start()
    jobs[message.chat.id] = [str(counter)]


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=False)
