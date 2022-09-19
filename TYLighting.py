# -*- coding: utf-8 -*-



# import RPi.GPIO as GPIO
#import wiringpi
from tkinter import * #Tk, Label, Button, Frame, mainloop,messagebox
from threading import Thread
import time
#from wiringpi import GPIO
import psycopg2
from configparser import ConfigParser
import threading
import csv
from loguru import logger
import datetime

'''wiringpi.wiringPiSetup()


def light_on(light_pin):
    wiringpi.wiringPiSetup()
    wiringpi.pinMode(light_pin, GPIO.OUTPUT)
    wiringpi.digitalWrite((light_pin), GPIO.HIGH)

    # GPIO.cleanup(light_pin)
    print(light_pin)


def light_off(light_pin):
    wiringpi.wiringPiSetup()
    wiringpi.pinMode(light_pin, GPIO.OUTPUT)
    wiringpi.digitalWrite((light_pin), GPIO.LOW)

    # GPIO.cleanup(light_pin)
    print(light_pin)


# wiringpi.wiringPiSetup()
def flash(light_pin, sleep=0.25, count=2):
    # wiringpi.wiringPiSetup()

    for i in range(count):
        light_off(light_pin)

        time.sleep(sleep)
        light_on(light_pin)

        time.sleep(sleep)
    print(light_pin)
'''
def load_list():
    with open("list.csv") as fp:
        reader = csv.reader(fp, delimiter=",", quotechar='"')
        data_read = [row for row in reader]
        return data_read


#list_pin = [[1, 12, 9, 2], [5, 0,6, 16], [11, 7, 13, 4], [10, 8, 15, 3]]
# list_pin=[[17,4,27,22],[10,9,5,6],[13,19,26,15],[21,16,20,21]]




def connect_db():
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
    con = connect_db()
    cur = con.cursor()
    if params == '':
        cur.execute(response)
    else:
        cur.execute(response, params)

    con.commit()
    return cur

def run_query(query, params = ''):
    con = connect_db()
    cur = con.cursor()

    if params == '':
        cur.execute(query)
    else:
        cur.execute(query, params)
    con.commit()
    return cur.fetchall()


def RideTheLight(name_table):
    print('проверяю наличие новых данных')
    while True:
        a = run_query(f'SELECT * FROM "{name_table}"')

        if a == []:
            pass
        else:
            rack = 1  # по умолчанию ставлю стелаж пока 1 так как у нас только один
            now = datetime.datetime.now()
            rack_col = a[0][3]

            rack_row = a[0][2]

            try:
                pins=load_list()
                pin=pins[int(rack_col)-1][int(rack_row)-1]
                print(f'Пин номер : {int(pin)}, {now}')
            except BaseException as eror :
                logger.add('debug.log',format='{time} {level} {message}')
                logger.debug(f'{eror}__rack_col:{rack_col} rack_row:{rack_row}(debug)')
                #print(f'rack_col:{rack_col} rack_row:{rack_row}')

            #flash(int(pin))
            db_with_commit(f'TRUNCATE "{name_table}"', '')

        time.sleep(0.5)


thread = threading.Thread(target=RideTheLight, args=("Ligthing",))
thread.start()







