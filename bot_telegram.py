from aiogram.utils import executor
from create_bot import dp, on_shutdown, on_startup
from data_base import sqlite_db
import os

async def on_startup(_):
    print('Бот вышел в онлайн')
    sqlite_db.sql_start()

from handlers import client, admin


client.register_handlers_client(dp)
admin.register_handlers_client(dp)


executor.start_webhook(
    dispatcher=dp,
    webhook_path='',
    on_startup=on_startup,
    on_shutdown=on_shutdown,
    skip_updates=True,
    host='0.0.0.0',
    port=int(os.environ.get('PORT', 5001))
)




# executor.start_polling(dp, skip_updates=True, on_startup=on_startup)