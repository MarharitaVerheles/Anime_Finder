import telebot
import requests
import time
from telebot import types
from model import recommendations_title, recommendations_by_description2, find_anime, get_description
from web_scraper import get_anime_pic

user_data = {}
bot = telebot.TeleBot('6157376204:AAGGfXQvutYJ3SSYjHcBpqFKLTbeMgcN_IY')

class UserData:
    def __init__(self, title='', user_input='', iteration=0, recommendations_list=None):
        self.title = title
        self.user_input = user_input
        self.iteration = iteration
        self.recommendations_list = recommendations_list

    def to_dict(self):
        return {'title': self.title, 'user_input': self.user_input,
                'iteration': self.iteration, 'recommendations_list': self.recommendations_list}

    @classmethod
    def from_dict(cls, data):
        return cls(data.get('title', ''), data.get('user_input', ''),
                   data.get('iteration', 0), data.get('recommendations_list', None))


@bot.message_handler(commands=["start"])
def start(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    item1 = types.KeyboardButton("Порекомендувати аніме за назвою")
    item2 = types.KeyboardButton("Порекомендувати аніме за описом")
    markup.add(item1, item2)
    bot.send_message(message.chat.id, "Я бот для пошуку аніме, спираючись на твої вподобання\n"
                                      "Натисни 'Порекомендувати аніме' щоб розпочати", reply_markup=markup)


@bot.message_handler(content_types='text')
def get_message(message):
    user_id = message.from_user.id
    if user_id not in user_data:
        user_data[user_id] = UserData()

    user_data[user_id].title = ''
    user_data[user_id].user_input = ''
    user_data[user_id].iteration = 0
    user_data[user_id].recommendations_list = None

    if message.text == "Порекомендувати аніме за назвою":
        msg = bot.send_message(message.chat.id, "Введіть назву аніме")
        bot.register_next_step_handler(msg, check_anime)

    elif message.text == "Порекомендувати аніме за описом":
        msg = bot.send_message(message.chat.id, "Введіть короткий опис аніме")
        bot.register_next_step_handler(msg, check_anime_by_description)

    else:
        bot.send_message(message.chat.id, 'Ви маєте натиснути кнопку.')


def check_anime_by_description(message):
    user_id = message.from_user.id
    if user_id in user_data:
        user_data[user_id].user_input = message.text
        user_data[user_id].recommendations_list = recommendations_by_description2(user_data[user_id].user_input)
        #recommendations_list = user_data[user_id].recommendations_list
        if user_data[user_id].recommendations_list:
            recommendations_formatted = ["{}. Назва: '{}', посилання: {}".format(
                index + 1, rec[0], rec[1]) for index, rec in
                enumerate(user_data[user_id].recommendations_list)]
            msg = '\n'.join(recommendations_formatted)
            bot.send_message(message.chat.id, text=msg)
            keyboard = types.InlineKeyboardMarkup()
            for index, recommendation in enumerate(user_data[user_id].recommendations_list):
                button = types.InlineKeyboardButton(
                    text=recommendation[0],
                    callback_data='details {} {}'.format(index, message.chat.id))
                keyboard.add(button)
            bot.send_message(message.chat.id, text='Виберіть аніме, про яке хочете дізнатися більше:',
                             reply_markup=keyboard)
        else:
            bot.send_message(message.chat.id, text="Нажаль, рекомендації не знайдені.")

def check_anime(message):
    user_id = message.from_user.id
    if user_id in user_data:
        user_data[user_id].user_input = message.text
        if user_data[user_id].title == '':
            user_data[user_id].title = find_anime(user_data[user_id].user_input, user_data[user_id].iteration)

        if user_data[user_id].title:
            keyboard = types.InlineKeyboardMarkup()
            key_stop = types.InlineKeyboardButton(text='Так, це те аніме', callback_data='stop')
            keyboard.add(key_stop)
            key_continue = types.InlineKeyboardButton(text='Ні, продовжуй пошук', callback_data='continue')
            keyboard.add(key_continue)
            bot.send_message(message.chat.id, 'Це те, що ви шукали {}?'.format(user_data[user_id].title),
                             reply_markup=keyboard)
        else:
            bot.send_message(message.chat.id, text="Більше нічого не знайдено.")



@bot.callback_query_handler(func=lambda call: True)
def callback_worker(call):
    user_id = call.from_user.id
    if user_id in user_data:
        if call.data == 'stop':
            user_data[user_id].recommendations_list = recommendations_title(user_data[user_id].title)
            recommendations_list = user_data[user_id].recommendations_list
            if user_data[user_id].recommendations_list:
                recommendations_formatted = [
                    "{}. Назва: '{}', посилання: {}".format(index + 1, rec[0], rec[1]) for index, rec in
                    enumerate(user_data[user_id].recommendations_list)]
                msg = '\n'.join(recommendations_formatted)
                bot.send_message(call.message.chat.id, text=msg)
                keyboard = types.InlineKeyboardMarkup()
                for index, recommendation in enumerate(user_data[user_id].recommendations_list):
                    name = recommendation[0]
                    button = types.InlineKeyboardButton(text=name, callback_data='details {} {}'.format(
                        index, call.message.chat.id))
                    keyboard.add(button)
                bot.send_message(call.message.chat.id, text='Виберіть аніме, про яке хочете дізнатися більше:',
                                 reply_markup=keyboard)
            else:
                bot.send_message(call.message.chat.id, text="Нажаль, рекомендації не знайдені.")

        elif call.data == 'continue':
            user_data[user_id].iteration += 1
            if user_data[user_id].iteration < 5:
                #user_data[user_id].iteration += 1
                user_data[user_id].title = find_anime(user_data[user_id].user_input, user_data[user_id].iteration)
                if user_data[user_id].title:
                    keyboard = types.InlineKeyboardMarkup()
                    key_stop = types.InlineKeyboardButton(text='Так, це те аніме', callback_data='stop')
                    keyboard.add(key_stop)
                    key_continue = types.InlineKeyboardButton(text='Ні, продовжуй пошук', callback_data='continue')
                    keyboard.add(key_continue)
                    bot.send_message(call.message.chat.id,
                                     'Це те, що ви шукали {}?'.format(user_data[user_id].title),
                                     reply_markup=keyboard)
            else:
                bot.send_message(call.message.chat.id, text="Більше нічого не знайдено.")

        elif call.data.startswith('details'):
            st = time.time()
            data = call.data.split(' ')
            if len(data) == 3:
                index = int(data[1])
                chat_id = int(data[2])
                recommendations_list = user_data[user_id].recommendations_list
                if recommendations_list:
                    selected_rec = recommendations_list[index]
                    image_url = get_anime_pic(selected_rec[1])
                    msg = get_description(selected_rec[0])
                    try:
                        bot.send_photo(chat_id, image_url, caption=msg)
                    except telebot.apihelper.ApiTelegramException as e:
                        if "message caption is too long":
                            short_message = msg[:1020] +'...'
                            bot.send_photo(chat_id, image_url, caption=short_message)
            else:
                bot.send_message(call.message.chat.id, text="Invalid callback data.")
            et = time.time()
            print("details: {}".format(et - st))

bot.polling()