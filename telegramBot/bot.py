from pickle import TRUE
import telebot
from telebot import types
from config import tokens
import re
import requests
bot = telebot.TeleBot(tokens['token'])
import random
import json
import time


# команда-помощник
@bot.message_handler(commands=['start', 'help'])
def help(message):
    help_string = 'Это бот, позволяет получить новостной дайджест или тренды и инстайты в новостях.\n\n' \
                  'Выберите, что вы хотите получить:'\
                #   '<strong>Список команд</strong>\n' \
                #   '/orders - получить список активных заказов\n' \
                #   '/?  (? - код заказа) - получить заказ по его коду'

    markup = types.ReplyKeyboardMarkup(resize_keyboard= True)
    item1 = types.KeyboardButton("Тренды и инсайты 💯")
    item2 = types.KeyboardButton("Новостной дайджест 📰")
    markup.add(item1)
    markup.add(item2)
    bot.send_message(message.chat.id, help_string, parse_mode='html', reply_markup= markup)



@bot.message_handler(content_types=['text'])
def bot_message(message):
    if message.chat.type == 'private':

        if message.text == 'Тренды и инсайты 💯':
            markup = types.ReplyKeyboardMarkup(resize_keyboard= True)
            item1 = types.KeyboardButton("Бухгалтер 📝")
            item2 = types.KeyboardButton("Гендиректор 🤵🏿")
            item3 = types.KeyboardButton("Отправить запрос в постмодерацию ➕")
            item4 = types.KeyboardButton("Назад 🔙")
            markup.add(item1)
            markup.add(item2)
            markup.add(item3)
            markup.add(item4)
            bot.send_message(message.chat.id, 'Тренды и инсайты:', parse_mode='html', reply_markup= markup)

        elif message.text == 'Новостной дайджест 📰':
            # time.sleep(1.5)
            # str = f'ВС РФ: если прежний принципал не расторг договор, новый может требовать от агента вернуть долг.\nСуды ошибочно посчитали, что: до обращения компании к агенту у юрлица не появилось право требовать возврата средств, поскольку оно не отказалось от договора и не потребовало от агента возврата денег;\nиз-за этого компания получила по договору цессии несуществующее право'\
            #     f'\n\nРасходы на содержание простаивающего здания за счет ОМС суд признал нецелевыми.\nКонтролеры и суд напомнили: по правилам ОМС затраты на содержание недвижимости относят к необходимым, только если ее используют при оказании медпомощи'
           
            # bot.send_message(message.chat.id, str, parse_mode='html')
            bot.send_message(message.chat.id, "Для бухгалтера:", parse_mode='html')
            requestbOOKERNews(message)
            bot.send_message(message.chat.id, "Для гендиректора:", parse_mode='html')
            requestGENDIRNews(message)


        if message.text == 'Бухгалтер 📝':
            bot.send_message(message.chat.id, 'Ваш запрос отправлен, ожидайте ответа', parse_mode='html')
            requestbOOKER(message)

        elif message.text == 'Гендиректор 🤵🏿':
            bot.send_message(message.chat.id, 'Ваш запрос отправлен, ожидайте ответа', parse_mode='html')
            requestGENDIR(message)

        elif message.text == 'Отправить запрос в постмодерацию ➕':
            

            keyboard = types.InlineKeyboardMarkup()
            key = types.InlineKeyboardButton(text = "Добавить роль", callback_data= f"role {message.chat.id}")
            key1 = types.InlineKeyboardButton(text = "Добавить источник", callback_data= f"url  {message.chat.id}")
            key2 = types.InlineKeyboardButton(text = "Добавить csv файл", callback_data= f"csv {message.chat.id}")
            key3 = types.InlineKeyboardButton(text = "Начальное меню 🔙", callback_data= f"back  {message.chat.id}")
            keyboard.add(key)
            keyboard.add(key1)
            keyboard.add(key2)
            keyboard.add(key3)
            bot.send_message(message.chat.id, f"Ваберите действие:", reply_markup=keyboard)

        elif message.text == 'Назад 🔙':
            help_string = 'Это бот, который позволит вам получить тренды по роли.\n\n' \
                          'Введите свою роль, либо выберите любую из списка'\
            
            markup = types.ReplyKeyboardMarkup(resize_keyboard= True)
            item1 = types.KeyboardButton("Тренды и инсайты 💯")
            item2 = types.KeyboardButton("Новостной дайджест 📰")
            markup.add(item1)
            markup.add(item2)
            bot.send_message(message.chat.id, help_string, parse_mode='html', reply_markup= markup)



# функция для обработки кнопок
@bot.callback_query_handler(func=lambda call: True)
def callback_worker(call):

    state = call.data.split()[0]
    if state == "back":

        help_string = 'Это бот, который позволит вам получить тренды по роли.\n\n' \
                          'Введите свою роль, либо выберите любую из списка'\
            
        markup = types.ReplyKeyboardMarkup(resize_keyboard= True)
        item1 = types.KeyboardButton("Тренды и инсайты 💯")
        item2 = types.KeyboardButton("Новостной дайджест 📰")
        markup.add(item1)
        markup.add(item2)
        bot.send_message(call.message.chat.id, help_string, parse_mode='html', reply_markup= markup)

    elif state == "role":
        
        msg = bot.send_message(call.message.chat.id, 'Введите роль:')
        bot.register_next_step_handler(msg, roleInput)
    
    elif state == "url":
        
        msg = bot.send_message(call.message.chat.id, 'Введите ссылку на источник:')
        bot.register_next_step_handler(msg, urlInput)
    
    elif state == "csv":
        
        msg = bot.send_message(call.message.chat.id, 'Отправьте csv файл:')
        bot.register_next_step_handler(msg, csvInput)


def roleInput(message):
    if(validateRole(message.text) == True):
        tmp = "Роль " + message.text + f" была отправлена на рассмотрение в постмодерацию\n" + "Если роль будет одобрена, она будет отображаться при получении трендов и инсайтов"
        bot.send_message(message.chat.id, tmp, parse_mode='html')
    else:
        bot.send_message(message.chat.id, "Роль введена не корректно", parse_mode='html')

def urlInput(message):
    if(validateURL(message.text) == True):
        tmp = "Источник  " + message.text + f" был отправлен на рассмотрение в постмодерацию\n" + "Если источник будет одобрен, то он будет добавлен в список используемых ресурсов"
        bot.send_message(message.chat.id, tmp, parse_mode='html')
    else:
        bot.send_message(message.chat.id, "Ссылка на источник введена не корректно", parse_mode='html')

def csvInput(message):
    tmp = "Файл  " +  f"был отправлен на рассмотрение в постмодерацию\n" + "Если файл будет одобрен, то он будет добавлен в список используемых ресурсов"
    bot.send_message(message.chat.id, tmp, parse_mode='html')
    print(message.document)

def requestbOOKER(message):
    x = requests.get('http://localhost:8080/api/vi/trend', params={'role':'BOOKER', 'path':'https://ipfs.io/ipfs/QmUXoBGrZ52PtyEEzY7nxfiJmmm5MLcnWY2sZsQxMfq7d5?filename=df_buh_concat_ver5.csv'})
    data = getParseData(x.text)
    # time.sleep(1.5)
    # data = 'Trend: момент должник возникать обязательство'\
    #         f'\nInsight: ВС РФ подтвердил, какие убытки можно взыскать с госзаказчика, если закупку отменили по его вине'
    bot.send_message(message.chat.id, data, parse_mode='html')

def requestGENDIR(message):
    x = requests.get('http://localhost:8080/api/vi/trend', params={'role':'OWNER', 'path':'https://ipfs.io/ipfs/QmTfxxUbAmXTrmRXn4rnXqGXbWU1q1xLWdR5XyScdHG8Vo?filename=df_bus_concat_ver2.csv'})
    data = getParseData(x.text)
    # time.sleep(1.5)
    # data = 'Trend: россия открыться название'\
    #         f'\nInsight: Позднее Министерство промышленности и торговли России утвердило изменения в перечень товаров для параллельного импорта, добавив в него продукцию Siemens, BMW и LEGO'
    bot.send_message(message.chat.id, data, parse_mode='html')

def requestbOOKERNews(message):
    x = requests.get('http://localhost:8080/api/v1/digest', params={'role':'BOOKER', 'path':'https://ipfs.io/ipfs/QmUXoBGrZ52PtyEEzY7nxfiJmmm5MLcnWY2sZsQxMfq7d5?filename=df_buh_concat_ver5.csv'})
    data = getParseNews(x.text)
    # time.sleep(1.5)
    # data = 'Trend: момент должник возникать обязательство'\
    #         f'\nInsight: ВС РФ подтвердил, какие убытки можно взыскать с госзаказчика, если закупку отменили по его вине'
    bot.send_message(message.chat.id, data, parse_mode='html')

def requestGENDIRNews(message):
    x = requests.get('http://localhost:8080/api/v1/digest', params={'role':'OWNER', 'path':'https://ipfs.io/ipfs/QmTfxxUbAmXTrmRXn4rnXqGXbWU1q1xLWdR5XyScdHG8Vo?filename=df_bus_concat_ver2.csv'})
    data = getParseNews(x.text)
    # time.sleep(1.5)
    # data = 'Trend: россия открыться название'\
    #         f'\nInsight: Позднее Министерство промышленности и торговли России утвердило изменения в перечень товаров для параллельного импорта, добавив в него продукцию Siemens, BMW и LEGO'
    bot.send_message(message.chat.id, data, parse_mode='html')


def validateRole(role):
    if (re.match(r"([a-zA-zа-яА-Я]{3,15}){1}(\s[a-zA-zа-яА-Я]{3,15}\s){0,3}", role ) != None) and (len(role) < 30):
        return True
    else:
        return False

def validateURL(url):
    if (re.match(r"[-a-zA-Z0-9@:%_\+.~#?&\/=]{2,256}\.[a-z]{2,4}\b(\/[-a-zA-Z0-9@:%_\+.~#?&\/=]*)?", url ) != None):
        return True
    else:
        return False

def getParseData(JSONdata): 
    return (json.loads(JSONdata)["incites"][0]) + f'\n' + (json.loads(JSONdata)["incites"][1])

def getParseNews(JSONdata): 
    return (json.loads(JSONdata)["news"][0]) + f'\n' + (json.loads(JSONdata)["news"][1])







bot.polling(none_stop=True)
    