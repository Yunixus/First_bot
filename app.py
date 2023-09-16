import asyncio
import logging
import os.path
import time
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from uploader import pyrogram_client, send_message_to_group
from logging.handlers import TimedRotatingFileHandler
from apscheduler.schedulers.asyncio import AsyncIOScheduler



if not os.path.exists("logs"):
    os.makedirs("logs")


logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.WARNING,
    handlers=[
        TimedRotatingFileHandler(
            "logs/userbot.log",
            when="midnight",
            encoding=None,
            delay=False,
            backupCount=10,
        ),
        logging.StreamHandler(),
    ],
)
LOGS = logging.getLogger(__name__)

if __name__ == '__main__':
    scheduler = AsyncIOScheduler()
    scheduler.add_job(send_message_to_group, "interval", seconds=3600)
    scheduler.start()
    pyrogram_client.run()
