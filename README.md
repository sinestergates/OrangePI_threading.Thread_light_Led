# OrangePI_threading.Thread_light_Led
''' Проект под OrangePI реализован отдельный поток для проверки таблицы в БД Postgres.Если в таблице появляется запись, то Orange включает контакт GPIO
и соответственно открывает нужное реле, к реле в данном случае подключается LED лента, но можно всё что угодно.
Также используется файл настроек доступа к базе данных и загрузка данных о массиве Gpio контактов расставленных в иерархической цепочке, то есть в нужной вам последовательности

Так же используется логирование ошибок LOGURU'''
