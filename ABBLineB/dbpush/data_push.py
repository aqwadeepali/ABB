import os, sys, csv, time
import elib
import datetime
import time
import ast
import json
from datetime import timedelta
from data_models import ReaderBase

from pymongo import MongoClient

from ConfigParser import SafeConfigParser


class Run():
	def __init__(self, args=[]):

		if len(args) == 0:
			args = sys.argv[1:]
			keys = "Flour,G Sugar,Salt,SBC,Vitamin,Calcium,ABC,Lecithin,GMS,SMP,Milk,Syrup,Vannila,Flavour,FFM,Water,Biscuit Dust,Sugar,Cream,Palm Oil"
		else:
			args_result = {}
			for k in args:
				s = k.split('=')
				args_result[s[0]] = elib.smartFmt(s[1])

			keys = args_result["keys"]
		self.collection = ""
		self.read_settings()

		self.properties = keys.split(",")
		self._date = "";
		self.all_dates = [];

		self.cfg = SafeConfigParser()
		self.cfg.optionxform = str
		self.cfg.read('loader.cfg')
		# source_target = self.cfg.items('source_target')

		print 'Reading Params....'
		# target_dict = self.read_parameters()
		# target_dict = self.read_from_db(dateparam="01/11/18")

		# self.push_records(target_dict)
		print self._date
		# self.write_files(target_dict)
		print 'File Ready to Use...'

	def read_settings(self):
		print "Reading Settings"
		all_json = ""
		all_keys = ""
		collection = ""
		reader = csv.DictReader(open('data/settings.txt'), delimiter="\t")
		for row in reader:
			if row["Field"] == "JSON":
				all_json = ast.literal_eval(row["Value"])
			if row["Field"] == "KEYS":
				all_keys = ast.literal_eval(row["Value"])
			if row["Field"] == "COLLECTION":
				collection = row["Value"]

		self.readerconfig = ReaderBase()
		self.kpis = self.readerconfig.kpis(all_keys)
		self.config = self.readerconfig.toKeyJSON(all_json)
		self.collection = collection

	def push_records(self, target_dict):
		print "Data Push Started..."

		client = MongoClient('mongodb://localhost:27017/')

		mydb = client['abb']
		dbData = []
		# minDate = min(sorted(self.all_dates))
		# maxDate = max(sorted(self.all_dates))
		for prop in target_dict:
			for key in target_dict[prop]:
				 row = {}
				 row = target_dict[prop][key]
				 row.setdefault("Prop", prop)
				 dbData.append(row)
		_to_push = {
			"asofdate": self._date,
			"identifier": "Mixing",
			"staging": dbData
		}

		record_id = mydb["staging"].update(_to_push, { "$set" : _to_push}, upsert=True)

		print mydb.collection_names()

		print "DB Push Completed..."


	def write_files(self, target_dict):
		for prop in self.properties:
			header = ["BatchCount", "TotalSetPoint", "TotalActualQty", "Deviation", "AvgDeviation", "AvgDuration", "TargetAchieved", "TargetMissed"]
			out_list = []
			for key in sorted(target_dict[prop].keys()):
				out_list.append(target_dict[prop][key])
			# print out_list
			outf = csv.DictWriter(open('data/outf_'+prop+'.txt', "wb"), header, delimiter="\t")
			outf.writeheader()
			for each_row in out_list:
				outf.writerow(each_row)

	def read_from_db(self, dateparam = ""):
		_dict = {}
		target_dict = {}
		connection = MongoClient('mongodb://localhost:27017/')

		myDb = connection["abb"]
		db = myDb[self.collection]
		dbresult = []
		if dateparam == "":
			dbresult = db.find()
		else:
			to_find = ".*"+dateparam+".*"
			db[self.collection].find({"TIME" : {"$regex" : to_find}})

		for prop in self.properties:
			_dict.setdefault(prop, {})
			target_dict.setdefault(prop, {})

		for row in dbresult:
			for prop in self.properties:  
				keyprop = prop.lower().replace(' ', '_')
				x = elib.trim(row[self.config["time"]])
				d = datetime.datetime.strptime(x, '%d/%m/%Y %H:%M:%S')
				fbtime = d.strftime('%Y-%m-%d %H:%M:%S')

				fbcount = elib.trim(row[self.config[keyprop+'_batch_count']])
				fbset = elib.tonum(row[self.config[keyprop+'_batch_set_weight']])
				fbactualweight = elib.tonum(row[self.config[keyprop+'_actual_weight']])
				
				self._date = elib.date2str(elib.str2date(fbtime, "%Y-%m-%d %H:%M:%S"))

				if fbcount not in _dict[prop].keys():
					_dict[prop].setdefault(fbcount, {}).setdefault("Set", [])
					_dict[prop].setdefault(fbcount, {}).setdefault("ActualWeight", [])
					_dict[prop].setdefault(fbcount, {}).setdefault("Time", [])
				_dict[prop][fbcount]["Set"].append(fbset)
				_dict[prop][fbcount]["ActualWeight"].append(fbactualweight)
				_dict[prop][fbcount]["Time"].append(fbtime)

		for prop in self.properties:
			total_batches = len(_dict[prop].keys())
			if prop not in target_dict.keys():
				target_dict.setdefault(prop, {}).setdefault(key, {})
			for key in sorted(_dict[prop].keys()):
				try:
					datetimeFormat = '%Y-%m-%d %H:%M:%S'
					date1 = max(_dict[prop][key]["Time"])
					date2 = min(_dict[prop][key]["Time"])
					dts = datetime.datetime.strptime(date1, datetimeFormat)
					dts_time = time.mktime(dts.timetuple()) * 1000
					self.all_dates.append(dts_time)
					diff = datetime.datetime.strptime(date1, datetimeFormat) - datetime.datetime.strptime(date2, datetimeFormat)
					avg_duration = str(diff)
					
					deviation = 0
					total_set = max(_dict[prop][key]["Set"])
					total_actual = max(_dict[prop][key]["ActualWeight"])
					deviation = total_set - total_actual
					
					avg_deviation = deviation / total_batches
					if total_set == 0:
						target_achieved = 0
					else:
						target_achieved = total_actual / total_set
					target_missed = 1 - target_achieved
					if key not in target_dict[prop].keys():
						target_dict[prop].setdefault(str(key), {})
					target_dict[prop][str(key)].setdefault("AvgDuration", avg_duration)
					target_dict[prop][str(key)].setdefault("TotalSetPoint", total_set)
					target_dict[prop][str(key)].setdefault("TotalActualQty", total_actual)
					target_dict[prop][str(key)].setdefault("BatchCount", key)
					target_dict[prop][str(key)].setdefault("Deviation", deviation)
					target_dict[prop][str(key)].setdefault("AvgDeviation", elib.rnd(avg_deviation, 2))
					target_dict[prop][str(key)].setdefault("TargetAchieved", target_achieved)
					target_dict[prop][str(key)].setdefault("TargetMissed", target_missed)
					# print prop, '---', str(key), '---', target_dict[prop][str(key)]
				except Exception as e:
					print e
		
		return target_dict

	def read_parameters(self):
		_dict = {}
		target_dict = {}

		for prop in self.properties:
			_dict.setdefault(prop, {})
			target_dict.setdefault(prop, {})

		
		source_target = self.cfg.items('source_target')
		for source, target in source_target:
			reader = csv.DictReader(open('data/' + source), delimiter="\t")
			for row in reader:
				for prop in self.properties:  
					keyprop = prop.lower().replace(' ', '_')
					x = elib.trim(row[self.config["time"]])

					fbcount = elib.trim(row[self.config[keyprop+'_batch_count']])
					fbset = elib.tonum(row[self.config[keyprop+'_batch_set_weight']])
					fbactualweight = elib.tonum(row[self.config[keyprop+'_actual_weight']])
					d = datetime.datetime.strptime(x, '%d/%m/%Y %H:%M:%S')
					fbtime = d.strftime('%Y-%m-%d %H:%M:%S')
					self._date = elib.date2str(elib.str2date(fbtime, "%Y-%m-%d %H:%M:%S"))

					if fbcount not in _dict[prop].keys():
						_dict[prop].setdefault(fbcount, {}).setdefault("Set", [])
						_dict[prop].setdefault(fbcount, {}).setdefault("ActualWeight", [])
						_dict[prop].setdefault(fbcount, {}).setdefault("Time", [])
					_dict[prop][fbcount]["Set"].append(fbset)
					_dict[prop][fbcount]["ActualWeight"].append(fbactualweight)
					_dict[prop][fbcount]["Time"].append(fbtime)

		for prop in self.properties:
			total_batches = len(_dict[prop].keys())
			print total_batches
			if prop not in target_dict.keys():
				target_dict.setdefault(prop, {}).setdefault(key, {})
			for key in sorted(_dict[prop].keys()):
				try:
					datetimeFormat = '%Y-%m-%d %H:%M:%S'
					date1 = max(_dict[prop][key]["Time"])
					date2 = min(_dict[prop][key]["Time"])
					# dts = datetime.datetime.strptime(date1, datetimeFormat)
					# dts_time = time.mktime(dts.timetuple()) * 1000
					# self.all_dates.append(dts_time)
					diff = datetime.datetime.strptime(date1, datetimeFormat) - datetime.datetime.strptime(date2, datetimeFormat)
					avg_duration = str(diff)
					
					deviation = 0
					total_set = max(_dict[prop][key]["Set"])
					total_actual = max(_dict[prop][key]["ActualWeight"])
					deviation = total_set - total_actual
					
					avg_deviation = deviation / total_batches
					if total_set == 0:
						target_achieved = 0
					else:
						target_achieved = total_actual / total_set
					target_missed = 1 - target_achieved
					if key not in target_dict[prop].keys():
						target_dict[prop].setdefault(str(key), {})
					target_dict[prop][str(key)].setdefault("AvgDuration", avg_duration)
					target_dict[prop][str(key)].setdefault("TotalSetPoint", total_set)
					target_dict[prop][str(key)].setdefault("TotalActualQty", total_actual)
					target_dict[prop][str(key)].setdefault("BatchCount", key)
					target_dict[prop][str(key)].setdefault("Deviation", deviation)
					target_dict[prop][str(key)].setdefault("AvgDeviation", elib.rnd(avg_deviation, 2))
					target_dict[prop][str(key)].setdefault("TargetAchieved", target_achieved)
					target_dict[prop][str(key)].setdefault("TargetMissed", target_missed)
					# print prop, '---', str(key), '---', target_dict[prop][str(key)]
				except Exception as e:
					print e
		# print target_dict
		return target_dict

# class Run:
#     def __init__(self, args=[]):
		
#         Params()

if __name__ == "__main__":
	# keys="Flour,G Sugar,Salt,SBC,Vitamin,Calcium,ABC,Lecithin,GMS,SMP,Milk,Syrup,Vannila,Flavour,FFM,Water,Biscuit Dust,Sugar,Cream,Palm Oil"

	Run()