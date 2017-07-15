import telebot
import os

if 'TOKEN' not in os.environ:
    print("missing TOKEN.Leaving...")
    os._exit(1)

bot = telebot.TeleBot(os.environ['TOKEN'])

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
	bot.reply_to(message, "Howdy, how are you doing?")
    
print("Ready for trolling!")
bot.polling()
