
import ast
import asyncio
from datetime import datetime, timedelta, timezone
import difflib
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

simo_word_tuple = (
    'ちんちん','チンチン','ﾁﾝﾁﾝ','ﾁﾝｺ','ﾁﾝｺ','ちんこ','チンコ','ちんぽこ','まんこ','ﾏﾝｺ','うんこ','ｳﾝｺ','ウンコ','マンコ'
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

    
class Tsukineko:
    def set_client(self,c):
        self.client = c
    def get_ch(self,id):
        return self.client.get_channel(id)

tf = Tsukineko()
tf.set_client(client)

def check_per(int):
    num = random.uniform(0, 100)
    return num <= int

def check_samenum(a,n):
    num = 0
    for i in n:
        if i == a:
            num =+ 1
    return num

def is_japanese(string):
    for ch in string:
        name = unicodedata.name(ch) 
        if "CJK UNIFIED" in name \
        or "HIRAGANA" in name \
        or "KATAKANA" in name:
            return True
    return False


flag = True
flag2 = True
talk_flag = True
master_flag = True

talk = Talk()
last_word = ''
feeling_dict = {}
kigen = 0
    
@client.event
async def on_ready():
    global odakenko, guild, nyanlog_ch, user_numlog_ch, msg_count_ch, feeling_dict, talk_flag, kigen
    log_ch = client.get_channel(870264545338347580)
    await log_ch.send('起動準備中…')

    odaneko = client.get_user(odaneko_id)
    guild = client.get_guild(guild_id)
    nyanlog_ch = guild.get_channel(nyanlog_ch_id)
    user_numlog_ch = guild.get_channel(user_numlog_ch_id)
    msg_count_ch = guild.get_channel(msg_count_ch_id)
    
    nyan_ch = client.get_channel(870264545338347580)
    for i in list("........................................"):
        msg = nyan_ch.last_message
        if nyan_ch.last_message:
            if nyan_ch.last_message.author.id == client.user.id:
                try:
                    await nyan_ch.last_message.delete()
                except:
                    pass
                else:
                    pass
            else:
                break
    await log_ch.send('今めっちゃログ読んでるので待ってください(白目)')
    talk_flag = False
    msgs = [ msg for msg in await nyan_ch.history(limit=1000).flatten() if all([not msg.author.bot,msg.content!=''])]
    msg_num = len(msgs)
    readed_msg_num = 0
    reading_msg = await log_ch.send('読破割合:00.00%')
    for msg in msgs:
        num = 0
        for word in ng_word_tuple:
            if word in msg.content:
                num -= 1
        for word in simo_word_tuple:
            if word in msg.content:
                num -= 2
        for word in g_word_tuple:
            if word in msg.content and check_per(50):
                num += 1
        if not msg.author.id in feeling_dict:
            feeling_dict[msg.author.id] = num
        else:
            feeling_dict[msg.author.id] += num
        readed_msg_num += 1
        if (check_per(1) or readed_msg_num==msg_num):
            await reading_msg.edit(content=f"読破割合:{int(readed_msg_num/msg_num*10000)/100}%")
        print(f"{msg.content}")
    await log_ch.send(f'ちょっとずるしましたが、{msg_num}メッセージ読み終わりました。')
    text = ""
    ready_log_ch = client.get_channel(885866610005532672)
    for (i,j) in zip(feeling_dict.keys(),feeling_dict.values()):
        text += f"・ [*{j}*]**{(client.get_user(i)).name}**\n"
    if len(text) < 2000:
        em = discord.Embed(title="好感度リスト",description=text)
        await ready_log_ch.send(embed=em)
    talk_flag = True
    
    kigen = int(random.randint(-10,10))
    
    ch_edit_loop.start()
    await log_ch.send('起動完了')

def nyan_translator(str):
    if check_per(7):
        str = "まぁ、"+str
    if check_per(7):
        str = "うん、"+str
    if check_per(5) and not '/' in str and not '♡' in str:
        str += random.choice(["ฅ^•ω•^ฅ","^ω^）","( ´ ω ` )","(´・ω・｀)","(・ω・)"])
    print("A"+str)
    return str

def nyan_translator2(str,user):
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




usersMsgLogDict = {}

def check_similarly(a,b):
    return difflib.SequenceMatcher(None, a, b).ratio()

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
    global flag2, last_word, feeling_dict, usersMsgLogDict, talk_flag
    global kigen
    
    guild = msg.guild
    
    msg_ctt = msg.content
    msg_ch = msg.channel
    channel = msg_ch
    msg_author = msg.author
    msg_author_id = msg.author.id

    if not msg.author.bot:
        if msg.guild:
            if msg.guild.id == 870264494541135882:
                msg_count += 1

    if (msg_ctt.startswith(prefix)):
        command = msg_ctt.split(prefix)[1]
        
        if (command == "ping"):
            re_tuple = ("にゃ…にゃんぐ…///","はわわ…","にゃん？")
            comment = random.choice(list(re_tuple))
            await msg_ch.send(comment)
        if msg_author.id == 827903603557007390:
            if (command.startswith("set_kigen ")):
                num = command.split("set_kigen ")[1]
                if num.isdigit():
                    num = int(num)
                    kigen = num
                    await msg_author.send(f"kigen = {kigen}")
                else:
                    await msg_author.send(f"数字…")
            if (command.startswith("check_kigen")):
                await msg_author.send(f"kigen = {kigen}")
            if (command.startswith("set_feeling ")):
                id = command.split(" ")[1]
                num = command.split(" ")[2]
                if id.isdigit() and num.isdigit():
                    id = int(id)
                    num = int(num)
                    if id in feeling_dict:
                        feeling_dict[id] = num
                        user = client.get_user(id)
                        await msg_author.send(f"{user} = {feeling_dict[id]}")
                    else:
                        await msg_author.send(f"いない！")
                else:
                    await msg_author.send(f"数字…")
            if (command.startswith("check_feeling ")):
                id = command.split("check_feeling ")[1]
                if id.isdigit():
                    id = int(id)
                    if id in feeling_dict:
                        user = client.get_user(id)
                        await msg_author.send(f"{user} = {feeling_dict[id]}")
                    else:
                        await msg_author.send(f"いない！")
                else:
                    await msg_author.send(f"数字…")
            await msg.delete()
            
            
    if msg_ch.id == 870368104805466192:
        if msg_ctt.isdigit() and check_per(50):
            res = int(msg_ctt) + 1
            count_ch = client.get_channel(870368104805466192)
            await count_ch.send(res)
                
    if all([msg_ctt != "" ,check_per(100), talk_flag]):
        ctt = msg_ctt
        user_id = msg.author.id
        if user_id == client.user.id:
            return
        if not( msg.guild == None or msg_ch.id == 870264545338347580):
            return
        if not flag2 or not is_japanese(ctt):
            return
        if msg_ctt.startswith("(") or msg_ctt.startswith("（"):
            return
        flag2 = False
        if not user_id in usersMsgLogDict:
            usersMsgLogDict[user_id] = ['temp']
        if not msg.author.id in feeling_dict:
            feeling_dict[user_id] = 0
        for word in ng_word_tuple:
            if word in ctt:
                feeling_dict[user_id] = feeling_dict[user_id]-1
                if check_per(15+kigen):
                    kigen -= 1
        for word in g_word_tuple:
            if word in ctt and check_per(50):
                feeling_dict[user_id] = feeling_dict[user_id]+1
            if check_per(15):
                kigen += 1
        kigen = max(min(10,kigen),-15)
        feeling_dict[user_id] = max(min(feeling_dict[user_id],10),-10)
        res = talk.get(msg_ctt)
        feeling_num = feeling_dict[user_id]
        if msg.author.id == 827903603557007390:
            feeling_dict[user_id] = int(random.randint(7,10))
        if check_per(5+feeling_dict[user_id]):
            feeling_dict[user_id] += 1
        if check_per(5-feeling_dict[user_id]):
            feeling_dict[user_id] -= 1

        similarly_list = []
        similarly_result = 0.0
        if len(usersMsgLogDict[user_id]) > 0:
            for i in usersMsgLogDict[user_id]:
                similarly_list.append(check_similarly(i,msg_ctt))
            similarly_result = sum(similarly_list)/len(similarly_list)
        usersMsgLogDict[user_id].append(msg_ctt)
        temp_list = usersMsgLogDict[user_id]
        if len(temp_list) > 3:
            usersMsgLogDict[user_id] = temp_list[1:]
        feeling_num += kigen
        if feeling_num >= -5:
            if user_id == 827903603557007390:
                res = res.replace("あなた", "ご主人様")
            if feeling_num >= 0:
                res = nyan_translator(res)
            if feeling_num >= 2:
                res = nyan_translator2(res,msg.author)
            if feeling_num >= 5:
                res = nyan_translator3(res,msg.author)
            if 'ご主人様は良く' in res:
                res = '(´・ω・｀)'
            if '大丈夫ですか' in res:
                res = "頭"+res
            if 'はよくする' in res:
                res = random.choice([':thinking:','😇','( ˘ω˘ )'])
            if '生きるの' in res:
                res = random.choice(['ｽﾝｯ( ˙꒳​˙  )','( ´•ω•` )','( ˘ω˘ )'])
            if '時計を持って' in res and feeling_num >= 8:
                res = f'**{datetime.now(JST).hour}**時にゃ'
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

            if similarly_result >= 0.5 and len(temp_list) > 2:
                feeling_dict[user_id] -= 3
                res = random.choice(
                    ['(   ¯−¯ )','(   ˙-˙   )','(´-ι_-｀)','(￣･ω･￣)']
                )
            print("af: "+res)
            async with channel.typing():
                if last_word != res:
                    time = int(len(res)/12)+1
                    await asyncio.sleep(time)
                    await msg.reply(res, mention_author=False)
                    last_word = res
                    em = discord.Embed(title=f'{msg.author.name}との会話')
                    em.add_field(name='好感',value=feeling_dict[msg.author.id])
                    em.add_field(name='相手',value=msg_ctt)
                    em.add_field(name='返信',value=res)
                    em.add_field(name='類似性',value=similarly_result)
                    log_ch = client.get_channel(878594409166430259)
                    await log_ch.send(embed=em)
                flag2 = True
            
client.run(token)
