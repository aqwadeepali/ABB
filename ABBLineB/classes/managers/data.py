import os
from xml.etree import ElementTree
from pymongo import MongoClient
# import _winreg

# ITANTA_STORE = r'SOFTWARE\Itanta\web'


CONFIG_PATH = str(os.path.realpath(__file__))
CONFIG_PATH = CONFIG_PATH.replace("data.pyc", "")
CONFIG_PATH = CONFIG_PATH.replace("data.pyo", "")
CONFIG_PATH = CONFIG_PATH.replace("data.py", "")
CONFIG_PATH = CONFIG_PATH.replace("classes\managers","")
CONFIG_PATH = CONFIG_PATH + "../../dbpush/"

# CONFIG_PATH = str(os.path.realpath(__file__))
# CONFIG_PATH = CONFIG_PATH.replace("tracker_data.pyc", "")
# CONFIG_PATH = CONFIG_PATH.replace("tracker_data.pyo", "")
# CONFIG_PATH = CONFIG_PATH.replace("tracker_data.py", "")
# CONFIG_PATH = CONFIG_PATH.replace("classes\managers","")
# CONFIG_PATH = CONFIG_PATH + "../../config/"

# def get_db_credentials():
#     credentials = {}
#     reg = _winreg.ConnectRegistry(None, _winreg.HKEY_LOCAL_MACHINE)
#     key = _winreg.OpenKey(reg, ITANTA_STORE)
#     index = 0
#     subkeyCnt, valuesCnt, modtime = _winreg.QueryInfoKey(key)
#     for n in xrange(valuesCnt):
#         v = _winreg.EnumValue(key, n)
#         if v[0] == 'user' or v[0] == 'password':
#             credentials[v[0]] = v[1]
#     _winreg.CloseKey(key)
#     return credentials


class DataManager():
    def __init__(self):
        # credentials = get_db_credentials()
        # print credentials
        # self.client = MongoClient('127.0.0.1', username=credentials['user'], password=credentials['password'], authSource='analyse_db', authMechanism='SCRAM-SHA-1')
        self.client = MongoClient('127.0.0.1', username="admin", password="admin123", authSource='analyse_db', authMechanism='SCRAM-SHA-1')
        print "Connections ready to use..."
    def get_connection(self):
        return self.client
	
	
	
