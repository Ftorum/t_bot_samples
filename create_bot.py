from aiogram import Bot
from aiogram.dispatcher import Dispatcher
from config import config
from aiogram.contrib.fsm_storage.memory import MemoryStorage

storage = MemoryStorage()

bot = Bot(token=config.BOT_TOKEN)
dp = Dispatcher(bot, storage=storage)

async def on_startup(dp):
    await bot.set_webhook(config.URL_APP)


async def on_shutdown(dp):
    await bot.delete_webhook()