
import ast
import asyncio
from datetime import datetime, timedelta, timezone
import math
import os
import random
import re
import signal
import sys
import traceback

import discord
from discord.ext import tasks, commands

client = discord.Client(intents=discord.Intents.all())
token = os.environ['TOKEN']

developer = client.get_user(827903603557007390)

# 時間軸設定
JST = timezone(timedelta(hours=+9), 'JST')

print("Nyan!!")

prefix = "nyan!"

@tasks.loop(seconds=60)
async def ch_edit_loop():
    pass

@client.event
async def on_ready():
    ch_edit_loop.start()
    print("Ready!!")
    
@client.event
async def on_message(msg):
    msg_ctt = msg.content
    msg_ch = msg.channel
    
    if (msg_ctt.startswith(prefix)):
        command = msg_ctt.split(prefix)[1]
        
        if (command == "ping"):
            re_tuple = ("にゃ…にゃんぐ…///","はわわ…","にゃん？")
            comment = random.choice(re_tuple)
            await msg_ch.send(comment)

client.run(token)
