import config
import telebot
import requests

import datetime
from telebot import types

bot = telebot.TeleBot(config.TOKEN)
HMS = '%H:%M:%S'


@bot.message_handler(commands=['start'])
def welcome(message):
    sticker = open('static/welcome.webp', 'rb')
    bot.send_sticker(message.chat.id, sticker)

    # keyboard
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    item_weather = types.KeyboardButton('Узнать погоду')
    item_time = types.KeyboardButton('Узнать время')

    markup.add(item_weather, item_time)

    bot.send_message(message.chat.id,
                     "Добро пожаловать, {0.first_name}!\nЯ - <b>{1.first_name}</b>.".format(message.from_user,
                                                                                            bot.get_me()),
                     parse_mode='html', reply_markup=markup)


@bot.message_handler(content_types=['text'])
def message_reply(message):
    if message.chat.type == 'private':
        if message.text == 'Узнать погоду':
            weather_msg = bot.send_message(message.chat.id, "Напиши город, в котором хочешь узнать погоду")
            # После выбора, вызов функции для узнавания погоды:
            bot.register_next_step_handler(weather_msg, get_weather)
        elif message.text == 'Узнать время':
            bot.send_message(message.chat.id, f"У вас сейчас: {datetime.datetime.now().strftime(HMS)}")


@bot.message_handler(content_types=['text'])
def get_weather(message):
    code_to_smile = {
        'Clear': 'Ясно \U00002600',
        'Clouds': 'Облачно \U00002601',
        'Rain': 'Дождь \U00002614',
        'Drizzle': 'Дождь \U00002614',
        'Thunderstorm': 'Гроза \U000026A1',
        'Snow': 'Снег \U0001F328',
        'Mist': 'Туман \U0001F328'
    }

    try:
        r = requests.get(
            f'http://api.openweathermap.org/data/2.5/weather?q={message.text}&appid={config.open_weather_token}'
            f'&units=metric'
        )
        data = r.json()

        city = data['name']
        cur_weather = data['main']['temp']

        weather_description = data['weather'][0]['main']
        if weather_description in code_to_smile:
            wd = code_to_smile[weather_description]
        else:
            wd = 'Даже не знаю, что за погода, может посмотришь в окно?'

        humidity = data['main']['humidity']
        wind = data['wind']['speed']

        markup = types.InlineKeyboardMarkup(row_width=2)
        item1 = types.InlineKeyboardButton('Указать другой город', callback_data='new_city')
        item2 = types.InlineKeyboardButton('Главное меню', callback_data='menu')
        markup.add(item1, item2)

        bot.send_message(message.chat.id, (f"***{datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}***\n"
                                           f"Погода в городе: {city}\nТемпература: {cur_weather} C° {wd}\n"
                                           f"Влажность: {humidity}%\nСкорость ветра: {wind}м/с"), reply_markup=markup
                         )

    except Exception:
        bot.send_message(message.chat.id, '\U00002620 Проверьте название города \U00002620')


@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
    try:
        if call.message:
            if call.data == 'new_city':
                msg = bot.send_message(call.message.chat.id, "Напиши город, в котором хочешь узнать погоду")
                bot.register_next_step_handler(msg, get_weather)
            elif call.data == 'menu':
                bot.send_message(call.message.chat.id, 'Вы в главном меню')

            # Убирает ТОЛЬКО инлайн кнопки. Сообщение остаётся
            bot.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                          reply_markup=None)

    except Exception as ex:
        print(repr(ex))


if __name__ == '__main__':
    bot.polling(none_stop=True)
