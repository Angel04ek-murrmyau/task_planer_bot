import telebot
from telebot import types
from os.path import expanduser
import datetime
import sqlite3
import threading
import dotenv
import os

dotenv.load_dotenv()
TOKEN=os.getenv("TOKEN")
home = expanduser('~')
bot = telebot.TeleBot(TOKEN)
open(home+'/databases/base.db','w+')
connection = sqlite3.connect(home + '/databases/base.db',check_same_thread=False)
cursor = connection.cursor()

cursor.execute('''
CREATE TABLE IF NOT EXISTS data (
    Id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    Name TEXT,
    Small_Status TEXT,
    Date TEXT,
    Chat_Id INTEGER,
    Description TEXT
)
''')
cursor.execute('''
CREATE TABLE IF NOT EXISTS users (
Chat_id INTEGER PRIMARY KEY
)
''')
@bot.message_handler(commands=['start'])
def start(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)

    btn_add_ivent = types.KeyboardButton('Добавить событие')
    btn_name_search = types.KeyboardButton('Поиск события по названию')
    btn_description_search = types.KeyboardButton('Поиск события по описанию')
    btn_show_important_ivents = types.KeyboardButton('Показать важные события')
    btn_show_near_ivents = types.KeyboardButton('Показать ближайшие события')

    markup.add(btn_add_ivent, btn_name_search, btn_description_search, btn_show_important_ivents, btn_show_near_ivents)

    bot.send_message(message.chat.id,f'Привет {message.from_user.first_name}! Это бот, который поможет в планировании и распределении ваших задач. Чтобы начать, выберите одно из возможных действий:', reply_markup=markup)

    cursor.execute(f'''
        INSERT OR IGNORE INTO users (Chat_Id) 
        VALUES ({message.chat.id})
    ''')


def check_message_text(message):
    return message.text in [
        'Добавить событие',
        'Поиск события по названию',
        'Поиск события по описанию',
        'Показать важные события',
        'Показать ближайшие события'
    ]


def add_ivent(message):
    ivent_name = bot.send_message(message.chat.id, 'Введите название события, которое хотите добавить:')
    bot.register_next_step_handler(ivent_name, process_ivent_name)


def process_ivent_name(message):
    ivent_name = message.text
    bot.send_message(message.chat.id, f'Название события: {ivent_name}')

    date_input = bot.send_message(message.chat.id, 'Введите дату события в формате (дд/мм/гггг чч:мм): ')
    bot.register_next_step_handler(date_input, process_date, ivent_name)


def process_date(message, ivent_name):
    try:
        ivent_date = datetime.datetime.strptime(message.text, '%d/%m/%Y %H:%M').strftime('%d/%m/%Y %H:%M')
        bot.send_message(message.chat.id, f'Установлена дата: {ivent_date}')
        importance_ask = bot.send_message(message.chat.id, 'Выберите срочность (1 - срочно, 2 - средняя срочность, 3 - не срочно): ')
        bot.register_next_step_handler(importance_ask, process_importance, ivent_name, ivent_date)
    except ValueError:
        bot.send_message(message.chat.id, 'Неверный формат даты, используйте формат "(дд/мм/гггг чч:мм)"')
        date_input = bot.send_message(message.chat.id,'Введите дату события в формате (дд/мм/гггг чч:мм): ')
        bot.register_next_step_handler(date_input, process_date, ivent_name)


def process_importance(message, ivent_name, ivent_date):
    importance = ['Срочно', 'Средняя срочность', 'Не срочно']
    try:
        index = int(message.text) - 1
        small_status = importance[index]
        bot.send_message(message.chat.id, f'Срочность: "{small_status}" ')

        description = bot.send_message(message.chat.id, 'Введите описание события:')
        bot.register_next_step_handler(description, process_description, ivent_name, small_status, ivent_date)
    except (IndexError, ValueError):
        bot.send_message(message.chat.id, 'Введите корректный вариант срочности (1, 2 или 3): ')
        importance_ask = bot.send_message(message.chat.id,'Выберите срочность (1 - срочно, 2 - средняя срочность, 3 - не срочно): ')
        bot.register_next_step_handler(importance_ask, process_importance, ivent_name, ivent_date)


def process_description(message, ivent_name, small_status, ivent_date):
    description = message.text
    bot.send_message(message.chat.id, f"Описание: {description}")
    chat_id = message.chat.id
    cursor.execute(f'''
                INSERT INTO data (Name, Small_Status, Date, Chat_Id, Description) VALUES ('{ivent_name}', '{small_status}', '{ivent_date}', {chat_id}, '{description}');
            ''')
    connection.commit()
    bot.send_message(message.chat.id, f'Cобытие успешно добавлено: \n Название: {ivent_name} \n Срочность: {small_status} \n Дата: {ivent_date} \n Описание: {description}')


def name_search(message):
    name = bot.send_message(message.chat.id, 'Введите название события, которое хотите найти: ')
    bot.register_next_step_handler(name, process_name_search)


def process_name_search(message):
    name_for_searching = message.text
    try:
        cursor.execute(f'''
            SELECT * FROM data WHERE Name LIKE '%{name_for_searching}%';
            ''')
        results = cursor.fetchall()
        if results:
            for row in results:
                bot.send_message(message.chat.id,f"Название: {row[1]} \n Срочность: {row[2]} \n Дата: {row[3]} \n Описание: {row[5]}")
        else:
            bot.send_message(message.chat.id, 'Событий с таким названием не найдено')
    except sqlite3.Error:
        bot.send_message(message.chat.id, f"Ошибка базы данных")


def description_search(message):
    description = bot.send_message(message.chat.id, 'Введите описание события, которое хотите найти: ')
    bot.register_next_step_handler(description, process_description_search)


def process_description_search(message):
    descripton_for_searching = message.text
    try:
        cursor.execute(f'''
            SELECT * FROM data WHERE Description LIKE '%{descripton_for_searching}%';
            ''')
        results = cursor.fetchall()
        if results:
            for row in results:
                bot.send_message(message.chat.id,f"Название: {row[1]} \n Срочность: {row[2]} \n Дата: {row[3]} \n Описание: {row[5]}")
        else:
            bot.send_message(message.chat.id, 'Событий с таким описанием не найдено')
    except sqlite3.Error:
        bot.send_message(message.chat.id, f"Ошибка базы данных")


def show_important_events(message):
    cursor.execute(f'''
        SELECT * FROM data WHERE Small_Status LIKE '%{"Срочно"}%';
        ''')
    results = cursor.fetchall()
    if results:
        for row in results:
            bot.send_message(message.chat.id,f"Название: {row[1]} \n Срочность: {row[2]} \n Дата: {row[3]} \n Описание: {row[5]}")
    else:
        bot.send_message(message.chat.id, 'Срочных событий не найдено')


def show_near_events(message):
    today = datetime.date.today()
    start_date = today - datetime.timedelta(days=7)
    start_date_str = start_date.strftime('%d/%m/%Y')
    end_date = today + datetime.timedelta(days=7)
    end_date_str = end_date.strftime('%d/%m/%Y')
    cursor.execute(f'''
            SELECT * FROM data WHERE DATE(Date) BETWEEN '{start_date_str}' AND '{end_date_str}';
        ''')
    results = cursor.fetchall()
    if results:
        for row in results:
            bot.send_message(message.chat.id,f"Название: {row[1]} \n Срочность: {row[2]} \n Дата: {row[3]} \n Описание: {row[5]}")
    else:
        bot.send_message(message.chat.id, 'Событий в ближайшее время не запланировано')


@bot.message_handler(func=check_message_text)
def handle_buttons(message):
    if message.text == 'Добавить событие':
        add_ivent(message)
    elif message.text == 'Поиск события по названию':
        name_search(message)
    elif message.text == 'Поиск события по описанию':
        description_search(message)
    elif message.text == 'Показать важные события':
        show_important_events(message)
    elif message.text == 'Показать ближайшие события':
        show_near_events(message)

def send_notifications():
    now = datetime.datetime.now()
    current_time = now.strftime('%d/%m/%Y %H:%M')
    cursor.execute(
        '''SELECT Chat_id FROM users'''
    )
    users = cursor.fetchall()
    for (chat_id,) in users:
        cursor.execute(f'''
                SELECT * FROM data 
                WHERE Date = '{current_time}' 
                AND Chat_Id = {chat_id}
            ''')
        results = cursor.fetchall()

        if results:
            for row in results:
                try:
                    bot.send_message(
                        chat_id,
                        f"Название: {row[1]}\n Срочность: {row[2]}\n Дата: {row[3]}\n Описание: {row[5]}"
                    )
                except Exception:
                    print(f"Ошибка")

def scheduler():
    while True:
        send_notifications()
        threading.Event().wait(60)

threading.Thread(target=scheduler, daemon=True).start()
bot.polling(non_stop=True)
connection.commit()
