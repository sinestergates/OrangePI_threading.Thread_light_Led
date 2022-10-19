
import wiringpi
from tkinter import * #Tk, Label, Button, Frame, mainloop,messagebox
from threading import Thread
import time
from wiringpi import GPIO
import psycopg2
from configparser import ConfigParser
import threading
import csv
from loguru import logger
import datetime

now = datetime.datetime.now()

wiringpi.wiringPiSetup()


def light_on(light_pin: int or tuple):
    wiringpi.wiringPiSetup()
    wiringpi.pinMode(light_pin, GPIO.OUTPUT)
    wiringpi.digitalWrite((light_pin), GPIO.HIGH)

    # GPIO.cleanup(light_pin)
    print('light on: '+str(light_pin))


def light_off(light_pin: int or tuple):
    wiringpi.wiringPiSetup()
    wiringpi.pinMode(light_pin, GPIO.OUTPUT)
    wiringpi.digitalWrite((light_pin), GPIO.LOW)

    # GPIO.cleanup(light_pin)
    print('light off: '+str(light_pin))


# wiringpi.wiringPiSetup()
def flash(light_pin: int or tuple, sleep=0.25, count=3):
    # wiringpi.wiringPiSetup()

    for i in range(count):
        light_off(light_pin)

        time.sleep(sleep)
        light_on(light_pin)

        time.sleep(sleep)
    print(light_pin)

def load_list(file='list_scheme.csv'):
    """Получаем массив пинов из файла окружения"""
    with open(f"{file}") as fp:
        reader = csv.reader(fp, delimiter=",", quotechar='"')
        data_read = [row for row in reader]
        return data_read


def connect_db():
    """Установка связи с БД"""
    config = ConfigParser()
    config.read('db.inf')

    cn = psycopg2.connect(
        database=config.get('setting', 'database'),
        user=config.get('setting', 'user'),
        password=config.get('setting', 'password'),
        host=config.get('setting', 'host'),
        port=config.get('setting', 'port'),
    )

    return cn


def db_with_commit(response, params):
    """Функция запрос в базу с добавлением"""
    con = connect_db()
    cur = con.cursor()
    if params == '':
        cur.execute(response)
    else:
        cur.execute(response, params)

    con.commit()
    return cur


def run_query(query, params=''):
    """Функция запрос в базу без добавления"""
    try:
        con = connect_db()
        cur = con.cursor()

        if params == '':
            cur.execute(query)
        else:
            cur.execute(query, params)

        return cur.fetchall()
    except:
        pass


def logic_yelow_func(pins: list, rack_col: int, rack_row: int) -> tuple:
    '''Функция формирует правильную логику поиска по массиву'''

    def logic_search(num_first: int, num_second: int, use_minus=False) -> tuple:
        """Выношу общую логику, use_minus использовать минус или нет, а в остальном делаем кортеж из двух пинов для того что бы
        получить жёлтый цвет на лентах"""
        if use_minus == False:
            pin_tuple: tuple = (int(pins[int(rack_col) - 1][int(rack_row) + num_first]),
                                int(pins[int(rack_col) - 1][int(rack_row) + num_second]))
        else:
            pin_tuple: tuple = (int(pins[int(rack_col) - 1][int(rack_row) - num_first]),
                                int(pins[int(rack_col) - 1][int(rack_row) + num_second]))
        return pin_tuple

    if rack_row == 1:
        pin_tuple = logic_search(num_first=1, num_second=0, use_minus=True)

    if rack_row == 2:
        pin_tuple = logic_search(num_first=0, num_second=1)

    if rack_row == 3:
        pin_tuple = logic_search(num_first=1, num_second=2)

    if rack_row == 4:
        pin_tuple = logic_search(num_first=2, num_second=3)

    print(f'Пин номер :  {(pin)}, {now}')

    return pin_tuple


def logic_work_RideTheLight(array: list, color: int, file: str = 'list_scheme.csv') -> None:
    """Общая функция работы orangepi, конкретно запуск работы LED лент"""
    pins = load_list(file)
    print('pins', pins)
    now = datetime.datetime.now()
    rack_col = array[0][3]  # колонка
    rack_row = array[0][2]  # ярус
    print('rack_col', rack_col, rack_col)

    def slice_of_array(start: int, finish: int) -> pin(int or tuple):
        """Общую логику выношу в отдельную функцию делаем срез в массиве, и уже в срезе вызываем верные пины"""
        slice_ = pins[rack_col - 1][start:finish:2]

        pin = int(slice_[int(rack_row) - 1])
        flash(pin)
        return pin

    try:
        if color == 3:
            pin = logic_yelow_func(pins, rack_col, rack_row)
            flash(pin)

        if color == 2:
            pin = slice_of_array(start=1, finish=8)

        if color == 1:
            pin = slice_of_array(start=0, finish=7)

        print(f'Пин номер :  {(pin)}, {now}')



    except BaseException as eror:
        logger.add('debug.log', format='{time} {level} {message}')
        logger.debug(f'{eror}__rack_col:{rack_col} rack_row:{rack_row}(debug)')


def run_color_one(array: list) -> None:
    """Логика работы с стеллажом с одним цветом"""
    id_rack = load_list()
    print('light', array)
    """Формируем массив из двумерного делаем обыкновенный и собираем в верном порядке, 
    то есть массивами с колонками формата [[колонка А],[колонка Б] и тд.], [i:i+4] это
    срез списка, [i:i+4]for i in range(0, 16, 4) формирует вложенный список с колонками"""

    pin_arr = [[pin for i in id_rack for pin in i][i:i+4]for i in range(0, 16, 4)]
    print('run_color_one', pin_arr)
    rack_col = array[0][3] #колонка
    rack_row = array[0][2]  #ярус
    pin = pin_arr[int(rack_col)-1][int(rack_row)-1] #сам номер пина GPIO
    print(f'Пин номер : {(pin)}, {now}')
    """Запускаем мигание ленты"""
    b = int(pin)
    print('b',type(b))
    #flash(int(pin))
    """Удаляем данные из базы"""
    db_with_commit(f'DELETE FROM "Ligthing" WHERE id = {array[0][0]}',
                   '')

def check_color(array: list) -> None:
    """Проверка входных данных о цвете"""
    if array[0][5] == 1:  # зелёный
        logic_work_RideTheLight(array, color=1)
    if array[0][5] == 2:  # красный
        logic_work_RideTheLight(array, color=2)
    if array[0][5] == 3:

        logic_work_RideTheLight(array, file='list_scheme.csv', color=3)
    else:
        pass


def RideTheLight():
    """Основная функция-поток проверяющая базу на наличие данных"""
    print('проверяю наличие новых данных')
    while True:
        id_rack = load_list()

        lights = run_query(
            f'SELECT * FROM "Ligthing" WHERE "Rack_id" ={id_rack[2][0]}')  # id_rack[2][0]- это цифра последняя в файле с массивом пинов, id Стеллажа

        LightingSceme = run_query(f'select "LigthingScheme","ColNumber","RowNumber" from "Rack" where id = {id_rack[2][0]}')

        def run_color_three():
            print('lights', lights)

            check_color(lights)
            db_with_commit(f'DELETE FROM "Ligthing" WHERE id = {lights[0][0]}',
                           '')  # lights[0][0] - id записи в массиве из базы'''

        if not lights:  # проверяем не пустой ли массив
            pass
        else:
            if LightingSceme[0][2] < lights[0][2] or LightingSceme[0][1] < lights[0][3]:
                print('Данные о стеллаже не соответствуют заявленным')
                db_with_commit(f'DELETE FROM "Ligthing" WHERE id = {lights[0][0]}',
                               '')


            else:
                # проверка схемы работы orangepi
                run_color_three() if int(LightingSceme[0][0]) == 1 else run_color_one(
                    lights)  # тернарный оператор, выполняем run_color_three() если выражение TRUE

        time.sleep(0.5)


thread = threading.Thread(target=RideTheLight)
thread.start()
