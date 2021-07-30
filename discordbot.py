
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

intents = discord.Intents.default()
intents.members = True
client = discord.Client(intents=intents)
token = os.environ['TOKEN']

developer = client.get_user(827903603557007390)

# 時間軸設定
JST = timezone(timedelta(hours=+9), 'JST')

print("Nyan!!")
prefix = 'nyan!'

odaneko_id = 846356637271064627
#odaneko_id = 827903603557007390
nyanlog_ch_id = 870331978770157658
user_numlog_ch_id = 870332072408002600
guild_id = 870264494541135882

anti_ch_tuple = (
    870324797291261992,
    870324843751563316,
    870315056397701200,
)

ng_word_tuple = (
    '死ね', 
    '消えろ', 
    'ﾀﾋね',
    'だまれ',
    '黙れ',
    '帰れ',
    '消えろ',
    'ふぁっく', 'ファック', 'ﾌｧｯｸ', 'Fuck', 'FUCK', 'fuck'
    'おだまり',
)

need_word_tuple = (
    'nya', 'Nya',
    'にゃ', 'ニャ', 'ﾆｬ'
)
def check_nyan(text):
    temp = 0
    for i in need_word_tuple:
        if not i in text:
            temp += 1
    return temp >= len(need_word_tuple)

day_up_id_1 = 870334047040204880
day_up_id_2 = 870334141739180082
day_down_id = 870333975141429319

def get_ch(int):
    ch = guild.get_channel(int)
    return ch

def get_data(ch):
    num = int(ch.name.split('：')[1])
    return num

NYAN = 0

odaneko = None
guild = None
nyanlog_ch = None
user_numlog_ch = None

@tasks.loop(seconds=10)
async def ch_edit_loop():
    global NYAN
    num_result = get_data(nyanlog_ch) + NYAN
    print(NYAN)
    if NYAN != get_data(nyanlog_ch):
        ch_name = f'合計日数：{num_result}'
        await nyanlog_ch.edit(name=ch_name)
        NYAN = 0
        
    user_num = len(guild.members)
    bot_num = 0
    for i in guild.members:
        if i.bot:
            bot_num += 1
            user_num -= 1
    if user_numlog_ch != None:
        if get_data(user_numlog_ch) != user_num:
            ch_name = f'総合人数：{user_num}'
            await user_numlog_ch.edit(name=ch_name)
    else:
        print("人数記録チャンネルがない！")

@client.event
async def on_ready():
    global odakenko, guild, nyanlog_ch, user_numlog_ch
    odaneko = client.get_user(odaneko_id)
    guild = client.get_guild(guild_id)
    nyanlog_ch = guild.get_channel(nyanlog_ch_id)
    user_numlog_ch = guild.get_channel(user_numlog_ch_id)
    
    ch_edit_loop.start()
    print("Nyan!!")
    
flag = True

nyan_checking_members_id = []

    
@client.event
async def on_message(msg):
    global NYAN
    global flag
    global odaneko_id
    
    msg_ctt = msg.content
    msg_ch = msg.channel
    msg_author_id = msg.author.id
    
    if (msg_ctt.startswith(prefix)):
        command = msg_ctt.split(prefix)[1]
        
        if (command == "ping"):
            re_tuple = ("にゃ…にゃんぐ…///","はわわ…","にゃん？")
            comment = random.choice(list(re_tuple))
            await msg_ch.send(comment)
            
    nyan_members_id = [ i.id for i in guild.get_role(870538137649152010).members ]
    if msg_author_id in nyan_members_id and msg_ctt != "" and msg_author_id != odaneko_id:
        if not msg_author_id in nyan_checking_members_id:
            nyan_checking_members_id.append(msg_author_id)
            num_up1 = get_data(get_ch(day_up_id_1))
            num_up2 = get_data(get_ch(day_up_id_2))
            num_down = get_data(get_ch(day_down_id))
            check = 0
            if check_nyan(msg_ctt):
                def check_nyan_try2(m):
                    if m.author.id != msg.author.id:
                        return 0
                    if m.channel.id != msg_ch.id:
                        return 0
                    if check_nyan(m.content):
                        return 0
                    return 1
                try:
                    msd2 = await client.wait_for("message", timeout=3, check=check_nyan_try2)
                except asyncio.TimeoutError:
                    check += num_up1
                    await msg_ch.send(f'**{msg.author}**さん、にゃん！')
                else:
                    await msg_ch.send(f'セーフ！\nあと少し遅かったら加算だったにゃん！')
            else:
                check -= 1
            member = guild.get_member(msg.author.id)
            nick = member.nick
            if not nick:
                nick = member.name
            if not "｜NyanCount:" in nick:
                await member.edit(nick=nick+"｜NyanCount:0")
                nick = member.name
            count = nick.split("｜NyanCount:")[1]
            nick_left = nick.nick.split("｜NyanCount:")[0]
            if (day).isdigit() == False:
                await member.edit(nick=member.name+"｜NyanCount:0")
            count = int(day)
            count += check
            await member.edit(nick=nick_left+f'｜NyanCount:{count}')
            checking_members_id.remove(msg_author_id)
            
            
            

    if msg.author.id == odaneko_id and flag == True and msg_ctt != "":
        if msg.channel.id in anti_ch_tuple:
            return
        flag = False
        print(f'メッセージを取得：{msg_ctt}')
        num_up1 = get_data(get_ch(day_up_id_1))
        num_up2 = get_data(get_ch(day_up_id_2))
        num_down = get_data(get_ch(day_down_id))
        check = 0
        if check_nyan(msg_ctt):

            def check_nyan_try(m):
                if m.author.id != odaneko_id:
                    return 0
                if m.channel.id != msg_ch.id:
                    return 0
                if check_nyan(m.content):
                    return 0
                return 1
            try:
                msd2 = await client.wait_for("message", timeout=3, check=check_nyan_try)
            except asyncio.TimeoutError:
                check += num_up1
                await msg_ch.send('あの…**にゃん**が付いて無いです…')
            else:
                await msg_ch.send('ちゃんと**にゃん**がつけれてえらいです！')
                await asyncio.sleep(1)
                await msg_ch.send('いいこいいこ♪')
        else:
            check -= 1
        for i in ng_word_tuple:
            if i in msg_ctt:
                check += num_up2
                await msg_ch.send(f'**{i}**なんて言う人…嫌いです…！')
        NYAN += check
        flag = True

    else:
        if msg_ctt.startswith(prefix):
            cmd1 = prefix+'add_count '
            if msg_ctt.startswith(cmd1):
                num = int(msg_ctt.split(cmd1)[1])
                if num <= 365:
                    re_text = '増やす量が多すぎるよォ…365より小さくしてね'
                    await msg_ch.send(re_text)
                    return
                num_result = get_data(nyanlog_ch) + num
                ch_name = f'合計日数：{num_result}'
                await nyanlog_ch.edit(name=ch_name)
                re_text = f'{num_result}日になったよ!'
                await msg_ch.semd(re_text)
                
            cmd2 = prefix+'set_user '
            if msg_ctt.startswith(cmd2):
                re_text = ""
                if (msg_ctt.split(cmd2)[1]).isdigit():
                    id = int(msg_ctt.split(cmd2)[1])
                    user = guild.get_member(id)
                    if user:
                        re_text = f'{user.mention}をみはるにゃん(=^・・^=)'
                        odaineko_id = id
                    else:
                        re_text = f'**{id}**って人が見つからなかったにゃん…'
                else:
                    re_text = f'**{msg_ctt.split(cmd2)[1]}**は絶対USER_IDじゃないにゃん…\n`nyan!set_user USER_ID`でセットできるにゃん！'

client.run(token)
