import os, sys, csv, time
import elib
import datetime
import time
import ast
from datetime import timedelta
from data_models import ReaderBase

from pymongo import MongoClient

from ConfigParser import SafeConfigParser

class Run():
    def __init__(self, args=[]):
        self.readerconfig = ReaderBase()
        self.config = self.readerconfig.getKeyJSON()
        self.collection = {}

        self.cfg = SafeConfigParser()
        self.cfg.optionxform = str
        self.cfg.read('loader.cfg')

        print 'Reading Params....'
        # self.read_data_push()
        
        # self.moulder_config = {}
        # all_json = self.read_settings("moulder_settings.txt")
        # self.moulder_config = self.readerconfig.toKeyJSON(all_json)
        # self.read_moulder_push()

        # self.cms_config = {}
        # all_json = self.read_settings("cms_settings.txt")
        # self.cms_config = self.readerconfig.toKeyJSON(all_json)
        # self.read_cms_push()

        # self.wt_config = {}
        # all_json = self.read_wt_settings("wet_weight_settings.txt")
        # self.wt_config = self.readerconfig.toKeyJSON(all_json)
        # self.read_wt_push()

        # self.packing_config = {}
        # all_json = self.read_settings("packing_settings.txt")
        # self.packing_config = self.readerconfig.toKeyJSON(all_json)
        # self.read_packing_push()

        self.setting_config = {}
        all_json = self.read_settings("ui_settings_config.txt")
        self.setting_config = self.readerconfig.toKeyJSON(all_json)
        self.read_setting_push()

    def read_data_push(self):
        target_data = []        
        source_target = self.cfg.items('source_target')
        for source, target in source_target:
            reader = csv.DictReader(open('data/' + source), delimiter="\t")
            for row in reader:
                x = elib.trim(row[self.config["time"]])
                d = datetime.datetime.strptime(x, '%d/%m/%Y %H:%M:%S')
                fbtime = d.strftime('%Y-%m-%d')
                row["asofdate"] = fbtime 
                fb_timestamp = time.mktime(d.timetuple())
                row["TIMESTAMP"] = fb_timestamp

                target_data.append(row)

        connection = MongoClient('127.0.0.1', username="admin", password="admin123", authSource='analyse_db', authMechanism='SCRAM-SHA-1')
        myDb = connection["analyse_db"]

        record_id = mydb[self.collection].insert(target_data)

        print mydb.collection_names()
        print "Data Push Completed..."

    def read_settings(self, txtfilename):
        print "Reading Settings"
        all_json = ""
        collection = ""
        reader = csv.DictReader(open('data/' + txtfilename), delimiter="\t")
        for row in reader:
            if row["Field"] == "JSON":
                all_json = ast.literal_eval(row["Value"])
            if row["Field"] == "COLLECTION":
                collection = row["Value"]
        self.collection = collection
        return all_json

    def read_setting_push(self):
        print self.setting_config
        target_data = []        
        source = "ui_settings.txt"
        reader = csv.DictReader(open('data/' + source), delimiter="\t")
        for row in reader:
            target_row = {}

            for tr in self.setting_config:
                target_row.setdefault(self.setting_config[tr], row[self.setting_config[tr]])
                
            target_data.append(target_row)

        connection = MongoClient('127.0.0.1', username="admin", password="admin123", authSource='analyse_db', authMechanism='SCRAM-SHA-1')
        mydb = connection["analyse_db"]

        record_id = mydb[self.collection].insert(target_data)

        print mydb.collection_names()
        print "Data Push Completed..."

    def read_packing_push(self):
        print self.packing_config
        target_data = []        
        source = "Moulder.txt"
        reader = csv.DictReader(open('data/' + source), delimiter="\t")
        for row in reader:
            target_row = {}

            for tr in self.packing_config:
                #print tr, '----'#, self.packing_config[tr]
                target_row.setdefault(self.packing_config[tr], row[self.packing_config[tr]])
            x = elib.trim(row[self.packing_config["time"]])
            d = datetime.datetime.strptime(x, '%d/%m/%Y %H:%M:%S')
            fbtime = datetime.datetime.strptime(d.strftime('%Y-%m-%d %H:%M:%S'), '%Y-%m-%d %H:%M:%S')
            fbdate = d.strftime('%Y-%m-%d')
            target_row["asofdate"] = fbdate
            # fbtime = d.strftime("%H:%M")
            # target_row["asoftime"] = fbtime

            fb_timestamp = time.mktime(d.timetuple())
            target_row["TIMESTAMP"] = fb_timestamp
            target_row["TIME"] = fbtime
            target_data.append(target_row)

        connection = MongoClient('127.0.0.1', username="admin", password="admin123", authSource='analyse_db', authMechanism='SCRAM-SHA-1')
        mydb = connection["analyse_db"]

        record_id = mydb[self.collection].insert(target_data)

        print mydb.collection_names()
        print "Data Push Completed..."

    def read_moulder_push(self):
        print self.moulder_config
        target_data = []        
        source = "Moulder.txt"
        reader = csv.DictReader(open('data/' + source), delimiter="\t")
        for row in reader:
            target_row = {}

            for tr in self.moulder_config:
                target_row.setdefault(self.moulder_config[tr], row[self.moulder_config[tr]])
            x = elib.trim(row[self.moulder_config["time"]])
            d = datetime.datetime.strptime(x, '%d/%m/%Y %H:%M:%S')
            fbdate = d.strftime('%Y-%m-%d')
            target_row["asofdate"] = fbdate
            # fbtime = d.strftime("%H:%M")
            # target_row["asoftime"] = fbtime

            fb_timestamp = time.mktime(d.timetuple())
            target_row["TIMESTAMP"] = fb_timestamp

            target_data.append(target_row)

        client = MongoClient('mongodb://localhost:27017/')

        mydb = client['abb']

        record_id = mydb[self.collection].insert(target_data)

        print mydb.collection_names()
        print "Data Push Completed..."

    def read_cms_push(self):
        print self.cms_config
        target_data = []        
        source = "Moulder.txt"
        reader = csv.DictReader(open('data/' + source), delimiter="\t")
        for row in reader:
            target_row = {}

            for tr in self.cms_config:
                target_row.setdefault(self.cms_config[tr], row[self.cms_config[tr]])
            x = elib.trim(row[self.cms_config["time"]])
            d = datetime.datetime.strptime(x, '%d/%m/%Y %H:%M:%S')
            fbdate = d.strftime('%Y-%m-%d')
            target_row["asofdate"] = fbdate
            # fbtime = d.strftime("%H:%M")
            # target_row["asoftime"] = fbtime

            fb_timestamp = time.mktime(d.timetuple())
            target_row["TIMESTAMP"] = fb_timestamp

            target_data.append(target_row)

        client = MongoClient('mongodb://localhost:27017/')

        mydb = client['abb']

        record_id = mydb.cms_report.insert(target_data)

        print mydb.collection_names()
        print "Data Push Completed..."

    def read_wt_push(self):
        print self.wt_config
        target_data = []        
        source = "Moulder.txt"
        reader = csv.DictReader(open('data/' + source), delimiter="\t")
        for row in reader:
            target_row = {}

            for tr in self.wt_config:
                target_row.setdefault(self.wt_config[tr], row[self.wt_config[tr]])
            x = elib.trim(row[self.wt_config["time"]])
            d = datetime.datetime.strptime(x, '%d/%m/%Y %H:%M:%S')
            fbdate = d.strftime('%Y-%m-%d')
            target_row["asofdate"] = fbdate
            # fbtime = d.strftime("%H:%M")
            # target_row["asoftime"] = fbtime

            fb_timestamp = time.mktime(d.timetuple())
            target_row["TIMESTAMP"] = fb_timestamp

            target_data.append(target_row)

        client = MongoClient('mongodb://localhost:27017/')

        mydb = client['abb']

        record_id = mydb.wt_weight_report.insert(target_data)

        print mydb.collection_names()
        print "Data Push Completed..."


if __name__ == "__main__":
    Run()