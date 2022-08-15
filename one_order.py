import telebot
from telebot import types
import itertools
import json
import re
import config

bot = telebot.TeleBot(config.token)
# Ниже напиши свой ID группу в телеграмме
GROUP_ID = ''


def get_all_buttons(): #функция для создания из файла json всех кнопак
    with open('content.json', encoding='utf-8') as f:
        config_data = json.load(f)
    all_buttons = []
    for keyboard in config_data:
        for button in keyboard['buttons']:
            all_buttons.append(button)
    return all_buttons


def get_keyboard(keyboard_type):
    with open('content.json', encoding='utf-8') as f:
        config_data = json.load(f)
    kb_info = list(filter(lambda el: el['keyboard_name'] == keyboard_type, config_data))[0]
    buttons = sorted(kb_info['buttons'], key=lambda el: int(el['position']))
    keyboard = types.InlineKeyboardMarkup()
    chunked = list(itertools.zip_longest(*[iter(buttons)] * 1))
    for chunk in chunked:
        chunked_btn = []
        for button in list(filter(lambda el: el is not None, chunk)):
            chunked_btn.append(
                types.InlineKeyboardButton(button['name'],
                                           callback_data=button['id'])
            )
        if len(chunked_btn) == 1:
            keyboard.row(chunked_btn[0])
    return keyboard


def generate_id(button):# функция для генерации id нужной группы
    global GROUP_ID
    GROUP_ID = config.GROUP_ID[int(button)]
    return GROUP_ID


def generate_message(button): #функция для создания сообщение после нажатия кнопки
    msg = ""
    if 'link' in button and 'link_id' in button:
        msg += '<b> %s </b>\n' % button['name']
        msg += '<b>Ссылка на чат: %s</b>' % str(button['link'])
    msg += button['to_print'] + '\n'
    return msg


@bot.message_handler(commands=['start'])#Запуск бота, команда start
def start(message):
    bot.send_message(message.chat.id,
                     'Привет, %s!' % message.from_user.full_name,
                     reply_markup=get_keyboard('main')
                     )


@bot.message_handler(commands=['off'])#Остановка бота, команда off
def end(message):
    bot.send_message(message.chat.id,
                     'До свидание, ваш вопрос не отправлен, он нарушает правило! %s!' % message.from_user.full_name)
    bot.polling(none_stop=False, interval=0)


@bot.message_handler(commands=['send'])#Команда отправки сообщения в группу телеграмм
def send(message):
    with open('info.txt', encoding='utf-8') as f:
        s = f.readlines()
    txt = ""
    for i in s:
        txt +=i
    if re.findall("(?P<url>https?://[^\s]+)", txt):# проверка на присуствия в тексте ссылки
        bot.send_message(chat_id=message.chat.id, text=end(message), parse_mode='html')
    elif re.findall(r"((8|\+7)[\- ]?)?(\(?\d{3}\)?[\- ]?)?[\d\- ]{7,10}", txt):# проверка на присуствия в тексте телефона
        bot.send_message(chat_id=message.chat.id, text=end(message), parse_mode='html')
    else:
        to_send_message = '<b>%s</b>\n\n' % txt
        to_send_message += 'Этот вопрос выложен у нас на канале (ссылка на канал).\nC помощью @zadam_vopros_bot\nМы Вконтакте: https://vk.com/shugaring_forum\nПо рекламе: @alina_tech'
        bot.send_message(GROUP_ID, to_send_message, parse_mode='html')


@bot.message_handler(content_types=['text'])# сохранения вопроса отправленого боту
def direct_message(msg):
    f = open('info.txt', 'w', encoding='utf-8')
    f.write(msg.text)
    f.close()


@bot.callback_query_handler(func=lambda call: True)#нажатие кнопок
def keyboard_answer(call):
    button = list(filter(lambda btn: call.data == btn['id'], get_all_buttons()))[0]
    if button['id'] == "2":
        keyboard = types.InlineKeyboardMarkup()
        keyboard.add(types.InlineKeyboardButton("Заказать рекламу", url="https://t.me/alina_tech"))
        bot.send_message(
            chat_id=call.message.chat.id,
            text="Отлично просто нажми на кнопку",
            reply_markup=keyboard,
            parse_mode='html'
        )
    elif button['id'] == "3":
        keyboard = types.InlineKeyboardMarkup()
        keyboard.add(types.InlineKeyboardButton("Основной канал", url="https://t.me/reklama_chats"))
        bot.send_message(
            chat_id=call.message.chat.id,
            text="Отлично просто нажми на кнопку",
            reply_markup=keyboard,
            parse_mode='html'
        )
    elif button['id'] == "1":
        bot.send_message(
            chat_id=call.message.chat.id,
            text=generate_message(button),
            reply_markup=get_keyboard(button['next_keyboard']),
            parse_mode='html'
        )
    elif button['id'] == "15":
        keyboard = types.ReplyKeyboardMarkup()
        keyboard.add(types.KeyboardButton("/send"))
        bot.send_message(
            chat_id=call.message.chat.id,
            text="Напишите, пожалуйста, свой вопрос одним сообщением.\nЕсли захотите сформулировать вопрос по другому, \
            можете отправить новым сообщением до нажатия кнопки /send , \
            после нажатия кнопки вопрос будет отправлен в чат и изменить его нельзя.",
            reply_markup=keyboard,
            parse_mode='html'
        )
    else:
        generate_id(button['link_id'])
        bot.send_message(
            chat_id=call.message.chat.id,
            text=generate_message(button),
            reply_markup=get_keyboard(button['next_keyboard']),
            parse_mode='html'
        )


bot.polling(none_stop=True, interval=0)