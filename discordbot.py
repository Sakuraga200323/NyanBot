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
    "好き","すき","スキ","ｽｷ",
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
    "こんばんは","今晩は","コンバンハ","嬉しい",
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
    await member.edit(nick='にゃー!')

@client.event
async def on_ready():
    global odakenko, guild, nyanlog_ch, user_numlog_ch, msg_count_ch
    odaneko = client.get_user(odaneko_id)
    guild = client.get_guild(guild_id)
    nyanlog_ch = guild.get_channel(nyanlog_ch_id)
    user_numlog_ch = guild.get_channel(user_numlog_ch_id)
    msg_count_ch = guild.get_channel(msg_count_ch_id)
    
    ch_edit_loop.start()
    print("Nyan!!")
    
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
        ("ね","にゃ"),
        ("か?","かにゃん?"),
        ('私','にゃー'),
        ('な','にゃ'),
        ('ありがとうございます',random.choice(['ありがとにゃん','ありがとうございますにゃん'])),
        ("下さい","下さいにゃ"),
        ("ください","くださいにゃ"),
        ("わかりません","わかりませんにゃ……"),
        ("行","イ"),
    )
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
    str = str.replace('あなた', user.name+"さん")
    print("C"+str)
    return str
    
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

    if not msg.author.bot:
        msg_count += 1

    if msg.author.id == 827903603557007390:
        if msg_ctt == "Nyan、ちょっとだまって":
            async with channel.typing():
                # simulate something heavy
                await asyncio.sleep(2)
            await msg_ch.send('にゃぁ…')
            master_flag = False
        if msg_ctt == "Nyan、話していいよ":
            async with channel.typing():
                # simulate something heavy
                await asyncio.sleep(2)
            await msg_ch.send('にゃぁ！！')
            master_flag = True

    if msg_ctt == "nyan! stop" and damare_count < 3:
        if msg.author.id in damarer:
            async with channel.typing():
                # simulate something heavy
                await asyncio.sleep(msg_delete_num3)
                await msg_ch.send(f'{msg.author.mention}さんはすでに黙れ申請をしてるにゃ')
        else:
            damarer.append(msg.author.id)
            damare_count += 1
            async with channel.typing():
                await msg_ch.send(f'{msg.author.mention}さんの黙れ申請を受理したにゃ')
                if damare_count < 3:
                    # simulate something heavy
                    await msg_ch.send(f'あと{3-damare_count}人でだまるにゃ…')
                elif damare_count == 3:
                    msg_list = (
                        'みんなそんなに黙ってほしーにゃか…',
                        '3人に黙れって言われたから、明日まで黙るにゃ',
                        'そんなに黙ってほしいなら黙るにゃ',
                        'みんなにゃーのこときらいにゃのにゃ…'
                    )
                    await msg_ch.send(random.choice(msg_list))
                    master_flag = False

    if (msg_ctt.startswith(prefix)):
        command = msg_ctt.split(prefix)[1]

        if (command == " ping"):
            re_tuple = ("にゃ…にゃんぐ…///","はわわ…","にゃん？")
            comment = random.choice(list(re_tuple))
            await msg_ch.send(comment)
                

    if master_flag == True and msg.guild != None:
        if (not msg.author.id in (odaneko_id, client.user.id) and not msg.author.bot):
            """
            for i in ng_word_tuple:
                if i in msg_ctt:
                    re_text_tuple = (
                        f'**{i}**なんていう人きらいにゃ！',
                        f'なんで**{i}**なんていうにゃ…',
                        f'言葉は時として相手を傷つけるにゃ。\n**{i}**なんていい例にゃ',
                        f'**{i}**は決していいことばじゃにゃーよ…',
                    )
                    re_text = random.choice(re_text_tuple)
                    temp = await msg_ch.send(re_text)
            """

        nyan_members_id = [ i.id for i in guild.get_role(870538137649152010).members ]
        if msg_author_id in nyan_members_id and msg_ctt != "":
            if not msg_author_id in nyan_checking_members_id:
                nyan_checking_members_id.append(msg_author_id)
                num_down1 = get_data(get_ch(day_up_id_1))
                num_down2 = get_data(get_ch(day_up_id_2))
                num_up = get_data(get_ch(day_down_id))
                check = 0
                if not check_nyan(msg_ctt):
                    async with channel.typing():
                        re_text = ""
                        def check_nyan_try2(m):
                            if m.author.id != msg.author.id:
                                return 0
                            if m.channel.id != msg_ch.id:
                                return 0
                            if not check_nyan(m.content):
                                return 0
                            return 1
                        try:
                            msd2 = await client.wait_for("message", timeout=5, check=check_nyan_try2)
                        except asyncio.TimeoutError:
                            check -= num_down1
                            re_text_tuple = (
                                f'**{msg.author}**さん、にゃん！',
                                f'**{msg.author}**さん猫語忘れてるにゃ～',
                                f'**{msg.author}**さんは猫語でしゃべらないとにゃ！',
                                f'**{msg.author}**さん、猫語！',
                                f'**{msg.author}**さん、あなたそれでも猫にゃ！？',
                            )
                            re_text = random.choice(re_text_tuple)
                        else:
                            re_text = f'セーフ！\nあと少し遅かったらマイナスだったにゃん！'
                    await msg_ch.send(re_text,delete_after=msg_delete_num)
                else:
                    check += num_up
                member = guild.get_member(msg.author.id)
                nick = member.nick
                if not nick:
                    nick = member.name
                if not "｜NyanCount:" in nick:
                    await member.edit(nick=nick+"｜NyanCount:0")
                    nick = member.name
                temp_list = nick.split("｜NyanCount:")
                nick_left = temp_list[0]
                if len(temp_list) == 2:
                    count = temp_list[1]
                else:
                    count = 0
                if not (str(count)).isdigit():
                    await member.edit(nick=member.name+"｜NyanCount:0")
                count = int(count)
                count += check
                await member.edit(nick=nick_left+f'｜NyanCount:{count}')
                nyan_checking_members_id.remove(msg_author_id)


    if (msg_ctt != "" ,check_per(90)) == (True, True):
        if msg.author.id == client.user.id:
            return
        if not( msg.guild == None or msg_ch.id == 870264545338347580):
            return
        if not flag2:
            return
        ctt = msg_ctt
        async with channel.typing():
            flag2 = False
            if not msg.author.id in feeling_dict:
                    feeling_dict[msg.author.id] = 0
            for word in ng_word_tuple:
                if word in ctt:
                    feeling_dict[msg.author.id] = feeling_dict[msg.author.id]-1
            for word in g_word_tuple:
                if word in ctt:
                    feeling_dict[msg.author.id] = feeling_dict[msg.author.id]+1
            feeling_dict[msg.author.id] = max(min(feeling_dict[msg.author.id],10),-10)
            res = talk.get(msg_ctt)
            feeling_num = feeling_dict[msg.author.id]
            if msg.author.id == 827903603557007390:
                feeling_dict[msg.author.id] = 10
            print("好感度: "+msg.author.name+"｜"+str(feeling_dict[msg.author.id]))
            print("be: "+res)
            if feeling_num >= 0:
                if msg.author.id == 827903603557007390:
                    res = res.replace("あなた", "ご主人様")
                if feeling_num >= 0:
                    res = nyan_translator(res)
                if feeling_num >= 2:
                    res = nyan_translator2(res)
                if feeling_num >= 5:
                    res = nyan_translator3(res,msg.author)
                if res == 'ご主人様は良くするんですかにゃん?':
                    res = '(´・ω・｀)'
                if res == 'ごめんにゃさい今時計を持っていにゃいのでわかりません':
                    res = f'時計買ったので分かるにゃ、**{datetime.now().hours}**時にゃ'
                print("af: "+res)
                if last_word != res:
                    await asyncio.sleep(int(len(res)/4))
                    await msg_ch.send(f">{msg.author.name}\n"+res)
                    last_word = res
                    if check_per(5):
                        feeling_dict[msg.author.id] += 1
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
