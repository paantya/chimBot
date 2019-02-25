#!/usr/bin/env python
# -*- coding: utf-8 -*-

import telebot
from telebot import types

#import re
import os
#import cash
#import xlrd
import pandas
import config
import random

# sphinx_gallery_thumbnail_number = 3
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

bgErr = 0.01
#import configTest as config
bot = telebot.TeleBot(config.token)

def get_times():
    with open("bot.txt", 'r') as f_cst1:
        pr1c_ = int(f_cst1.readline())
    return pr1c_

def write_time(data_):
    with open("bot.txt", 'w') as f_cst4:
        f_cst4.write(data_)

def get_dispersio():
    with open("dispersio.txt", 'r') as f_cst2:
        pr2c_ = float(f_cst2.readline())
    return pr2c_

def write_dispersio(data_):
    with open("dispersio.txt", 'w') as f_cst3:
        f_cst3.write(data_)



@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
    # Если сообщение из чата с ботом
    if call.message:
        if call.data == "status":
            pr1c = get_times()
            pr2c = get_dispersio()
            text = "Time: {}\nDispersio: {}.".format(pr1c, pr2c)
            bot.answer_callback_query(callback_query_id=call.id, show_alert=True, text=text)
        else:
            write_dispersio(call.data)
            bot.answer_callback_query(callback_query_id=call.id, show_alert=False, text="Dispersio: {}".format(call.data))


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

            def dispersio(results):
                # calculate mean
                m = sum(results) / len(results)
                # calculate variance using a list comprehension
                var_res = sum([(xi - m) ** 2 for xi in results]) / len(results)
                return var_res

            d_id = 2
            param_dispersio = get_dispersio()
            while dispersio(B[:d_id+1]) <= param_dispersio:
                d_id += 1


            def B300(x):
                pr = get_times()
                k = 0
                while x[k] < pr:
                    k += 1
                return k

            def BBg(x, bg):
                k = 0
                while x[k] <= (bg + bgErr):
                    k += 1
                return k

            bg = sum(B[:d_id]) / len(B[:d_id])
            BdBG = B - bg

            trs = [(BdBG[i + 1] + BdBG[i]) * (A[i + 1] - A[i]) / 2 for i in range(d_id, B300(A))]
            tr_sum = sum(trs)
            trs_pls = [(BdBG[i + 1] + BdBG[i]) * (A[i + 1] - A[i]) / 2 for i in range(d_id-1, B300(A))]
            tr_sum_pls = sum(trs_pls)
            text = "sum = `{}`\nsam = `{}`\nmax = `{}`\nsbg = `{}`\nmax - sbg = \n`{}`\ndispersio: -1".format(tr_sum, tr_sum_pls, maxB, bg, (maxB - bg))

            keyboard = types.InlineKeyboardMarkup()
            old_d = -1
            for i in range(2, BBg(B, bg) + 2):
                if old_d <= dispersio(B[:i]):
                    callback_button = types.InlineKeyboardButton(
                        text="{}: {}".format(i, dispersio(B[:i])),
                        callback_data="{}".format(1.00001 * dispersio(B[:i]))
                    )
                    keyboard.add(callback_button)
                    old_d = dispersio(B[:i])
            callback_button = types.InlineKeyboardButton(text="status", callback_data="status")
            keyboard.add(callback_button)

            bot.send_message(message.chat.id, text, parse_mode="Markdown", reply_to_message_id=message.message_id,
                             reply_markup=keyboard
                             )


            action_string = 'upload_photo'
            bot.send_chat_action(message.chat.id, action_string)
            df[[0,1]].to_csv(file_name, sep=' ', encoding='utf-8')

            f1 = plt.figure(figsize=(17, 7))
            plt.plot(A, B, '-', color = 'k')
            line_max, = plt.plot(A, [maxB for i in A], ':', color='r', label='max intensity')
            line_sbg, =plt.plot(A, [bg for i in A], '-.', label='sr. bg')
            line_bg7, = plt.plot(A[:BBg(B, bg)], B[:BBg(B, bg)], 'o', color='g')
            line_bg, = plt.plot(A[:d_id], B[:d_id], 'o', color='r', label = 'bg')
            line_sg, = plt.plot(A[BBg(B, bg):B300(A) + 1], B[BBg(B, bg):B300(A) + 1], '^', color='g', label = 'signal')
            plt.xlabel('time')
            plt.ylabel('intensity')
            plt.title('the '+file_name)
            plt.legend([
                line_sg,
                line_bg,
                line_bg7,
                line_max,
                line_sbg
                ],
                [
                    'signal',
                    'background',
                    'candidate background ',
                    'max intensity = '+str(maxB),
                    'sr background = '+str(bg)
                 ])
            plt.grid()
            plt.savefig('pic' + file_name[:-4] + '_all.png')
            plt.close(f1)
            #for t,x in zip(A[BBg(B, bg):B300(A) + 1], B[BBg(B, bg):B300(A) + 1]):
            #    print("{} {}".format(t,x))



            photo = open('pic' + file_name[:-4] + '_all.png', 'rb')
            bot.send_document(message.chat.id, photo, reply_to_message_id=message.message_id)
            photo.close()
            if os.path.exists('pic' + file_name[:-4] + '_all.png'):
                os.remove('pic' + file_name[:-4] + '_all.png')


            f2 = plt.figure(figsize=(17, 7))
            plt.plot(A[:BBg(B, bg)+1], B[:BBg(B, bg)+1], ':')
            line_sbg, = plt.plot(A[:BBg(B, bg) + 1], [bg for i in A[:BBg(B, bg) + 1]], '-.', label='sr. bg')
            line_bg7, = plt.plot(A[:BBg(B, bg)], B[:BBg(B, bg)], 'o', color='g')
            line_bg, = plt.plot(A[:d_id], B[:d_id], 'o', color='r')
            line_sg, = plt.plot(A[BBg(B, bg)], B[BBg(B, bg)], '^', color='g')
            plt.xlabel('time')
            plt.ylabel('intensity')
            plt.title('the background '+file_name)
            plt.legend([line_sg, line_bg, line_bg7, line_sbg], ['signal', 'background', 'candidate background', 'sr background = '+str(bg)])
            plt.grid()
            plt.savefig('pic' + file_name[:-4] + '_bg.png')
            plt.close(f2)

            photo = open('pic' + file_name[:-4] + '_bg.png', 'rb')
            bot.send_document(message.chat.id, photo, reply_to_message_id=message.message_id)
            photo.close()
            if os.path.exists('pic'+file_name[:-4]+'_bg.png'):
                os.remove('pic'+file_name[:-4]+'_bg.png')


        except Exception:
            text = 'Что-то пошло не так :С\n' \
                   'Попробуйсте ещё раз, если не получится, то что-то не так с содержинием файла'
            bot.send_message(message.chat.id, text, parse_mode = "Markdown", reply_to_message_id = message.message_id)
        finally:
            #plt.close("all")
            if os.path.exists(file_name):
                os.remove(file_name)
            if os.path.exists('pic'+file_name[:-4]+'_all.png'):
                os.remove('pic'+file_name[:-4]+'_all.png')
            #if os.path.exists('pic'+file_name[:-4]+'_bg.png'):
            #    os.remove('pic'+file_name[:-4]+'_bg.png')




@bot.message_handler(commands=['status'])
def set_status(message):
    pr1 = get_times()
    pr2 = get_dispersio()

    text = "Текущее значени параметра отсечения: **{}**.\nТекущее значени параметра разброса фона: **{}**.".format(pr1,pr2)
    bot.send_message(message.chat.id, text, parse_mode="Markdown", reply_to_message_id=message.message_id)

@bot.message_handler(commands=['set_botten'])
def set_botten(message):
    if len(message.text)<13 or not message.text.split()[-1].isdecimal() or int(message.text.split()[-1]) < 2 or int(message.text.split()[-1]) > 1000:
        bot_pr = get_times()
        text = "Введите корректное значени верхней границы.\nЦелое число от 2 до 1000. Сейчас: {}\n__По умолчанию рекомендуется значение 300.".format(bot_pr)
        bot.send_message(message.chat.id, text, parse_mode="Markdown", reply_to_message_id=message.message_id)
    else:
        write_time(message.text.split()[-1])
        text = "Мы заменили значение верхней границы на **{}**.".format(message.text.split()[-1])
        bot.send_message(message.chat.id, text, parse_mode="Markdown")

@bot.message_handler(commands=['set_dispersio'])
def set_dispersio(message):
    import re
    def is_number_regex(s):
        """ Returns True is string is a number. """
        if re.match("^\d+?\.?\d+?e?-?\d+?$", s) is None:
            return False
        return True
    if len(message.text) < 15 or not is_number_regex(message.text.split(' ')[-1]) or float(message.text.split()[-1]) < 0:
        dis_pr = get_dispersio()
        text = "Введите корректное значени верхней границы.\nНужно число больше нуля. Сейчас: {}\n__По умолчанию рекомендуется значение 1.0e-6.".format(dis_pr)
        bot.send_message(message.chat.id, text, parse_mode="Markdown", reply_to_message_id=message.message_id)
    else:
        write_dispersio(message.text.split(" ")[-1])
        text = "Мы заменили значение верхней границы на **{}**.".format(message.text.split(" ")[-1])
        bot.send_message(message.chat.id, text, parse_mode="Markdown")


# Обычный режим
@bot.message_handler(content_types=["text"])
def any_msg(message):
    sml = (['😁','🙈','✨','🌸','🍁','🍀','🎏','🐙','🐧','🐨','🐳','🐼','👻','👾'])
    text = sml[message.date % len(sml)]
    bot.send_message(message.chat.id, text, parse_mode='Markdown')

if __name__ == '__main__':
    while True:
        try:
            bot.polling(none_stop=True)
        except Exception:
            print('error Exception')
