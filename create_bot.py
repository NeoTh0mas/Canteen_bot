import asyncio
from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.redis import RedisStorage2
from dotenv import load_dotenv, find_dotenv
import os
import logging
from apscheduler.schedulers.asyncio import AsyncIOScheduler
import tzlocal


# token
TOKEN = "5575454212:AAGmtKOE8vGrZu7xh--k1FFV66mKjUNwyio"
PAYMENT_PROVIDER_TOKEN = "398062629:TEST:999999999_F91D8F69C042267444B74CC0B3C747757EB0E065"
service = 266212760

# configure logging
logging.basicConfig(level=logging.INFO)

# redis password for redis storage
load_dotenv(find_dotenv())
password = os.environ.get("REDIS_PWD")

# initialize bot and its dispatcher
bot = Bot(token=TOKEN)
scheduler = AsyncIOScheduler(timezone=str(tzlocal.get_localzone()))


loop = asyncio.new_event_loop()
storage = RedisStorage2(host="redis-13310.c264.ap-south-1-1.ec2.cloud.redislabs.com", port=13310, password=password)
dp = Dispatcher(bot, storage=storage, loop=loop)
