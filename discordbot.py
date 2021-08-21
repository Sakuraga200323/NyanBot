
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
import unicodedata

import discord
from discord.ext import tasks, commands


import requests
import json

class Talk:
    def __init__(self):
        self.key = os.environ['TALKAPI-KEY']
        self.api = 'https://api.a3rt.recruit-tech.co.jp/talk/v1/smalltalk'

    def get(self,talking):
        url = self.api
        r = requests.post(url,{'apikey':self.key,'query':talking})
        data = json.loads(r.text)
        if data['status'] == 0:
            t = data['results']
            ret = t[0]['reply']
        else:
            ret = '…にゃん'
        return ret


intents=discord.Intents.all()
client = discord.Client(intents=intents)
token = os.environ['TOKEN']

developer = client.get_user(827903603557007390)

# 時間軸設定
JST = timezone(timedelta(hours=+9), 'JST')

print("Nyan!!")
prefix = 'nyan!'

msg_delete_num = 5

odaneko_id = 846356637271064627
#odaneko_id = 827903603557007390
nyanlog_ch_id = 870331978770157658
msg_count_ch_id = 877010466109554748
user_numlog_ch_id = 870332072408002600
guild_id = 870264494541135882

anti_ch_tuple = (
    870324797291261992,
    870324843751563316,
    870315056397701200,
)

ng_word_tuple = (
    '死ね', 'ﾀﾋね','消えろ', 'だまれ', '黙れ', 'ダマレ', 'ﾀﾞﾏﾚ', 'だまって',
    '消えろ', 'キエロ','きえろ','ｷｴﾛ','ふぁっく', 'ファック', 'ﾌｧｯｸ', 'Fuck', 'FUCK', 'fuck',
    'おだまり','おまえ','アホ','ボケ','カス','ハゲ','デブ','チビ','クソ','ぶさいく','ばばあ','きもい','くさい','のろま','無能'
)

g_word_tuple = (
    "可愛い","かわいい","カワイイ","ｶﾜｲｲ",
    "好き","すき","スキ","ｽｷ","愛してる","アイシテル","ｱｲｼﾃﾙ","あいしてる",
    "頑張","がんば","ガンバ","ｶﾞﾝﾊ",
    "流石","さすが","サスガ","ｻｽｶﾞ",
    "優し","やさしい","ヤサシイ","ﾔｻｼｲ",
    "楽し","たのし","タノシ","ﾀﾉｼ",
    "癒","美人","おしゃれ",
    "凄","すご","スゴ","ｽｺﾞ",
    "尊敬する","そんけいする","ソンケイする","ｿﾝｹｲする",
    "ありがとう","有難う","アリガトウ","ｱﾘｶﾞﾄｳ",
    "おはよう","こんにちは","こんばんは","お早う",
    "オハヨウ","ｵﾊﾖｳ","今日は","ｺﾝﾆﾁﾊ","コンニチハ",
    "こんばんは","今晩は","コンバンハ","嬉しい","ごめんね","ゴメンね"
)

need_word_tuple = (
    'nya', 'Nya', 'NYA',
    'にゃ', 'ニャ', 'ﾆｬ'
)

damare_count = 0
damarer = []

def check_nyan(text):
    temp = 0
    for i in need_word_tuple:
        if not i in text:
            temp += 1
    return temp < len(need_word_tuple)

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
msg_count = 0

odaneko = None
guild = None
nyanlog_ch = None
user_numlog_ch = None
msg_count_ch = None

@tasks.loop(seconds=10)
async def ch_edit_loop():
    global NYAN
    global msg_count
    if msg_count > 0:
        num_result = get_data(msg_count_ch) + msg_count
        ch_name = f'総発言数：{num_result}'
        await msg_count_ch.edit(name=ch_name)
        msg_count = 0
        
        
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
    member = guild.get_member(client.user.id)
    await member.edit(nick='汎用自己学習型会話AI ≪雪猫≫')

@client.event
async def on_ready():
    global odakenko, guild, nyanlog_ch, user_numlog_ch, msg_count_ch
    odaneko = client.get_user(odaneko_id)
    guild = client.get_guild(guild_id)
    nyanlog_ch = guild.get_channel(nyanlog_ch_id)
    user_numlog_ch = guild.get_channel(user_numlog_ch_id)
    msg_count_ch = guild.get_channel(msg_count_ch_id)
    
    ch_edit_loop.start()
    log_ch = client.get_channel(870264545338347580)
    await log_ch.send('起動したにゃ!\n皆の事は忘れちゃったけど…またお話してくれると嬉しいにゃ(=^･ω･^=)')
    
flag = True
master_flag = True
flag2 = True

nyan_checking_members_id = []

talk = Talk()
last_word = ''
feeling_dict = {}

def check_per(int):
    num = random.uniform(0, 100)
    return num <= int

def check_samenum(a,n):
    num = 0
    for i in n:
        if i == a:
            num =+ 1
    return num

def nyan_translator(str):
    if check_per(5) and not '/' in str and not '♡' in str:
        str += random.choice(["ฅ^•ω•^ฅ","^ω^）","( ´ ω ` )","(´・ω・｀)","(・ω・)"])
    print("A"+str)
    return str

def nyan_translator2(str):
    replace_tuple = (
        ("ですね","にゃ"),
        ("ですよ","にゃ"),
        ("です","にゃ"),
        ("ます","ますにゃ"),
        ("ました","ましたにゃん"),
        ("ますよ","ますにゃん"),
        ("ね","にゃ"),
        ("か?","かにゃん?"),
        ('私','にゃー'),
        ('な','にゃ'),
        ('ありがとうございます',random.choice(['ありがとにゃん','ありがとうございますにゃん'])),
        ("下さい","下さいにゃ"),
        ("ください","くださいにゃ"),
        ("ません","ませんにゃ……"),
        ("行","イ"),
        ('はい','にゃん、'),
    )
    str = str.replace('あなた', user.name+"さん")
    for i in replace_tuple:
        str = str.replace(i[0],i[1])
    print("B"+str)
    return str

def nyan_translator3(str, user):
    if check_per(5):
        str += '…///'
    if check_per(5):
        str += '♡'
    if check_per(5) and not '/' in str and not '♡' in str:
        str += '♪'
    if check_per(5) and not '/' in str and not '♡' in str:
        str += '!'
    if check_per(50):
        str = str.replace("秘密"," ひ・み・つ ")
    print("C"+str)
    return str

def is_japanese(string):
    for ch in string:
        name = unicodedata.name(ch) 
        if "CJK UNIFIED" in name \
        or "HIRAGANA" in name \
        or "KATAKANA" in name:
            return True
    return False

@client.event
async def on_message(msg):
    global NYAN
    global flag
    global odaneko_id
    global nyan_checking_members_id
    global master_flag
    global damare_count
    global damarer
    global msg_count
    global flag2, last_word, feeling_dict
    
    guild = msg.guild
    
    msg_ctt = msg.content
    msg_ch = msg.channel
    channel = msg_ch
    msg_author_id = msg.author.id

    if not msg.author.bot and msg.guild.id == 870264494541135882 and not msg.author.id != client.user.id:
        msg_count += 1

    if (msg_ctt.startswith(prefix)):
        command = msg_ctt.split(prefix)[1]

        if (command == " ping"):
            re_tuple = ("にゃ…にゃんぐ…///","はわわ…","にゃん？")
            comment = random.choice(list(re_tuple))
            await msg_ch.send(comment)

    if msg_ch.id == 870368104805466192:
        if msg_ctt.isdigit() and check_per(50):
            res = int(msg_ctt) + 1
            count_ch = client.get_channel(870368104805466192)
            await count_ch.send(res)
                
    if (msg_ctt != "" ,check_per(100)) == (True, True):
        ctt = msg_ctt
        if msg.author.id == client.user.id:
            return
        if not( msg.guild == None or msg_ch.id == 870264545338347580):
            return
        if not flag2:
            return
        if not is_japanese(ctt):
            return
        if msg_ctt.startswith("(") or msg_ctt.startswith("（"):
            return
        async with channel.typing():
            flag2 = False
            if not msg.author.id in feeling_dict:
                    feeling_dict[msg.author.id] = 0
            for word in ng_word_tuple:
                if word in ctt:
                    feeling_dict[msg.author.id] = feeling_dict[msg.author.id]-1
            for word in g_word_tuple:
                if word in ctt and check_per(50):
                    feeling_dict[msg.author.id] = feeling_dict[msg.author.id]+1
            feeling_dict[msg.author.id] = max(min(feeling_dict[msg.author.id],10),-10)
            res = talk.get(msg_ctt)
            feeling_num = feeling_dict[msg.author.id]
            if msg.author.id == 827903603557007390:
                feeling_dict[msg.author.id] = 10
            if check_per(5+feeling_dict[msg.author.id]):
                feeling_dict[msg.author.id] += 1
            if check_per(5-feeling_dict[msg.author.id]):
                feeling_dict[msg.author.id] -= 1
            print("好感度: "+msg.author.name+"｜"+str(feeling_dict[msg.author.id]))
            print("be: "+res)
            if feeling_num >= -5:
                if msg.author.id == 827903603557007390:
                    res = res.replace("あなた", "ご主人様")
                if feeling_num >= 0:
                    res = nyan_translator(res)
                if feeling_num >= 2:
                    res = nyan_translator2(res)
                if feeling_num >= 5:
                    res = nyan_translator3(res,msg.author)
                if  'ご主人様は良く' in res:
                    res = '(´・ω・｀)'
                if '時計を持って' in res and feeling_num >= 8:
                    res = f'時計買ったので分かるにゃ、**{datetime.now(JST).hour}**時にゃ'
                simo_check_tuple = (
                    'ちんちん','チンチン','ﾁﾝﾁﾝ','ﾁﾝｺ','ﾁﾝｺ','ちんこ','チンコ','ちんぽこ','まんこ','ﾏﾝｺ','うんこ','ｳﾝｺ','ウンコ','マンコ'
                )
                simo_check = 0
                for i in simo_check_tuple:
                    if i in msg_ctt:
                        simo_check += 1
                if simo_check > 0:
                    res = random.choice(
                        ['( ˘•ω•˘ )','( ´•ω•｀)','(   ˙-˙   )','(｡•́ - •̀｡)','(  ´0ω0`)']
                    )
                    feeling_dict[msg.author.id] -= simo_check
                print("af: "+res)
                if last_word != res:
                    await asyncio.sleep(int(len(res)/5)+1)
                    await msg_ch.send(f">{msg.author.name}\n"+res)
                    last_word = res
                    em = discord.Embed(title=f'{msg.author.name}との会話')
                    em.add_field(name='好感',value=feeling_dict[msg.author.id])
                    em.add_field(name='相手',value=msg_ctt)
                    em.add_field(name='返信',value=res)
                    log_ch = client.get_channel(878594409166430259)
                    await log_ch.send(embed=em)
            flag2 = True
            




        if msg_ctt.startswith(prefix):

            if msg_ch.id == 870266562018426921:
                if msg_ctt.startswith('nyan!trade "'):
                    de = msg_ctt.split('"')[1]
                    q = msg_ctt.split('"')[3]
                    plus_a = msg_ctt.split('"')[5]
                    embed = discord.Embed(title=f'{msg.author.name}さんの取引です')
                    embed.add_field(name="**出**", value=de)
                    embed.add_field(name="**求**", value=q)
                    embed.add_field(name="**追記**", value=plus_a)
                    async with channel.typing():
                        # simulate something heavy
                        await asyncio.sleep(2)
                    await msg_ch.send(embed=embed)
                    await asyncio.sleep(5)
                    await msg.delete()

client.run(token)
