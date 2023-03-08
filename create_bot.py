import asyncio
from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.redis import RedisStorage2
from datetime import datetime
import os
import logging
from apscheduler.schedulers.asyncio import AsyncIOScheduler
import tzlocal

from db_handlers import time_period_get
# 5874860229:AAH2_hWPVfUBpt7qybnjvfb0FeqAepv3gWs  test
# 5575454212:AAGmtKOE8vGrZu7xh--k1FFV66mKjUNwyio  original

# AgACAgIAAxkBAAPJY_Xx4LXRl0NwEEjijCdTtPAUiPMAApHBMRvQybFLhEzBp3fjW0UBAAMCAAN5AAMuBA test
# AgACAgIAAxkBAAIe22MfWKQe0kNQ-MOkVGqa4oFjHO9rAAKfwjEb-dz5SNhQ_YJkWNSmAQADAgADeQADKQQ original
# token
TOKEN = "5575454212:AAGmtKOE8vGrZu7xh--k1FFV66mKjUNwyio"
PAYMENT_PROVIDER_TOKEN = "398062629:TEST:999999999_F91D 8F69C042267444B74CC0B3C747757EB0E065"
table_id = "AgACAgIAAxkBAAIe22MfWKQe0kNQ-MOkVGqa4oFjHO9rAAKfwjEb-dz5SNhQ_YJkWNSmAQADAgADeQADKQQ"
service = [266212760]

# configure logging
logging.basicConfig(level=logging.INFO)

# redis password for redis storage
# load_dotenv(find_dotenv())
password = os.environ.get("REDIS_PWD")

# initialize bot and its dispatcher
bot = Bot(token=TOKEN)
scheduler = AsyncIOScheduler(timezone=str(tzlocal.get_localzone()))


loop = asyncio.new_event_loop()
storage = RedisStorage2(host="redis-13310.c264.ap-south-1-1.ec2.cloud.redislabs.com", port=13310, password=password)
dp = Dispatcher(bot, storage=storage, loop=loop)


def time_check():
    now = datetime.now()
    time_s, time_f = now.replace(hour=9, minute=45), now.replace(hour=11, minute=40)
    return True if time_s < now < time_f or not time_period_get() else False
