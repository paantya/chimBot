#!/usr/bin/env python
# -*- coding: utf-8 -*-

import telebot
import telebot.types as types

import re
import cash
import config

#import configTest as config
bot = telebot.TeleBot(config.token)


@bot.message_handler(commands=['start'])
def send_welcome(message):
    text = 'Добро пожаловать!\nЯ помогу тебе разобраться с числами!\nВыберите интересующий вас раздел:'
    keyboardStart = telebot.types.InlineKeyboardMarkup()
    bot.send_message(message.chat.id, text)

@bot.message_handler(commands=['help'])
def send_help(message):
    text = 'Помошь:\n/help - это сообещние\n/about - о боте\n\nДля содсчёт "собственного числа имени" введите ФИО полностью.\nДля подсчёта "собственного числа даты вождения" введите дату рождения в формате ДД ММ ГГГГ или ГГГГ ММ ДД.'
    bot.send_message(message.chat.id, text)

 # Обработчик для документов и аудиофайлов

@bot.message_handler(content_types=['document'])
def handle_docs_audio(message):
    # sendChatAction
	# action_string can be one of the following strings: 'typing', 'upload_photo', 'record_video', 'upload_video',
	# 'record_audio', 'upload_audio', 'upload_document' or 'find_location'.
    action_string = 'typing'
    bot.send_chat_action(message.chat.id, action_string)

    # getFile
	# Downloading a file is straightforward
	# Returns a File object
    print(message)
    file_name = message.document.file_name
    file_info = bot.get_file(message.document.file_id)
    print(file_name,file_info)


    action_string = 'upload_document'
    bot.send_chat_action(message.chat.id, action_string)
    import requests
    file = requests.get('https://api.telegram.org/file/bot{0}/{1}'.format(config.token, file_info.file_path))
    print('ok', file)
    #photo = open('/tmp/photo.png', 'rb')
    #bot.send_photo(message.chat.id, photo)
    bot.send_document(message.chat.id, file)



# Обычный режим
@bot.message_handler(content_types=["text"])
def any_msg(message):
    text = 'nyam?'
    bot.send_message(message.chat.id, text,parse_mode='Markdown')

if __name__ == '__main__':
    try:
        bot.polling(none_stop=True)
    except Exception:
        print('error Exception')

#YandexMetrica.setCustomAppVersion("1.13.2");
