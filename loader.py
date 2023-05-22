from telebot import TeleBot
from telebot.storage import StateMemoryStorage
import os
from dotenv import load_dotenv
load_dotenv()


TOKEN = os.getenv('BOT_TOKEN')
API_KEY = os.getenv('API_KEY')

storage = StateMemoryStorage()
bot = TeleBot(token=TOKEN, state_storage=storage)
