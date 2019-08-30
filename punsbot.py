# -*- coding: utf-8 -*-
import telebot
import os
import sqlite3
import uuid
import string
import unicodedata
import re
import sys
import random
import time

reload(sys)
sys.setdefaultencoding('utf-8')

allowed_chars_puns = string.ascii_letters + " " + string.digits + "áéíóúàèìòùäëïöü"
allowed_chars_triggers = allowed_chars_puns + "^$.*+?(){}\\[]<>=-"
version = "0.7.0"
required_validations = 5

if 'TOKEN' not in os.environ:
    print("missing TOKEN.Leaving...")
    os._exit(1)

if 'DBLOCATION' not in os.environ:
    print("missing DB.Leaving...")
    os._exit(1)

bot = telebot.TeleBot(os.environ['TOKEN'])
bot.skip_pending = True

def is_valid_regex(regexp=""):
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
                if not is_valid_regex(trigger):
                    print "Incorrect regex trigger %s on line %s of file %s. Not added" % (trigger, str(number), punsfile)
                else:
                    pun = line.split('|')[1].strip()
                    answer = cursor.execute('''SELECT count(trigger) FROM puns WHERE pun = ? AND trigger = ? AND chatid = 0''', (pun.decode('utf8'), trigger.decode('utf8'),)).fetchone()
                    if answer[0] == 0:
                        cursor.execute('''INSERT INTO puns(uuid,chatid,trigger,pun) VALUES(?,?,?,?)''', (str(uuid.uuid4()), "0", trigger.decode('utf8'), pun.decode('utf8')))
                        db.commit()
                        print "Added default pun \"%s\" for trigger \"%s\"" % (pun, trigger)
            else:
                print "Incorrect line %s on file %s. Not added" % (str(number), punsfile)
    db.close()


def db_setup(dbfile='puns.db'):
    db = sqlite3.connect(dbfile)
    cursor = db.cursor()
    cursor.execute('CREATE TABLE IF NOT EXISTS puns (uuid text, chatid int, trigger text, pun text)')
    cursor.execute('CREATE TABLE IF NOT EXISTS validations (punid text, chatid int, userid text, karma int)')
    cursor.execute('CREATE TABLE IF NOT EXISTS chatoptions (chatid int, silence int, efectivity int, unique (chatid))')
    db.commit()
    db.close()
    for db_file in os.listdir('./defaultpuns/punsfiles'):
        load_default_puns(dbfile=punsdb, punsfile="./defaultpuns/punsfiles/" + db_file)


def is_chat_silenced(message="", dbfile='puns.db'):
    db = sqlite3.connect(dbfile)
    cursor = db.cursor()
    answer = cursor.execute('''SELECT silence from chatoptions where chatid = ?''', (message.chat.id,)).fetchone()
    silence = int(answer[0] if answer is not None and answer[0] is not None else 0)
    return True if silence > time.time() else False


def silence_until(chatid=""):
    global punsdb
    db = sqlite3.connect(punsdb)
    cursor = db.cursor()
    answer = cursor.execute('''SELECT silence from chatoptions where chatid = ?''', (chatid,)).fetchone()
    return str(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(answer[0]))) if answer is not None and answer[0] is not None and int(time.time()) < int(answer[0]) else "Never"


def load_chat_options(chatid=""):
    global punsdb
    db = sqlite3.connect(punsdb)
    cursor = db.cursor()
    answer = cursor.execute('''SELECT chatid,silence,efectivity from chatoptions where chatid = ?''', (chatid,)).fetchone()
    db.close()
    chatoptions = {'chatid': chatid,
                   'silence': answer[1] if answer is not None and answer[1] is not None else None,
                   'efectivity': answer[2] if answer is not None and answer[2] is not None else None}
    return chatoptions


def set_chat_options(chatoptions=""):
    global punsdb
    db = sqlite3.connect(punsdb)
    cursor = db.cursor()
    chatid = chatoptions['chatid'] if chatoptions['chatid'] is not None else None
    silence = chatoptions['silence'] if chatoptions['silence'] is not None else None
    efectivity = chatoptions['efectivity'] if chatoptions['efectivity'] is not None else None
    cursor.execute('''INSERT OR REPLACE INTO chatoptions(chatid,silence,efectivity) VALUES(?,?,?)''', (chatid, silence, efectivity))
    db.commit()
    db.close()


def is_efective(chatid=""):
    global punsdb
    db = sqlite3.connect(punsdb)
    cursor = db.cursor()
    random.randrange(0, 101, 2)
    answer = cursor.execute('''SELECT efectivity from chatoptions where chatid = ?''', (chatid,)).fetchone()
    return True if answer is None or answer[0] is None or int(answer[0]) >= random.randint(0, 100) else False


def efectivity(chatid=""):
    global punsdb
    db = sqlite3.connect(punsdb)
    cursor = db.cursor()
    answer = cursor.execute('''SELECT efectivity from chatoptions where chatid = ?''', (chatid,)).fetchone()
    return answer[0] if answer is not None else "100"


def find_pun(message="", dbfile='puns.db'):
    db = sqlite3.connect(dbfile)
    cursor = db.cursor()
    answer_list = []
# First, remove emojis and any other char not in the allowed chars
    clean_text = "".join(c for c in message.text.lower() if c in allowed_chars_puns).split()
# Then, remove accents from letters, ó becomes on o to be compared with the triggers list
    if clean_text != []:
        last_clean = unicodedata.normalize('NFKD', clean_text[-1]).encode('ASCII', 'ignore')
        triggers = cursor.execute('''SELECT trigger from puns where (chatid = ? or chatid = 0) order by chatid desc''', (message.chat.id,)).fetchall()
        for i in triggers:
            if is_valid_regex(i[0]):
                regexp = re.compile('^' + i[0] + '$')
                if regexp.match(last_clean) is not None:
                    matches = cursor.execute('''SELECT uuid,pun,chatid from puns where trigger = ? AND (chatid = ? OR chatid = 0) ORDER BY chatid desc''', (i[0], message.chat.id)).fetchall()
                    for j in matches:
                        if j[1].split()[-1] != last_clean:
                            enabled = cursor.execute('''SELECT SUM(karma) from validations where punid = ? AND chatid = ?''', (j[0], message.chat.id)).fetchone()
                            if j[2] == 0 or enabled[0] >= required_validations or (bot.get_chat_members_count(message.chat.id) < required_validations and enabled[0] > 0):
                                answer_list.append(j[1])
        db.close()
        return None if answer_list == [] else random.choice(answer_list)


@bot.message_handler(commands=['punshelp', 'help'])
def help(message):
    helpmessage = '''Those are the commands available
    /punadd         Add a new pun (trigger|pun)
    /pundel         Delete an existing pun (uuid)
    /punlist        Lists all the puns for this chat (/list or /punslist)
    /punapprove     Give +1 to a pun
    /punban         Give -1 to a pun
    /punsilence     Stop puns for specified minutes
    /punset         Set the probability of answering with a pun (1-100)
    /punshelp       This help (/help)

    ** PunsBot muted on this channel until %s  **
    ** Probability of answering with a pun: %s%% **

    Puns will be enabled if karma is over %s on groups with more than %s people.
    On groups with less people, only positive karma is required

    Version: %s
    ''' % (silence_until(message.chat.id), efectivity(message.chat.id), required_validations, required_validations, version)
    bot.reply_to(message, helpmessage)


@bot.message_handler(commands=['punapprove'])
def approve(message):
    global triggers
    global punsdb
    quote = message.text.replace('/punapprove', '').strip()
    if quote == '':
        bot.reply_to(message, 'Missing uuid to approve or invalid syntax: \"/punapprove \"pun uuid\"')
        return
    db = sqlite3.connect(punsdb)
    cursor = db.cursor()
    answer = cursor.execute('''SELECT count(uuid) FROM puns WHERE chatid = ? AND uuid = ?''', (message.chat.id, quote.strip(),)).fetchone()
    if answer[0] != 1:
        bot.reply_to(message, 'UUID ' + quote.strip() + ' not found')
    else:
        answer = cursor.execute('''SELECT count(punid) FROM validations WHERE chatid = ? AND punid = ? AND userid = ? and karma = 1''', (message.chat.id, quote.strip(), message.from_user.id)).fetchone()
        if answer[0] >= 1:
            bot.reply_to(message, 'You have already approved ' + quote + '. Only one approve by user is allowed.')
        else:
            cursor.execute('''INSERT INTO validations(punid,chatid,userid,karma) VALUES(?,?,?,1)''', (quote.strip(), message.chat.id, message.from_user.id))
            db.commit()
            answer = cursor.execute('''SELECT SUM(karma) FROM validations WHERE chatid = ? AND punid = ?''', (message.chat.id, quote.strip())).fetchone()
            bot.reply_to(message, 'Thanks for approve ' + quote.strip() + '. Pun karma is ' + str(answer[0]))
    db.close()
    return


@bot.message_handler(commands=['punban'])
def ban(message):
    global triggers
    global punsdb
    quote = message.text.replace('/punban', '').strip()
    if quote == '':
        bot.reply_to(message, 'Missing uuid to ban or invalid syntax: \"/punban \"pun uuid\"')
        return
    db = sqlite3.connect(punsdb)
    cursor = db.cursor()
    answer = cursor.execute('''SELECT count(uuid) FROM puns WHERE chatid = ? AND uuid = ?''', (message.chat.id, quote.strip(),)).fetchone()
    if answer[0] != 1:
        bot.reply_to(message, 'UUID ' + quote.strip() + ' not found')
    else:
        answer = cursor.execute('''SELECT count(punid) FROM validations WHERE chatid = ? AND punid = ? AND userid = ? and karma = -1''', (message.chat.id, quote.strip(), message.from_user.id)).fetchone()
        if answer[0] >= 1:
            bot.reply_to(message, 'You have already ban ' + quote + '. Only one ban by user is allowed.')
        else:
            cursor.execute('''INSERT INTO validations(punid,chatid,userid,karma) VALUES(?,?,?,-1)''', (quote.strip(), message.chat.id, message.from_user.id))
            db.commit()
            answer = cursor.execute('''SELECT SUM(karma) FROM validations WHERE chatid = ? AND punid = ?''', (message.chat.id, quote.strip())).fetchone()
            bot.reply_to(message, 'Thanks for ban ' + quote.strip() + '. Pun karma is ' + str(answer[0]))
    db.close()
    return


@bot.message_handler(commands=['punadd'])
def add(message):
    global triggers
    global punsdb
    quote = message.text.replace('/punadd', '')
    if quote == '' or len(quote.split('|')) != 2:
        bot.reply_to(message, 'Missing pun or invalid syntax: \"/punadd \"pun trigger\"|\"pun\"')
        return
    trigger = quote.split('|')[0].strip()
    for character in trigger:
        if character not in allowed_chars_triggers:
            bot.reply_to(message, 'Invalid character ' + character + ' in trigger, only letters and numbers are allowed')
            return
    if not is_valid_regex(trigger):
        bot.reply_to(message, 'Not valid regex ' + trigger + ' defined as trigger ')
        return
    pun = quote.split('|')[1].strip()
    db = sqlite3.connect(punsdb)
    cursor = db.cursor()
    answer = cursor.execute('''SELECT count(trigger) FROM puns WHERE trigger = ? AND chatid = ? AND pun = ?''', (trigger, message.chat.id, pun)).fetchone()
    db.commit()
    if answer[0] != 0:
        bot.reply_to(message, 'A trigger with this pun already exists')
    else:
        punid = uuid.uuid4()
        cursor.execute('''INSERT INTO puns(uuid,chatid,trigger,pun) VALUES(?,?,?,?)''', (str(punid), message.chat.id, trigger.decode('utf8'), pun.decode('utf8')))
        cursor.execute('''INSERT INTO validations(punid,chatid,userid,karma) VALUES(?,?,?,1)''', (str(punid), message.chat.id, message.from_user.id))
        db.commit()
        if bot.get_chat_members_count(message.chat.id) >= required_validations:
            bot.reply_to(message, 'Pun ' + str(punid) + ' added to your channel. It have to be approved by ' + str(required_validations) + ' different people to be enabled on this chat')
        else:
            bot.reply_to(message, 'Pun ' + str(punid) + ' added to your channel. Positive karma is required to enable pun on this chat')
        print "Pun \"%s\" with trigger \"%s\" added to channel %s" % (pun, trigger, message.chat.id)
    db.close()
    return


@bot.message_handler(commands=['pundel'])
def delete(message):
    global triggers
    global punsdb
    quote = message.text.replace('/pundel', '').strip()
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


@bot.message_handler(commands=['punsilence'])
def silence(message):
    global punsdb
    quote = message.text.replace('/punsilence', '').strip()
    if quote == '' or not quote.isdigit():
        bot.reply_to(message, 'Missing time to silence or invalid syntax: \"/punsilence "time in minutes"')
        return
    if int(quote) > 60 or not quote.isdigit():
        bot.reply_to(message, 'Disabling PunsBot for more than an hour is not funny 😢')
        return
    chatoptions = load_chat_options(message.chat.id)
    if chatoptions['silence'] is None or int(chatoptions['silence']) <= int(time.time()):
        chatoptions['silence'] = 60 * int(quote) + int(time.time())
    else:
        if int(chatoptions['silence']) + 60 * int(quote) - int(time.time()) >= 3600:
            bot.reply_to(message, 'Disabling PunsBot for more than an hour is not funny 😢')
            return
        else:
            chatoptions['silence'] = 60 * int(quote) + int(chatoptions['silence'])
    set_chat_options(chatoptions)
    bot.reply_to(message, 'PunsBot will be muted until ' + time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(chatoptions['silence'])))


@bot.message_handler(commands=['punset'])
def set(message):
    quote = message.text.replace('/punset', '').strip()
    if quote == '' or int(quote) > 100 or int(quote) < 0 or not quote.isdigit():
        bot.reply_to(message, 'Missing probability, out of range or invalid syntax: \"/punset "probability (1-100)"')
        return
    elif quote == '0':
        bot.reply_to(message, 'Probability cannot be 0, to disable punsbot during a period of time, use /punsilence"')
        return
    chatoptions = load_chat_options(message.chat.id)
    chatoptions['efectivity'] = int(quote)
    set_chat_options(chatoptions)
    bot.reply_to(message, 'PunsBot will detect puns ' + quote + '% of the times')


@bot.message_handler(commands=['list', 'punlist', 'punslist'])
def list(message):
    index = "| uuid | status (karma) | trigger | pun\n"
    puns_list = ""
    global punsdb
    db = sqlite3.connect(punsdb)
    cursor = db.cursor()
    answer = cursor.execute('''SELECT * from puns WHERE (chatid = ? OR chatid = 0) ORDER BY chatid''', (message.chat.id,)).fetchall()
    db.commit()
    for i in answer:
        validations = cursor.execute('''SELECT SUM(validations.karma) FROM puns,validations WHERE puns.chatid = ? AND puns.uuid = ? AND puns.uuid == validations.punid AND puns.chatid = validations.chatid''', (message.chat.id, i[0],)).fetchone()
        if str(i[1]) == '0':
            puns_list += "| default pun | always enabled | " + str(i[2]) + " | " + str(i[3]) + "\n"
        else:
            if bot.get_chat_members_count(message.chat.id) >= required_validations:
                if validations[0] >= required_validations:
                    puns_list += "| " + str(i[0]) + " | enabled (" + str(validations[0]) + "/" + str(required_validations) + ") | " + str(i[2]) + " | " + str(i[3]) + "\n"
                else:
                    puns_list += "| " + str(i[0]) + " | disabled (" + str(validations[0]) + "/" + str(required_validations) + ") | " + str(i[2]) + " | " + str(i[3]) + "\n"
            else:
                if validations[0] > 0:
                    puns_list += "| " + str(i[0]) + " | enabled (" + str(validations[0]) + ") | " + str(i[2]) + " | " + str(i[3]) + "\n"
                else:
                    puns_list += "| " + str(i[0]) + " | disabled (" + str(validations[0]) + ") | " + str(i[2]) + " | " + str(i[3]) + "\n"
    if len(puns_list) > 4000:
        entries = puns_list.split('\n')
        output = ""
        for i in entries:
            if len(index + output + i + '\n') > 4000:
                bot.reply_to(message, index + output)
                output = i + '\n'
            else:
                output = output + i + '\n'
        bot.reply_to(message, index + output)
    else:
        bot.reply_to(message, index + puns_list)
    db.close()
    return


@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Lets do some pun jokes, use /punshelp for help")


@bot.message_handler(func=lambda m: True)
def echo_all(message):
    if not is_chat_silenced(message=message, dbfile=punsdb) and is_efective(message.chat.id):
        rima = find_pun(message=message, dbfile=punsdb)
        if rima is not None:
            bot.reply_to(message, rima)


punsdb = os.path.expanduser(os.environ['DBLOCATION'])
db_setup(dbfile=punsdb)
print "PunsBot %s ready for puns!" % (version)
bot.polling(none_stop=True)
