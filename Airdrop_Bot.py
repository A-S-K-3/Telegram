'''# -*- coding: future_fstrings -*-'''

# # coding=utf-8

import telepot,telepot.loop,telepot.namedtuple
import pprint,json,time,os,threading,requests,random,collections
import sqlite3

db_exists=os.path.exists("database.db")
conn=sqlite3.connect("database.db", check_same_thread=False)
if not db_exists:
    cur=conn.cursor()
    cur.execute("CREATE TABLE user (id INT, referredby INT, firstname VARCHAR(50), username VARCHAR(50), twitter VARCHAR(128), wallet VARCHAR(128))")
    #tomochain wallet
    conn.commit()
    del cur

WELCOME="""Hi {} , 

I am your friendly ??? Airdrop bot.

- Follow these simple tasks and earn 50 ???

<b>Follow the below steps : </b>

🔸 Join Our <a href="http://t.me/airdrop_tester123">Telegram Group</a>
🔸 Join Our <a href="http://t.me/airdrop_tester12">Telegram Channel</a>
🔸 Follow our <a href="http://twitter.com/telegram">Twitter</a>
🔸 Submit your Details 👍 

✅ Get an extra 15 ??? by using your referral link to invite your friends !"""

main_menu=telepot.namedtuple.ReplyKeyboardMarkup(
    keyboard=[
        [telepot.namedtuple.KeyboardButton(text="💰 My Balance")],
        [telepot.namedtuple.KeyboardButton(text="🔄 Resubmit my details")]
    ],
    resize_keyboard=True
)

bot=telepot.Bot("1232088569:AAH6WGq4BbMn0X6uInTWlzZ2dofhuwsq77w")
step={}
captcha={}

def convertUnicodeDict(data):
    if isinstance(data, basestring):
        return data.encode('utf-8')
    elif isinstance(data, collections.Mapping):
        return dict(map(convertUnicodeDict, data.iteritems()))
    elif isinstance(data, collections.Iterable):
        return type(data)(map(convertUnicodeDict, data))
    else:
        return data

def handle(msg):
    #msg=convertUnicodeDict(msg)
    cur=conn.cursor()
    pprint.pprint(msg)
    userid=msg["from"]["id"]
    firstname=msg['from']['first_name']
    username="None"
    try:
        username="@"+msg['from']['username']
    except:
        pass
    if "data" in msg.keys():
        if msg["data"]=="StartTask":
            menu=telepot.namedtuple.InlineKeyboardMarkup(
                inline_keyboard=[
                    [telepot.namedtuple.InlineKeyboardButton(text="Join Telegram Group",url="https://t.me/airdrop_tester123")],
                    [telepot.namedtuple.InlineKeyboardButton(text="Join Telegram Channel",url="https://t.me/airdrop_tester12")],
                    [telepot.namedtuple.InlineKeyboardButton(text="⏩ Proceed",callback_data="Step2")]
                ]
            )
            bot.sendMessage(userid,"▶️<b> Step ( 1/3 )</b>\n\nClick the button below to join our telegram community and then click the ' ⏩ Proceed ' button to continue !",reply_markup=menu,parse_mode="html",disable_web_page_preview=True)
            return
        if msg["data"]=="Step2":
            if bot.getChatMember("@airdrop_tester123",userid)["status"]=="left" or bot.getChatMember("@airdrop_tester12",userid)["status"]=="left":
                bot.answerCallbackQuery(msg["id"],"You have not finished this task!")
                return
            bot.sendMessage(userid,"▶️ <b>Step ( 2/3 )</b>\n\nFollow <a href='https://twitter.com/telegram'>Twitter</a> and then submit your twitter username (eg @telegram)",parse_mode="html",disable_web_page_preview=True)
            step[userid]=3
            return
    text=msg["text"]

    if text.startswith("/start"):
        cur.execute(f"SELECT * FROM user WHERE id={userid}")
        d=cur.fetchall()
        if len(d)==0 or d[0][4]=="None":
            d=text.split(" ")
            referredby=-1
            if len(d)==2:
                referredby=d[1]
                cur.execute(f"SELECT id FROM user WHERE id={referredby}")
                if len(cur.fetchall())==0:
                    referredby=-1
            cur.execute(f"INSERT INTO user VALUES ({userid},{referredby},'{firstname}','{username}','None','None')")
            conn.commit()
            a=random.randint(30,60)
            b=random.randint(6,15)
            captcha[userid]=a+b
            step[userid]=1
            bot.sendMessage(userid,f"In order to continue, please answer the following mathematical question — \n<b>{a} + {b}</b>:",parse_mode="html",disable_web_page_preview=True)
        else:
            cur.execute(f"SELECT id FROM user WHERE referredby={userid}")
            cnt=len(cur.fetchall())
            bot.sendMessage(userid,f"💰 Airdrop Balance : {cnt*15+50} ???\n\n🚹 Ref. Link : https://t.me/Airdrop_tester123_bot?start={userid}\n⚡️Total Referred : {cnt} Person\n\nRefer friends to earn upto 15 ???",reply_markup=main_menu,disable_web_page_preview=True)
    
    elif text=="🔄 Resubmit my details":
        menu =telepot.namedtuple.InlineKeyboardMarkup(
            inline_keyboard=[
                [telepot.namedtuple.InlineKeyboardButton(text="▶️ Start Task",callback_data="StartTask")]
            ]
        )
        bot.sendMessage(userid,WELCOME.format(firstname),parse_mode="html",reply_markup=menu,disable_web_page_preview=True)
        return

    elif text=="💰 My Balance":
        cur.execute(f"SELECT id FROM user WHERE referredby={userid}")
        cnt=len(cur.fetchall())
        bot.sendMessage(userid,f"💰 Airdrop Balance : {cnt*15+50} ???\n\n🚹 Ref. Link : https://t.me/Airdrop_tester123_bot?start={userid}\n⚡️Total Referred : {cnt} Person\n\nRefer friends to earn upto 15 ???",reply_markup=main_menu,disable_web_page_preview=True)

    elif text=="/export" and (userid==1185742601 or userid==1292474148):
        cur.execute(f"SELECT * FROM user")
        d=cur.fetchall()
        f=open("data.csv","w")
        f.write("id, referredby, firstname, username, twitter, wallet, balance, includedReferralBalance\n")
        for dd in d:
            f.write("u")
            uid=dd[0]
            for ddd in dd:
                if type(ddd)==unicode:
                    ddd=ddd.encode("utf-8")
                f.write(f"{ddd};")
            cur.execute(f"SELECT id FROM user WHERE referredby={uid}")
            d=cur.fetchall()
            cnt=len(d)
            f.write(f"{50+cnt*15};{cnt*15}")
            f.write("\n")
        f.close()
        bot.sendDocument(userid,open("data.csv","rb"))

    elif text.startswith("/broadcast") and (userid==1185742601 or userid==1292474148):
        txt=text.replace("/broadcast ","")
        cur.execute(f"SELECT id FROM user")
        d=cur.fetchall()
        for dd in d:
            try:
                bot.sendMessage(dd[0],txt,parse_mode="html")
            except:
                pass
            time.sleep(0.05)

    else:
        if userid in step.keys():
            if step[userid]==1 and userid in captcha.keys():
                d=None
                try:
                    d=int(text)
                except:
                    a=random.randint(30,60)
                    b=random.randint(6,15)
                    captcha[userid]=a+b
                    bot.sendMessage(userid,f"Invalid answer\n\nPlease enter the answer of <b>{a} + {b}</b>:",parse_mode="html",disable_web_page_preview=True)
                    return
                if d!=captcha[userid]:
                    a=random.randint(30,60)
                    b=random.randint(6,15)
                    captcha[userid]=a+b
                    bot.sendMessage(userid,f"Invalid answer\n\nPlease enter the answer of <b>{a} + {b}</b>:",parse_mode="html",disable_web_page_preview=True)
                    return
                menu =telepot.namedtuple.InlineKeyboardMarkup(
                    inline_keyboard=[
                        [telepot.namedtuple.InlineKeyboardButton(text="▶️ Start Task",callback_data="StartTask")]
                    ]
                )
                bot.sendMessage(userid,WELCOME.format(firstname),parse_mode="html",reply_markup=menu,disable_web_page_preview=True)
                del captcha[userid]
                return
            elif step[userid]==3:
                if not text.startswith("@") or text.find(" ")!=-1:
                    bot.sendMessage(userid,"Invalid username!")
                    return
                cur.execute(f"UPDATE user SET twitter='{text}' WHERE id={userid}")
                conn.commit()
                step[userid]=4
                bot.sendMessage(userid,"▶️<b> Step ( 3/3 )</b>\n\nSubmit your wallet address to receive airdrop :",parse_mode="html",disable_web_page_preview=True)
                return
            elif step[userid]==4:
                cur.execute(f"SELECT id FROM user WHERE wallet='{text}'")
                d=cur.fetchall()
                if len(d)!=0 and d[0][0]!=userid:
                    bot.sendMessage(userid,"⚠️ Duplicate Wallet Detected !\n Entry Blocked !")
                    cur.execute(f"UPDATE user SET wallet='BLOCKED' WHERE id={userid}")
                    conn.commit()
                    del step[userid]
                    return
                else:
                    cur.execute(f"UPDATE user SET wallet='{text}' WHERE id={userid}")
                    conn.commit()
                    bot.sendMessage(userid,f"<b>✅ Successfully Submitted !</b>\n\nYou must have to keep subscribed to our pages till the airdrop ends. Any incomplete task will lead you ban.\n\n🚹 <b>Referral Link</b> : https://t.me/Airdrop_tester123_bot?start={userid}\n\nYou will recieve 15 ??? Per Referral",parse_mode="html",reply_markup=main_menu,disable_web_page_preview=True)
                    del step[userid]
                    return

telepot.loop.MessageLoop(bot,handle).run_as_thread()
while 1:
    time.sleep(60)