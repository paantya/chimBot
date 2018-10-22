#!/usr/bin/env python
# -*- coding: utf-8 -*-

import telebot

#import re
import os
#import cash
#import xlrd
import pandas
import config
import random

# sphinx_gallery_thumbnail_number = 3
import matplotlib.pyplot as plt

bgErr = 0.01
#import configTest as config
bot = telebot.TeleBot(config.token)

# Обработчик для документов
@bot.message_handler(content_types=['document'])
def handle_docs_audio(message):
    action_string = 'typing'
    bot.send_chat_action(message.chat.id, action_string)

    mimeType = message.document.mime_type
    file_name = message.document.file_name
    if mimeType != 'application/vnd.ms-excel':
        text = "Енто не excel файл! :С"
        bot.send_message(message.chat.id, text, reply_to_message_id=message.message_id)
    else:
        try:
            file_info = bot.get_file(message.document.file_id)
            downloaded_file = bot.download_file(file_info.file_path)
            f = open(file_name, "wb")
            f.write(downloaded_file)
            f.close()

            df = pandas.read_excel(file_name, header=None)
            A = df[0].values
            B = df[1].values
            minB = min(B)
            maxB = max(B)

            bgs = [i for i in B if i <= (minB + bgErr)]
            bg = sum(bgs) / len(bgs)
            BdBG = B - bg

            def B300(x):
                k = 0
                while x[k] < 300:
                    k += 1
                return k

            def BBg(x, bg):
                k = 0
                while x[k] <= (bg + bgErr):
                    k += 1
                return k

            trs = [(BdBG[i + 1] + BdBG[i]) * (A[i + 1] - A[i]) / 2 for i in range(BBg(B, bg), B300(A))]
            trSum = sum(trs)
            text = "sum = `{}`\nmax = `{}`\nsbg = `{}`".format(trSum, maxB, bg)
            bot.send_message(message.chat.id, text, parse_mode = "Markdown", reply_to_message_id = message.message_id)

            action_string = 'upload_photo'
            bot.send_chat_action(message.chat.id, action_string)

            plt.figure(figsize=(17, 7))
            plt.plot(A, B, ':')
            line_max, = plt.plot(A, [maxB for i in A], '-.', color='b', label='max intensity')
            line_sbg, =plt.plot(A, [bg for i in A], '-.', label='sr. bg')
            line_bg, = plt.plot(A[:BBg(B, bg)], B[:BBg(B, bg)], 'o', color='r', label = 'bg')
            line_sg, = plt.plot(A[BBg(B, bg):B300(A) + 1], B[BBg(B, bg):B300(A) + 1], '^', color='g', label = 'signal')
            plt.xlabel('time')
            plt.ylabel('intensity')
            plt.title('the '+file_name)
            plt.legend([line_sg, line_bg, line_max, line_sbg], ['signal', 'background', 'max intensity = '+str(maxB),
                                                                'sr background = '+str(bg)])
            plt.grid()
            plt.savefig('pic' + file_name[:-4] + '_all.png')

            photo = open('pic' + file_name[:-4] + '_all.png', 'rb')
            bot.send_document(message.chat.id, photo, reply_to_message_id=message.message_id)

            plt.figure(figsize=(17, 7))
            plt.plot(A[:BBg(B, bg)+1], B[:BBg(B, bg)+1], ':')
            line_sbg, = plt.plot(A[:BBg(B, bg) + 1], [bg for i in A[:BBg(B, bg) + 1]], '-.', label='sr. bg')
            line_bg, = plt.plot(A[:BBg(B, bg)], B[:BBg(B, bg)], 'o', color='r')
            line_sg, = plt.plot(A[BBg(B, bg)], B[BBg(B, bg)], '^', color='g')
            plt.xlabel('time')
            plt.ylabel('intensity')
            plt.title('the background '+file_name)
            plt.legend([line_sg, line_bg, line_sbg], ['signal', 'background', 'sr background = '+str(bg)])
            plt.grid()
            plt.savefig('pic' + file_name[:-4] + '_bg.png')

            photo = open('pic' + file_name[:-4] + '_bg.png', 'rb')
            bot.send_document(message.chat.id, photo, reply_to_message_id=message.message_id)
        except Exception:
            text = 'Что-то пошло не так :С\n' \
                   'Попробуйсте ещё раз, если не получится, то что-то не так с содержинием файла'
            bot.send_message(message.chat.id, text, parse_mode = "Markdown", reply_to_message_id = message.message_id)
            if os.path.exists(file_name):
                os.remove(file_name)
            if os.path.exists('pic'+file_name[:-4]+'_all.png'):
                os.remove('pic'+file_name[:-4]+'_all.png')
            if os.path.exists('pic'+file_name[:-4]+'_bg.png'):
                os.remove('pic'+file_name[:-4]+'_bg.png')

# Обычный режим
@bot.message_handler(content_types=["text"])
def any_msg(message):
    text = random.choice(['😁','🙈','✨','🌸','🍁','🍀','🎏','🐙','🐧','🐨','🐳','🐼','👻','👾'])
    bot.send_message(message.chat.id, text, parse_mode='Markdown')

if __name__ == '__main__':
    try:
        bot.polling(none_stop=True)
    except Exception:
        print('error Exception')
