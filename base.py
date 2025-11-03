from os.path import expanduser
import sqlite3
import datetime

home = expanduser('~')

open(home+'/databases/base.db','w+')
connection = sqlite3.connect(home + '/databases/base.db')
cursor = connection.cursor()

cursor.execute('''
CREATE TABLE IF NOT EXISTS data (
    Id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    Name TEXT,
    Small_Status TEXT,
    Date DATETIME,
    Chat_Id INTEGER,
    Description TEXT
)
''')

def add_ivent():
    name = input('Введите название события, которое хотите добавить: ')
    print(f'Добавлено событие: {name}')
    importance = ['Срочно', 'Средняя срочность', 'Не срочно']
    while True:
        importance_ask = input('Выберете срочность (1 - cрочно, 2 - средняя срочность, 3 - не срочно): ')
        try:
            index = int(importance_ask) - 1
            small_status = importance[index]
            print(f'Срочность: "{small_status}" ')
            break
        except (IndexError, ValueError):
            print('Введите корректный вариант срочности (1,2 или 3)')
    while True:
        date_input = input('Введите дату события в формате (дд/мм/гггг): ')
        try:
            date = datetime.datetime.strptime(date_input,'%d/%m/%Y').timetuple()
            print(f"Установлена дата: {date_input}")
            break
        except ValueError:
            print("Неверный формат даты, используйте формат 'дд/мм/гггг'")
    chat_id = 430074484
    description = input('Введите описание события: ')
    print(f"Описание: {description}")
    cursor.execute(f'''
    INSERT INTO data (Name,Small_Status,Date,Chat_Id,Description) 
     VALUES ('{name}', '{small_status}', '{date}', {chat_id}, '{description}');
    ''')

def name_search():
    search_name_input = input('Введите название события, которое хотите найти: ')
    cursor.execute(f'''
    SELECT * FROM data WHERE Name LIKE '%{search_name_input}%';
''')
    results = cursor.fetchall()
    if results:
        for line in results:
            print(line)
    else:
        print('Событие не найдено')

def description_search():
    search_description_input = input('Введите описание события, которое хотите найти: ')
    cursor.execute(f'''
    SELECT * FROM data WHERE Description LIKE '%{search_description_input}%';
''')
    results = cursor.fetchall()
    if results:
        for line in results:
            print(line)
    else:
        print('Событий с таким описанием не найдено')

def show_important_ivents():
    cursor.execute(f'''
SELECT * FROM data WHERE Small_Status LIKE '%{"Срочно"}%';
''')
    results = cursor.fetchall()
    if results:
        for line in results:
            print(line)
    else:
        print('Срочных событий не найдено')

def show_near_ivents():
    today = datetime.datetime.now()
    start_date = today - datetime.timedelta(days=7)
    start_date_str = str(start_date)
    start_date_str = start_date_str[:10]
    end_date = today + datetime.timedelta(days=7)
    end_date_str = str(end_date)
    end_date_str = end_date_str[:10]
    cursor.execute(f'''
SELECT * FROM data WHERE Date BETWEEN '{start_date_str}' AND '{end_date_str}';
''')
    results = cursor.fetchall()
    if results:
        for line in results:
            print(line)
    else:
        print('Событий в ближайшее время не запланировано')
connection.commit()
