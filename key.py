from requests import Session
import time
import hashlib		
import wmi 			#pip install wmi pywin32
import platform
import psutil		#pip install psutil
import shutil

def create_key(tool_name):
	try:
		c = wmi.WMI()
		dic = {}
		for item in c.Win32_PhysicalMedia():
			dic[str(item.wmi_property('Tag').value).replace('\\','')] = str(item.wmi_property('SerialNumber').value).replace(' ','')
		diskserial = dic['.PHYSICALDRIVE0']
	except:
		diskserial = ''

	try:
		computername = str(platform.node())
	except:
		computername = ''

	try:
		hdtotal, hdused, hdfree = shutil.disk_usage("/")
	except:
		hdtotal = ''

	try:
		ramsize = str(psutil.virtual_memory().total)
	except:
		ramsize = ''

	try:
		ncpu = str(psutil.cpu_count(logical=True))
	except:
		ncpu = ''
	key_reg = diskserial + ' ' + computername + ' ' + str(hdtotal) + ' ' + ramsize + ' ' + ncpu + ' ' + tool_name
	# print(key_reg)
	key_reg = hashlib.md5(key_reg.encode('utf-8')).hexdigest()
	# print(key_reg)
	return key_reg

# print(create_key('kuishoupro'))

def encode_key(key_reg):
	key_value = '0123456789'
	key_result = ''
	for i in range(len(key_reg)):
		key_result += key_value[ord(key_reg[i]) % len(key_value)]
	return key_result

def date_to_int(ddate):
	idate = ddate.replace('-', '').replace('/', '')
	return int(idate)

def check_key(key_reg):
	ses = Session()
	# res = ses.post('http://127.0.0.1:8000/key/', data={'key_reg': key_reg}, timeout=10)
	res = ses.post('https://adkeytool.herokuapp.com/key/', data={'key_reg': key_reg}, timeout=60)
	data = res.json()
	# print(data)
	text = 'Actived'
	if data['result'] == '0':
		text = 'Key not found'
		return False, text
	idate_now = int(time.strftime("%Y%m%d"))
	idate_key = date_to_int(data['expiry_date'])
	if idate_now > idate_key:
		text = 'Key has expired'
		return False, text
	key_result = data['key_result']
	if key_result != key_reg:
		text = 'Key is error'
		return False, text
	return True, data['expiry_date']
