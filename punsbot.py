# -*- coding: utf-8 -*-
import telebot
import os
import sqlite3
import uuid
import string
import unicodedata
import re
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

allowed_chars_puns = string.ascii_letters + " " + string.digits + "áéíóúàèìòùäëïöü"
allowed_chars_triggers = allowed_chars_puns + "^$.*+?(){}\\[]<>=-"
version = "0.4.2"

if 'TOKEN' not in os.environ:
    print("missing TOKEN.Leaving...")
    os._exit(1)

if 'DBLOCATION' not in os.environ:
    print("missing DB.Leaving...")
    os._exit(1)

bot = telebot.TeleBot(os.environ['TOKEN'])


def isValidRegex(regexp=""):
    try:
        re.compile(regexp)
        is_valid = True
    except re.error:
        is_valid = False
    return is_valid


def load_default_puns(dbfile='puns.db', punsfile='puns.txt'):
    db = sqlite3.connect(dbfile)
    cursor = db.cursor()
    with open(os.path.expanduser(punsfile), 'r') as staticpuns:
        number = 0
        for line in staticpuns:
            number += 1
            if len(line.split('|')) == 2:
                trigger = line.split('|')[0].strip()
                if not isValidRegex(trigger):
                    print "Incorrect regex trigger %s on line %s of file %s. Not added" % (trigger, str(number), punsfile)
                else:
                    pun = line.split('|')[1].strip()
                    answer = cursor.execute('''SELECT count(trigger) FROM puns WHERE pun = ? AND trigger = ? AND chatid = 0''', (pun, trigger,)).fetchone()
                    if answer[0] == 0:
                        cursor.execute('''INSERT INTO puns(uuid,chatid,trigger,pun) VALUES(?,?,?,?)''', (str(uuid.uuid4()), 0, trigger, pun))
                        db.commit()
                        print "Added default pun \"%s\" for trigger \"%s\"" % (pun, trigger)
            else:
                print "Incorrect line %s on file %s. Not added" % (str(number), punsfile)
    db.close()


def db_setup(dbfile='puns.db'):
    db = sqlite3.connect(dbfile)
    cursor = db.cursor()
    cursor.execute('CREATE TABLE IF NOT EXISTS puns (uuid text, chatid int, trigger text, pun text)')
    db.commit()
    db.close()
    for file in os.listdir('./defaultpuns'):
        if not os.path.isdir(file):
            load_default_puns(dbfile=punsdb, punsfile="./defaultpuns/" + file)


def findPun(message="", dbfile='puns.db'):
    db = sqlite3.connect(dbfile)
    cursor = db.cursor()
# First, remove emojis and any other char not in the allowed chars
    clean_text = "".join(c for c in message.text.lower() if c in allowed_chars_puns).split()
# Then, remove accents from letters, ó becomes on o to be compared with the triggers list
    last_clean = unicodedata.normalize('NFKD', clean_text[-1]).encode('ASCII', 'ignore')
    if last_clean != []:
        triggers = cursor.execute('''SELECT trigger from puns where chatid = ? or chatid = 0 order by chatid desc''', (message.chat.id,)).fetchall()
        for i in triggers:
            if isValidRegex(i[0]):
                regexp = re.compile('^' + i[0] + '$')
                if regexp.match(last_clean) is not None:
                    answer = cursor.execute('''SELECT pun from puns where trigger = ? AND (chatid = ? OR chatid = 0) ORDER BY chatid desc''', (i[0], message.chat.id)).fetchone()
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
    if quote == '' or len(quote.split('|')) != 2:
        bot.reply_to(message, 'Missing pun or invalid syntax: \"/punadd \"pun trigger\"|\"pun\"')
        return
    trigger = quote.split('|')[0].strip()
    for character in trigger:
        if character not in allowed_chars_triggers:
            bot.reply_to(message, 'Invalid character ' + character + ' in trigger, only letters and numbers are allowed')
            return
    if not isValidRegex(trigger):
        bot.reply_to(message, 'Not valid regex ' + trigger + ' defined as trigger ')
        return
    pun = quote.split('|')[1].strip()
    db = sqlite3.connect(punsdb)
    cursor = db.cursor()
    answer = cursor.execute('''SELECT count(trigger) FROM puns WHERE trigger = ? AND chatid = ?''', (trigger, message.chat.id,)).fetchone()
    db.commit()
    if answer[0] != 0:
        bot.reply_to(message, 'There is already a pun with \'' + trigger + '\' as trigger for this group')
    else:
        cursor.execute('''INSERT INTO puns(uuid,chatid,trigger,pun) VALUES(?,?,?,?)''', (str(uuid.uuid4()), message.chat.id, trigger, pun))
        bot.reply_to(message, 'Pun added to your channel')
        db.commit()
        print "Pun \"%s\" with trigger \"%s\" added to channel %s" % (pun, trigger, message.chat.id)
    db.close()
    return


@bot.message_handler(commands=['pundel'])
def delete(message):
    global triggers
    global punsdb
    quote = message.text.replace('/pundel ', '')
    if quote == '':
        bot.reply_to(message, 'Missing pun uuid to remove or invalid syntax: \"/pundel \"pun uuid\"')
        return
    db = sqlite3.connect(punsdb)
    cursor = db.cursor()
    answer = cursor.execute('''SELECT count(uuid) FROM puns WHERE chatid = ? AND uuid = ?''', (message.chat.id, quote,)).fetchone()
    db.commit()
    if answer[0] != 1:
        bot.reply_to(message, 'UUID ' + quote + ' not found')
    else:
        cursor.execute('''DELETE FROM puns WHERE chatid = ? and uuid = ?''', (message.chat.id, quote))
        bot.reply_to(message, 'Pun deleted from your channel')
        db.commit()
        print "Pun with UUID \"%s\" deleted from channel %s" % (quote, message.chat.id)
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
            list += "| " + str(i[0]) + " | " + str(i[2]) + " | " + str(i[3]) + "\n"
    bot.reply_to(message, list)
    db.close()
    return


@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.reply_to(message, "Lets do some pun jokes, use /punshelp for help")


@bot.message_handler(func=lambda m: True)
def echo_all(message):
    rima = findPun(message=message, dbfile=punsdb)
    if rima is not None:
        bot.reply_to(message, rima)

punsdb = os.path.expanduser(os.environ['DBLOCATION'])
db_setup(dbfile=punsdb)
print "PunsBot %s ready for puns!" % (version)
bot.polling(none_stop=True)
