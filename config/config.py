import os

from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = str(os.getenv("BOT_TOKEN"))
ADMIN_ID = str(os.getenv("ADMIN_ID")) 
URL_APP = str(os.getenv("URL_APP")) 