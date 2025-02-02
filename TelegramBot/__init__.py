import sys
import time
from asyncio import get_event_loop, new_event_loop, set_event_loop
import uvloop
import requests

from pyrogram import Client
from TelegramBot.config import *
from TelegramBot.logging import LOGGER
from apscheduler.schedulers.asyncio import AsyncIOScheduler

uvloop.install()
LOGGER(__name__).info("Starting TelegramBot....")
BotStartTime = time.time()


# Checking Python version.
if sys.version_info[0] < 3 or sys.version_info[1] < 8:
    LOGGER(__name__).critical(
        """
=============================================================
You MUST need to be on python 3.8 or above, shutting down the bot...
=============================================================
"""
    )
    sys.exit(1)


LOGGER(__name__).info("setting up event loop....")
try:
    loop = get_event_loop()
except RuntimeError:
    set_event_loop(new_event_loop())
    loop = get_event_loop()


LOGGER(__name__).info(
    r"""
____________________________________________________________________
|  _______   _                                ____        _        |
| |__   __| | |                              |  _ \      | |       |
|    | | ___| | ___  __ _ _ __ __ _ _ __ ___ | |_) | ___ | |_      |
|    | |/ _ \ |/ _ \/ _` | '__/ _` | '_ ` _ \|  _ < / _ \| __|     |
|    | |  __/ |  __/ (_| | | | (_| | | | | | | |_) | (_) | |_      |
|    |_|\___|_|\___|\__, |_|  \__,_|_| |_| |_|____/ \___/ \__|     |
|                    __/ |                                         |
|__________________________________________________________________|
""")


# Checking Sabnzbd configs.
LOGGER(__name__).info("Checking SABnzbd configs....")
if SAB_IP and SAB_PORT:
    SABNZBD_ENDPOINT = f"http://{SAB_IP}:{SAB_PORT}/sabnzbd/api?apikey={SAB_API_KEY}"
else:
    SABNZBD_ENDPOINT = f"https://sab-shizuku.itssoap.ninja/sabnzbd/api?apikey={SAB_API_KEY}"
try:
    response = requests.get(SABNZBD_ENDPOINT, timeout=3)
    response.raise_for_status()
except:
    LOGGER(__name__).critical(
        "Can not establish a successful connection with SABnzbd. Please double-check your configs and try again later.")
    sys.exit(1)


# Checking NZBHydra configs.
LOGGER(__name__).info("Checking NZBHydra configs....")
if HYDRA_IP and HYDRA_PORT:
    NZB_URL = f"http://{HYDRA_IP}:{HYDRA_PORT}"
else:
    NZB_URL = "https://nzbhydra-shizuku.itssoap.ninja" 
    
NZBHYDRA_ENDPOINT = f"{NZB_URL}/api?apikey={HYDRA_API_KEY}"
NZBHYDRA_URL_ENDPOINT = (
    f"{NZB_URL}/getnzb/api/replace_id?apikey={HYDRA_API_KEY}")
NZBHYDRA_STATS_ENDPOINT = (
    f"{NZB_URL}/api/stats?apikey={HYDRA_API_KEY}")
try:
    response = requests.get(NZBHYDRA_ENDPOINT, timeout=10)
    response.raise_for_status()
    if "Wrong api key" in response.text:
        raise ValueError("Wrong API value in configs.")
except Exception as error:
    print(error)
    LOGGER(__name__).critical(
        "Can not establish a successful connection with NZBHydra. Please double-check your configs and try again later.")
    sys.exit(1)


# Starting Apscheduler
LOGGER(__name__).info("Starting Apscheduler...")
scheduler = AsyncIOScheduler()
scheduler.start()


# starting the client
LOGGER(__name__).info("initiating the client....")
plugins = dict(root="TelegramBot/plugins")
bot = Client(
    "UsenetBot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN,
    plugins=plugins)
