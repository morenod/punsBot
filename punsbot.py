import telebot
import os
import sqlite3
import uuid
import string
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

version = "0.3.1"
allowed_chars = string.ascii_letters

if 'TOKEN' not in os.environ:
    print("missing TOKEN.Leaving...")
    os._exit(1)

if 'DBLOCATION' not in os.environ:
    print("missing DB.Leaving...")
    os._exit(1)

bot = telebot.TeleBot(os.environ['TOKEN'])

def db_setup(dbfile='puns.db'):
    db = sqlite3.connect(dbfile)
    cursor = db.cursor()
    cursor.execute('CREATE TABLE IF NOT EXISTS puns (uuid text, chatid int, trigger text, pun text)')
    with open(os.path.expanduser('./defaultpuns.txt'), 'r') as staticpuns:
        for line in staticpuns:
            trigger = line.split('|')[0]
            pun = line.split('|')[1]
            answer = cursor.execute('''SELECT count(trigger) FROM puns WHERE pun = ? AND trigger = ? AND chatid = 0''', (pun, trigger,)).fetchone()
            if answer[0] == 0:
                cursor.execute('''INSERT INTO puns(uuid,chatid,trigger,pun) VALUES(?,?,?,?)''', (str(uuid.uuid4()), 0, trigger, pun))
                db.commit()
    db.close()

def findPun(message="",dbfile='puns.db'):
    db = sqlite3.connect(dbfile)
    cursor = db.cursor()
#    last = "".join(c for c in message.text.lower() if c in allowed_chars).split()[-1]
    last = "".join(c for c in message.text.lower() if c in allowed_chars).split()
    if last != []:
        answer = cursor.execute('''SELECT pun from puns where trigger = ? AND (chatid = ? OR chatid = 0) ORDER BY chatid desc''', (last[-1], message.chat.id)).fetchone()
        db.commit()
        db.close()
        return answer

@bot.message_handler(commands=['punshelp'])
def help(message):
    helpmessage = '''Those are the commands available
    /punadd         Add a new pun (trigger|pun)
    /pundel         Delete an existing pun (uuid)
    /punlist        Lists all the puns for this chat
    /punmod         Modify an existing pun (uuid|trigger|pun)
    /punshelp       This help
    '''
    bot.reply_to(message, helpmessage)

@bot.message_handler(commands=['punadd'])
def add(message):
    global triggers
    global punsdb
    quote = message.text.replace('/punadd ', '')
    if quote == '' or  len(quote.split('|')) != 2:
        bot.reply_to(message, 'Missing pun or invalid syntax: \"/punadd \"pun trigger\"|\"pun\"')
        return
    trigger = quote.split('|')[0]
    for character in trigger:
        if character not in allowed_chars:
            bot.reply_to(message, 'Invalid character '+ character + ' in trigger, only letters and numbers are allowed')
            return
    pun = quote.split('|')[1]
    db = sqlite3.connect(punsdb)
    cursor = db.cursor()
    answer = cursor.execute('''SELECT count(trigger) FROM puns WHERE trigger = ? AND chatid = ?''', (trigger,message.chat.id,)).fetchone()
    db.commit()
    if answer[0] != 0:
        bot.reply_to(message, 'There is already a pun with \''+ trigger+ '\' as trigger for this group')
    else:
        cursor.execute('''INSERT INTO puns(uuid,chatid,trigger,pun) VALUES(?,?,?,?)''', (str(uuid.uuid4()),  message.chat.id, trigger, pun))
        bot.reply_to(message, 'Pun added to your channel')
        db.commit()
    db.close()
    return

@bot.message_handler(commands=['pundel'])
def delete(message):
    global triggers
    global punsdb
    quote = message.text.replace('/pundel ', '')
    if quote == '':
#todo: add uuid validator
        bot.reply_to(message, 'Missing pun uuid to remove or invalid syntax: \"/pundel \"pun uuid\"')
        return
    db = sqlite3.connect(punsdb)
    cursor = db.cursor()
    answer = cursor.execute('''SELECT count(uuid) FROM puns WHERE chatid = ? AND uuid = ?''', (message.chat.id, quote,)).fetchone()
    db.commit()
    if answer[0] != 1:
        bot.reply_to(message, 'UUID '+quote+' not found')
    else:
        cursor.execute('''DELETE FROM puns WHERE chatid = ? and uuid = ?''', (message.chat.id, quote))
        bot.reply_to(message, 'Pun deleted from your channel')
        db.commit()
    db.close()
    return

@bot.message_handler(commands=['list', 'punslist'])
def list(message):
    list = "| uuid | trigger | pun\n"
    global punsdb
    db = sqlite3.connect(punsdb)
    cursor = db.cursor()
    answer = cursor.execute('''SELECT * from puns WHERE (chatid = ? OR chatid = 0) ORDER BY chatid''', (message.chat.id,)).fetchall()
    db.commit()
    for i in answer:
        if str(i[1]) == '0':
            list += "| default pun | " + str(i[2]) + " | " + str(i[3]) + "\n"
        else:
            list += "| "+ str(i[0]) + " | " + str(i[2]) + " | " + str(i[3]) + "\n"
    bot.reply_to(message, list)
    db.close()
    return

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
	bot.reply_to(message, "Lets do some pun jokes, use /punshelp for help")

@bot.message_handler(func=lambda m: True)
def echo_all(message):
    rima = findPun(message=message,dbfile=punsdb)
    if rima != None:
        bot.reply_to(message, rima)

punsdb = os.path.expanduser(os.environ['DBLOCATION'])
db_setup(dbfile=punsdb)
print "PunsBot %s ready for puns!" %(version)
bot.polling(none_stop=True)
