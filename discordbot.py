
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
prefix = 'nyan!'

odaneko_id = 846356637271064627
nyanlog_ch_id = 870331978770157658
guild_id = 870264494541135882
odaneko = client.get_user(odaneko_id)
guild = client.get_guild(guild_id)
nyanlog_ch = guild.get_channel(nyanlog_ch_id)

anti_ch_tuple = (
    870324797291261992,
    870324843751563316,
    870315056397701200,
)

ng_word_tuple = (
    '死ね', 
    '消えろ', 
    'ﾀﾋね'
)

need_word_tuple = (
    'nya', 'Nya',
    'にゃ', 'ニャ', 'ﾆｬ'
)

day_up_id_1 = 870333975141429319
day_up_id_2 = 870334047040204880
day_down_id = 870334141739180082

def get_ch(int):
    ch = guild.get_channel(int)
    return ch

def get_data(ch):
    num = int(ch.name.split('：')[1])
    return num

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
            comment = random.choice(list(re_tuple))
            await msg_ch.send(comment)

    if msg.author.id == odaneko_id:
        if msg.channel.id in anti_ch_tuple:
            return
        num_up1 = get_data(get_ch(day_up_id_1))
        num_up2 = get_data(get_ch(day_up_id_2))
        num_down = get_data(get_ch(day_down_id))
        check = 0
        temp = 0
        for j in need_word_tuple:
            if not i in msg_ctt:
                temp += 1
        if temp >= len(need_word_tuple):
            check += num_up1
        else:
            check -= 1
        for i in ng_word_tuple:
            if i in msg_ctt:
                check += num_up2
        num_result = get_data(nyanlog_ch) + check
        ch_name = f'合計日数：{num_result}'
        nyanlog_ch.edit(name=ch_name)

    else:
        if msg_ctt.startswith(prefix):
            cmd1 = prefix+'add_count'
            if msg_ctt.startswith(cmd1)
                num = int(msg_ctt.split(cmd1)[1])
                if num <= 365:
                    re_text = '増やす量が多すぎるよォ…365より小さくしてね'
                    await msg_ch.send(re_text)
                    return
                num_result = get_data(nyanlog_ch) + num
                ch_name = f'合計日数：{num_result}'
                    nyanlog_ch.edit(name=ch_name)
                re_text = f'{num_result}日になったよ!'
                await msg_ch.semd(re_text)

client.run(token)
