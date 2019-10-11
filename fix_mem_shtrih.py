# -*- coding: utf-8 -*-

import pyshtrih
from datetime import datetime
from time import sleep
import logging
from re import findall, MULTILINE

class fix_mem():
	def __init__(self):
		self.init_logs()
		self.wtf_type_oo()
		self.find_device()
		self.reset_settings()
		try:
			self.write_correct_value_in_tables()
			self.logger.info(u'Data write in table is successfully')
		except:
			self.logger.error(u'Data write in table is failed')
			self.logger.info(u'Process is crashed')
			exit()
		self.read_needs_param()
		self.logger.info(u'Like a boss')
		self.device.disconnect()
	
	def init_logs(self):
		# Включить логирование
		now = datetime.strftime(datetime.now(), '%Y-%m-%d_%H-%M-%S') 
		logging.basicConfig(format=u'[%(asctime)s] %(levelname)-8s %(message)s',
					level=logging.DEBUG, filename=u'/opt/memSH/shtrih_fix.log')
		self.logger = logging.getLogger(__name__)
		
		self.logger.info(u'Process is started')
	
	def wtf_type_oo(self):
		'''
		Определение типа объекта продаж
		'''
		linc_to_host = '/etc/hosts'
		with open(linc_to_host) as f:
			f = f.read()
			res = findall(r'^192.*.', f, MULTILINE)
			if res:
				self.ip_dns = [192, 168, 140, 253]
				text = 'This is MM/MK'
				self.type_oo = 'mm/mk'
				
			else:
				self.ip_dns = [10, 8, 130, 202]
				self.type_oo = 'gm'
				text = 'This is GM'
			logging.info(u'%s', text)

	def find_device(self):
		'''
		Функция поиска ККМ
		'''
		self.find_ports = []
		
		def discovery_callback(port, baudrate):
			# Считываются все порты и скорости, на которых может работать ККМ
			text = u'Checked port:{0}, speed:{1}'.format(port, baudrate)
			self.logger.debug(u'%s', text)
			self.find_ports.append(port)

		self.devices = pyshtrih.discovery(discovery_callback)
		status = False
		for port in self.find_ports:
			if 'ttyACM' in port:
				status = True
				
		if not self.devices or status is False:
			self.logger.error(u'KKM is not found')
			self.logger.info(u'Process is not running')
			exit()
		else:
			self.device = self.devices[0]
			# Подключаемся к ККМ
			self.device.connect()
			self.logger.info(u'Uses KKM: {0} on port: {1}'.format(self.device.name, self.device.port)) 

	def reset_settings(self):
		'''
		Выполнение технического обнуления ККМ,
		при котором присходит сброс настроек до заводских настроек
		'''
		self.logger.info(u'Try started tech. reset')
		try:
			self.device.reset_settings()
			self.logger.debug(u'Tech. reset is successful')
		except pyshtrih.excepts.Error:
			self.logger.error(u'0x16 (Tech. reset is successful) - command is not supported on this mode(0x73)')
			self.logger.info(u'Process is crashed')
			exit()

		# Устанавливаем текущую дату	
		try:
			now = datetime.now()
			self.device.set_datetime(now)
			self.logger.debug(u'Set correct date and time: {0} - OK'.format(now))
		except pyshtrih.excepts.Error:
			self.logger.error(u'0x22 (Date programming) - Not found check tape (0x6B)')
			self.logger.error(u'Failed set correct date and time')
			self.logger.info(u'Process is crashed')
			exit()

		# Инициируем таблицы
		try:
			self.device.init_table()
			self.logger.debug(u'Table initialization  - ОК')
		except:
			self.logger.error(u'Table initialization is fail')
			self.logger.info(u'Process is crashed')
			exit()

		# Выполняем общее гашение
		try:
			self.device.reset_summary()
			self.logger.debug(u'started the total damping - OK')
		except:
			self.logger.error(u'the total damping is fail')
			self.logger.info(u'Process is crashed')
			exit()

		sleep(8)


	def read_needs_param(self):
		'''
		Чтение парраметров, котроые на данный момент находятся в ККМ
		'''
		values = {}

		self.logger.debug(u'Data in table:')
		# Отрезчик чеков
		cut_chek = self.device.read_table(1, 1, 7, type(2))[u'Значение']
		self.logger.debug('Cut_chek: %s', cut_chek)
		
		# ДНС имя
		dns1 = self.device.read_table(16, 1, 15, type(2))
		dns2 = self.device.read_table(16, 1, 16, type(2))
		dns3 = self.device.read_table(16, 1, 17, type(2))
		dns4 = self.device.read_table(16, 1, 18, type(2))
		ip_dns = '.'.join([str(x[u'Значение']) for x in [dns1, dns2, dns3, dns4]])
		self.logger.debug('DNS: %s', ip_dns)
	
		# имя ОФД
		ofd_name = self.device.read_table(18, 1, 10, type('a'))[u'Значение']
		self.logger.debug('OFD_name: %s', ofd_name)
	
		# Адрес ОФД
		ofd_url = self.device.read_table(18, 1, 11, type('a'))[u'Значение']
		self.logger.debug('OFD_adres: %s', ofd_url)
	
		# ИНН
		ofd_inn = self.device.read_table(18, 1, 12, type('a'))[u'Значение']
		self.logger.debug('INN: %s', ofd_inn)
	
		# Сервер ОФД
		server_ofd = self.device.read_table(19, 1, 1, type('a'))[u'Значение']
		self.logger.debug('OFD_server: %s', server_ofd)
	
		# Порт ОФД
		port_ofd = self.device.read_table(19, 1, 2, type(2))[u'Значение']
		self.logger.debug('OFD_port: %s', port_ofd)
	
		# РНДИС
		rndis = self.device.read_table(21, 1, 9, type(2))[u'Значение']
		
		self.logger.debug('RNDIS: %s', rndis)
		
	def write_correct_value_in_tables(self):
		'''
		Запись корректных парраметров таблиц в ККМ
		'''
		self.logger.info(u'Write data in table')

		# Устанавливаем текущую дату/время
		now = datetime.now()
		self.device.set_datetime(now)
		
		try:
			# Отрезчик чеков
			self.device.write_table(1, 1, 7, 2, int)
			self.logger.debug('cut_check - OK')
		except:
			self.logger.debug('cut_check - not writed')
		
		sleep(3)
		
		# ДНС имя
		try:
			self.device.write_table(16, 1, 15, self.ip_dns[0], int)
			self.device.write_table(16, 1, 16, self.ip_dns[1], int)
			self.device.write_table(16, 1, 17, self.ip_dns[2], int)
			self.device.write_table(16, 1, 18, self.ip_dns[3], int)
			self.logger.debug('dns - OK')
		except:
			self.logger.debug('dns - not writed')
			
		if self.type_oo == 'gm':
			self.device.write_table(16, 1, 13, 254, int)
			self.logger.debug('mask - OK')
		
		sleep(3)
		
		try:
			# имя ОФД
			name = u'АО "Тандер"'
			self.device.write_table(18, 1, 10, name, str)
			self.logger.debug('ofd_name - OK')
		except:
			self.logger.debug('ofd_name - not writed')
		
		sleep(3)
	
		try:
			# Адрес ОФД
			adres = u'lk.ofd-magnit.ru'
			self.device.write_table(18, 1, 11, adres, str)
			self.logger.debug('ofd_adres - OK')
		except:
			self.logger.debug('ofd_adres - not writed')
		
		sleep(3)
	
		try:
			# ИНН
			inn = u'2310031475'
			self.device.write_table(18, 1, 12, inn, str)
			self.logger.debug('inn - OK')
		except:
			self.logger.debug('inn - not writed')
		
		sleep(3)
	
		try:
			# Сервер ОФД
			server = u'kkt.ofd-magnit.ru'
			self.device.write_table(19, 1, 1, server, str)
			self.logger.debug('ofd_server - OK')
		except:
			self.logger.debug('ofd_server - not writed')
		
		sleep(3)
		
		try:
			# Порт ОФД
			self.device.write_table(19, 1, 2, 7001, int)
			self.logger.debug('ofd_port - OK')
		except:
			self.logger.debug('ofd_port - not writed')
		
		sleep(3)
	
		try:
			# РНДИС
			self.device.write_table(21, 1, 9, 1, int)
			self.logger.debug('rndis - OK')
		except:
			self.logger.debug('rndis - not writed')
		
			
	

if __name__ == '__main__':
	fix_mem()
