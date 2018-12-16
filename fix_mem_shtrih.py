#! /usr/bin/python2.7
# -*- coding: utf-8 -*-
import pyshtrih
from datetime import datetime
from time import sleep


def color_red(text):
	text = '\x1b[31m' + text + '\x1b[0m'
	return(text)


def color_green(text):
	text = '\x1b[32m' + text + '\x1b[0m'
	return(text)


def color_yellow(text):
	text = '\x1b[33m' + text + '\x1b[0m'
	return(text)


def color_nn(text):
	text = '\x1b[36m' + text + '\x1b[0m'
	return(text)


def discovery_callback(port, baudrate):
	# print(port, baudrate)
	pass


def needs_value(text):
	dicts = text.params
	val = dicts['Значение'.decode('utf8')]
	return val



def read_needs_param(device):
	# Отрезчик чеков
	cut_chek = device.read_table(1, 1, 7, type(2))
	cut_chek = needs_value(cut_chek)
	print(u'Отрезчик чеков')
	print(cut_chek)

	# ДНС имя
	dns1 = device.read_table(16, 1, 15, type(2))
	dns2 = device.read_table(16, 1, 16, type(2))
	dns3 = device.read_table(16, 1, 17, type(2))
	dns4 = device.read_table(16, 1, 18, type(2))
	print(u'DNS')
	ip_dns = '.'.join([str(needs_value(x)) for x in [dns1, dns2, dns3, dns4]])
	print(ip_dns)

	# Место расчетов
	payment_state = device.read_table(18, 1, 14, type('a'))
	payment_state = needs_value(payment_state)
	print(u'payment_state')
	print(payment_state)

	# Оператор
	operator = device.read_table(18, 1, 8, type('a'))
	operator = needs_value(operator)
	print(u'operator')
	print(operator)

	# имя ОФД
	ofd_name = device.read_table(18, 1, 10, type('a'))
	ofd_name = needs_value(ofd_name)
	print(u'ofd_name')
	print(ofd_name)

	# Адрес ОФД
	ofd_url = device.read_table(18, 1, 11, type('a'))
	ofd_url = needs_value(ofd_url)
	print(u'ofd_url')
	print(ofd_url)

	# ИНН
	ofd_inn = device.read_table(18, 1, 12, type('a'))
	ofd_inn = needs_value(ofd_inn)
	print(u'ofd_inn')
	print(ofd_inn)

	# Сервер ОФД
	server_ofd = device.read_table(19, 1, 1, type('a'))
	server_ofd = needs_value(server_ofd)
	print(u'server_ofd')
	print(server_ofd)

	# Порт ОФД
	port_ofd = device.read_table(19, 1, 2, type(2))
	port_ofd = needs_value(port_ofd)
	print(u'port_ofd')
	print(port_ofd)

	# РНДИС
	rndis = device.read_table(21, 1, 9, type(2))
	rndis = needs_value(rndis)
	print(u'rndis')
	print(rndis)


def write_correct_value_in_tables(device):
	# Отрезчик чеков
	print(u'Отрезчик чеков')
	device.write_table(1, 1, 7, 2, int)

	device.beep()
	sleep(5)

	# # ДНС имя
	print(u'ДНС имя')
	device.write_table(16, 1, 15, 192, int)
	device.write_table(16, 1, 16, 168, int)
	device.write_table(16, 1, 17, 140, int)
	device.write_table(16, 1, 18, 253, int)

	device.beep()
	sleep(5)

	# Место расчетов
	print(u'Место расчетов')
	payment_state = device.read_table(18, 1, 14, str)
	payment_state = needs_value(payment_state)
	print(payment_state)

	device.beep()
	sleep(5)

	# Оператор
	print(u'Оператор')
	device.write_table(18, 1, 8, payment_state, str)

	device.beep()
	sleep(5)

	# имя ОФД
	print(u'имя ОФД')
	name = u'АО "Готичный Квас"'
	device.write_table(18, 1, 10, name, str)

	device.beep()
	sleep(5)

	# Адрес ОФД
	print(u'Адрес ОФД')
	adres = u'lk.ofd-gotic_kvas.ru'
	device.write_table(18, 1, 11, adres, str)

	device.beep()
	sleep(5)

	# ИНН
	print(u'ИНН')
	inn = u'260000175'
	device.write_table(18, 1, 12, inn, str)

	device.beep()
	sleep(5)

	# Сервер ОФД
	print(u'Сервер ОФД')
	server = u'kkt.ofd-gotic_kvas.ru'
	device.write_table(19, 1, 1, server, str)

	device.beep()
	sleep(5)

	# Порт ОФД
	print(u'Порт ОФД')
	device.write_table(19, 1, 2, 7001, int)

	device.beep()
	sleep(5)

	# РНДИС
	print(u'РНДИС')
	device.write_table(21, 1, 9, 1, int)
	device.beep()


def main():

	print(color_yellow(u'Добрый день!'))
	print(color_yellow(u'Это скрипт исправления ошибки "Ошибка ОЗУ" на ККМ Штрих'))
	text = 'Приступить к исправлению проблемы? (y/n):'
	answer = raw_input(color_nn(text))
	if answer.lower() == 'n':
		print(color_yellow(u'Видимо вами был выбран скрипт, справляющий не данную проблему'))
		exit()
	elif answer.lower() == 'y':
		print(u'Идет поиск ККМ')
		devices = pyshtrih.discovery(discovery_callback)	
	else:
		print(color_red(u'Из двух возможных вариантов вы ни один не ввели, скрипт заканчивает свою работу'))
		exit()
	# devices = pyshtrih.discovery(discovery_callback)

	if not devices:
		raise Exception(u'Device not fount')

	device = devices[0]
	# Подключаемся к ККМ
	device.connect()
	# Делаем технологическое обнуление
	print(u'* Делаем тех.обнуление')
	device.reset_settings()
	# Устанавливаем текущую дату
	print(u'* Устанавливаем корректную дату и время')
	now = datetime.now()
	device.set_datetime(now)
	# Инициируем таблицы
	print(u'* Инициализируем таблицы')
	device.init_table()
	# Выполняем общее гашение
	print(u'* Выполняем общее гашение')
	device.reset_summary()

	sleep(10)

	text = 'Приступить к заполнению таблиц корректными данныйми? (y/n): '
	answer = raw_input(color_nn(text))
	if answer.lower() == 'y':
		print(u'Выполняем заполнение таблиц корректными данными:')
		now = datetime.now()
		device.set_datetime(now)
		write_correct_value_in_tables(device)
	else:
		print(color_yellow(u'Таблицы остались не заполнены, вам необходимо их заполнить вручную'))
		device.disconnect()
		exit()
	text = 'Хотите считать с ККМ записанные данные? (y/n): '
	answer = raw_input(color_nn(text))
	if answer.lower() == 'y':
		print(u'Данные из таблиц:')
		read_needs_param(device)
	print(color_green(u'Проблема исправлена, необходимо перезагрузить ККМ.'))
	print(color_nn(u'После перезагрузки ККМ будет доступна по RNDIS'))
	device.disconnect()


if __name__ == '__main__':
	main()
