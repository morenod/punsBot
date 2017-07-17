import telebot
import os
import sqlite3
import uuid

if 'TOKEN' not in os.environ:
    print("missing TOKEN.Leaving...")
    os._exit(1)

bot = telebot.TeleBot(os.environ['TOKEN'])

def db_setup(dbfile='puns.db'):
    db = sqlite3.connect(dbfile)
    cursor = db.cursor()
    cursor.execute('CREATE TABLE IF NOT EXISTS puns (uuid text, chatid int, trigger text, pun text)')
    db.commit()
    db.close()

def db_load_triggers(dbfile='puns.db'):
    db = sqlite3.connect(dbfile)
    cursor = db.cursor()
    answer = str(cursor.execute('SELECT trigger FROM puns').fetchall())
    db.commit()
    db.close()
    return answer

def findPun(message="",dbfile='puns.db'):
    answer = ""
    db = sqlite3.connect(dbfile)
    cursor = db.cursor()
    for i in message.split(" "):
        answer = cursor.execute('''SELECT pun from puns where trigger = ?''', (i,)).fetchone()
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
        bot.reply_to(message, 'Missing pun or invalid sytanx: \"/punadd \"pun trigger\"|\"pun\"')
        return
    trigger = quote.split('|')[0]
    pun = quote.split('|')[1]
    db = sqlite3.connect(punsdb)
    cursor = db.cursor()
    cursor.execute('''INSERT INTO puns(uuid,chatid,trigger,pun) VALUES(?,?,?,?)''', (str(uuid.uuid4()),  message.chat.id, trigger, pun))
    bot.reply_to(message, 'Pun added to your channel')
    db.commit()
    db.close()
    triggers = db_load_triggers(punsdb)
    print triggers

@bot.message_handler(commands=['punslist'])
def list(message):
    global punsdb
    db = sqlite3.connect(punsdb)
    cursor = db.cursor()
    answer = cursor.execute('''SELECT * from puns''').fetchall()
    print answer
    db.commit()
    bot.reply_to(message, answer)
    db.close()
    return

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
	bot.reply_to(message, "Lets do some pun jokes, use /punshelp for help")

@bot.message_handler(func=lambda m: True)
def echo_all(message):
    rima = findPun(message=message.text,dbfile=punsdb)
    if rima != None:
        bot.reply_to(message, rima)

punsdb = os.path.expanduser("~/punsdb.db")
db_setup(dbfile=punsdb)
triggers = db_load_triggers(dbfile=punsdb)
print("Ready for puns!")
bot.polling(none_stop=True)
