import sqlite3
import requests
from bs4 import BeautifulSoup
from datetime import datetime


def create_table() -> None:
    """
    Создание новой таблицы в базе данных
    :return:
    """

    connection = sqlite3.connect('schedule_db.sqlite')
    cursor = connection.cursor()

    cursor.execute('''
        CREATE TABLE Schedule(
            id INTEGER NOT NULL PRIMARY KEY,
            WeekID TEXT NOT NULL,
            WeekFirstDay TEXT NOT NULL,
            DayOfWeek TEXT NOT NULL,
            NumOfLesson TEXT NOT NULL,
            NameOfGroup TEXT NOT NULL,
            Subgroup TEXT,
            Subject TEXT NOT NULL,
            TypeOfSubject TEXT NOT NULL,
            Teacher TEXT NOT NULL,
            Classroom TEXT NOT NULL,
            OnlineCheck BIT NOT NULL
        )''')

    connection.commit()
    connection.close()


def insert_to_db(row: list) -> None:
    """
    Добавление строки из таблицы в базу данных schedule_db.sqlite
    :param row:
    :return:
    """
    try:
        create_table()
    except:
        pass
    connection = sqlite3.connect('schedule_db.sqlite')
    cursor = connection.cursor()

    cursor.execute('''
        SELECT * 
        FROM Schedule
        WHERE WeekID=? and WeekFirstDay = ? and DayOfWeek=? and NumOfLesson=? and NameOfGroup=? and  Subgroup=? 
        and Subject=? and TypeOfSubject =? and Teacher =? and Classroom =? and OnlineCheck = ?
        ''', (row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9], row[10]))
    if cursor.fetchone():
        pass
    else:
        cursor.execute('''
            INSERT INTO Schedule (WeekID, WeekFirstDay, DayOfWeek, NumOfLesson, NameOfGroup, Subgroup,
            Subject, TypeOfSubject, Teacher, Classroom, OnlineCheck)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9], row[10]))
        # print(row)
    connection.commit()
    connection.close()


def find_by_classroom(week_first_day: str, classroom: str) -> list:
    """
    Вывод в терминал расписания по заданной аудитории
    :param week_first_day:
    :param classroom:
    :return:
    """
    try:
        connection = sqlite3.connect('schedule_db.sqlite')
        cursor = connection.cursor()

        cursor.execute('''
            SELECT DayOfWeek, NumOfLesson,
            Subject, TypeOfSubject, NameOfGroup, Teacher
            FROM schedule
            WHERE WeekFirstDay=? and Classroom=?
        ''', (week_first_day, classroom))
        week = cursor.fetchall()
        connection.commit()
        connection.close()
        prev_day = ''
        for i in week:
            if prev_day != i[0]:
                prev_day = i[0]
                print('-' * 104)
            print('|', i[0].center(4), '|', i[1], '|', i[2].center(45), '|',
                  i[3].center(10), '|', i[4].center(15), '|', i[5].center(10), '|')
            prev_day = i[0]
        print('-' * 104)
        return week
    except:
        print('Не удалось считать данные недели по группе')


def find_by_teacher(week_first_day: str, teacher: str) -> list:
    """
    Вывод в терминал расписания по заданному преподавателю
    :param week_first_day:
    :param teacher:
    :return:
    """
    try:
        connection = sqlite3.connect('schedule_db.sqlite')
        cursor = connection.cursor()

        cursor.execute('''
            SELECT DayOfWeek, NumOfLesson,
            Subject, TypeOfSubject, NameOfGroup, Classroom
            FROM schedule
            WHERE WeekFirstDay=? and Teacher=?
        ''', (week_first_day, teacher))
        week = cursor.fetchall()
        connection.commit()
        connection.close()
        prev_day = ''
        for i in week:
            if prev_day != i[0]:
                prev_day = i[0]
                print('-' * 104)
            print('|', i[0].center(4), '|', i[1], '|', i[2].center(45), '|',
                  i[3].center(10), '|', i[4].center(15), '|', i[5].center(10), '|')
            prev_day = i[0]
        print('-' * 104)
        return week
    except:
        print('Не удалось считать данные недели по группе')


def find_by_group(week_first_day: str, name_of_group: str) -> list:
    """
    Вывод в терминал расписания по заданной группе
    :param week_first_day:
    :param name_of_group:
    :return:
    """
    try:
        connection = sqlite3.connect('schedule_db.sqlite')
        cursor = connection.cursor()

        cursor.execute('''
            SELECT DayOfWeek, NumOfLesson,
            Subject, TypeOfSubject, Teacher, Classroom
            FROM schedule
            WHERE WeekFirstDay=? and NameOfGroup=?
        ''', (week_first_day, name_of_group))
        week = cursor.fetchall()
        connection.commit()
        connection.close()
        prev_day = ''
        for i in week:
            if prev_day != i[0]:
                prev_day = i[0]
                print('-' * 104)
            print('|', i[0].center(4), '|', i[1], '|', i[2].center(45), '|',
                  i[3].center(10), '|', i[4].center(15), '|', i[5].center(10), '|')
            prev_day = i[0]
        print('-' * 104)
        return week
    except:
        print('Не удалось считать данные недели по группе')


def delete_from_db(week_id: str) -> None:
    """
    Удаление всех записей по заданной неделе
    :param week_id:
    :return:
    """
    connection = sqlite3.connect('schedule_db.sqlite')
    cursor = connection.cursor()

    cursor.execute('''
            DELETE FROM Schedule 
            WHERE WeekID = ?
    ''', (week_id,))

    connection.commit()
    connection.close()


def parser(week_id: list) -> None:
    """
    Парсинг расписания с сайта и занесение его в базу данных
    :param week_id:
    :return:
    """
    week = week_id  # id недели
    try:
        delete_from_db(week[0])
    except:
        pass
    authorise = requests.post('http://scs.sarfti.ru/login/index',
                              data={'login': '', 'password': '', 'guest': 'Войти как гость'})
    page_of_table = requests.post('http://scs.sarfti.ru/date/printT',
                                  data={'id': week[0], 'show': 'Распечатать', 'list': 'list',
                                        'compact': 'compact'},
                                  cookies=authorise.history[0].cookies)
    page_of_table.encoding = 'utf-8'
    soup = BeautifulSoup(page_of_table.text, 'html.parser')
    table = soup.find('table', class_="load tablesorter list")
    t_body = table.find('tbody')
    list_of_rows = t_body.findAll('tr')
    for row in list_of_rows:
        list_of_cells = row.findAll('td')
        for i in range(len(list_of_cells)):
            list_of_cells[i] = list_of_cells[i].text
        list_of_cells = week_id + list_of_cells
        if 'ОНЛАЙН' in list_of_cells[-1]:
            list_of_cells.append('1')
        elif 'Онлайн' in list_of_cells[-1]:
            list_of_cells.append('1')
        else:
            list_of_cells.append('0')
        insert_to_db(list_of_cells)
    # with open('Table.txt', 'w') as file:
    #     file.write(str(t_body))


def parse_week_id() -> list:
    """
    Получение списка доступных недель с сайта scs.sarfti.ru
    :return:
    """
    authorise = requests.post('http://scs.sarfti.ru/login/index',
                              data={'login': '', 'password': '', 'guest': 'Войти как гость'})
    page_of_table = requests.post('http://scs.sarfti.ru/date/printT',
                                  cookies=authorise.history[0].cookies)
    page_of_table.encoding = 'utf-8'
    soup = BeautifulSoup(page_of_table.text, "html.parser")
    select = soup.find('select')
    list_of_week_id = []
    for i in select.findAll('option'):
        l_i = str(i).split('"')
        list_of_week_id.append([l_i[1], i.text])
    return list_of_week_id


start = datetime.now()

# for i in parse_week_id():
#     parser(i)
# parser(["316", '2023-10-23'])
find_by_group('2023-10-23', 'ИТ-31')
print(30 * "*")
find_by_teacher('2023-10-23', 'Чернявский В.П.')
print(30 * "*")
find_by_classroom('2023-10-23', 'к2,113')

print(datetime.now() - start)
