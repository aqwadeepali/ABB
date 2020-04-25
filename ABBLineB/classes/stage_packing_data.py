import os, sys, csv, time
import elib
import datetime
import time
import ast
import json
from datetime import timedelta, datetime
from stage_model import ReaderBase
from time import strftime
from pymongo import MongoClient
import pandas as pd
import pdfkit
import uuid
import zipfile
import re
import operator
import imgkit

from highcharts import Highchart

import logging
import logging.config
from logging import getLogger, INFO, ERROR, WARNING, CRITICAL, NOTSET, DEBUG, Formatter
from concurrent_log_handler import ConcurrentRotatingFileHandler

# path_wkthmltopdf = r'C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe'
# config = pdfkit.configuration(wkhtmltopdf=path_wkthmltopdf)

# path_wkthmltoimage = r'C:\Program Files\wkhtmltopdf\bin\wkhtmltoimage.exe'
# image_config = imgkit.config(wkhtmltoimage=path_wkthmltoimage)

CONFIG_PATH = str(os.path.realpath(__file__))
CONFIG_PATH = CONFIG_PATH.replace("stage_packing_data.pyc", "")
CONFIG_PATH = CONFIG_PATH.replace("stage_packing_data.pyo", "")
CONFIG_PATH = CONFIG_PATH.replace("stage_packing_data.py", "")
CONFIG_PATH = CONFIG_PATH + "data/"

FILE_PATH = str(os.path.realpath(__file__))
FILE_PATH = FILE_PATH.replace("stage_packing_data.pyc", "")
FILE_PATH = FILE_PATH.replace("stage_packing_data.pyo", "")
FILE_PATH = FILE_PATH.replace("stage_packing_data.py", "")
FILE_PATH = FILE_PATH.replace("classes", "")
FILE_PATH = FILE_PATH + "dbpush/data/"

HTML_TEMPLATE1 = '<html><head><style>'\
  'h1 {text-align: center;font-family: Helvetica, Arial, sans-serif; page-break-before: always;}'\
  'h2 {text-align: center;font-family: Helvetica, Arial, sans-serif;}'\
  'h3 {text-align: center;font-family: Helvetica, Arial, sans-serif;}'\
  'table { margin-left: auto;margin-right: auto;}'\
  'table, th, td {border: 1px solid black;border-collapse: collapse;}'\
  'th {padding: 3px;text-align: center;font-family: Helvetica, Arial, sans-serif;font-size: 85%;background-color:#ACD7E3}'\
  'td {padding: 3px;text-align: center;font-family: Helvetica, Arial, sans-serif;font-size: 80%;background-color:#ddeff3}'\
  'table tbody tr:hover {background-color: #dddddd;}' \
  '.wide {width: 100%;} .wide tr:nth-child(even) { background: #e9e9e9;}' \
  '</style></head><body>'
  
HTML_TEMPLATE3 = '<html><head><link rel="stylesheet" type="text/css" href="'+CONFIG_PATH+'all_css.css"/><style>'\
  'h1 {font-family: Helvetica, Arial, sans-serif;page-break-before: always;}'\
  'h2 {font-family: Helvetica, Arial, sans-serif;}'\
  'h3 {font-family: Helvetica, Arial, sans-serif;}'\
  'table { margin-left: auto;margin-right: auto;}'\
  'table, th, td {border: 1px solid black;border-collapse: collapse;}'\
  'th {padding: 3px;text-align: center;font-family: Helvetica, Arial, sans-serif;font-size: 85%;background-color:#ACD7E3}'\
  'td {padding: 3px;text-align: center;font-family: Helvetica, Arial, sans-serif;font-size: 80%;background-color:#ddeff3}'\
  'table tbody tr:hover {background-color: #dddddd;}' \
  '.wide {width: 100%;} .wide tr:nth-child(even) { background: #e9e9e9;}' \
  '</style></head><body>'

HTML_TEMPLATE2 = '</body></html>'

class PRun():
    def __init__(self):
        
        self.collection = ""
        self.properties = ""
        self.reportKeys = []
        self.reportManager = {}
        self.log = getLogger()
        self.read_settings()

        self._date = "";
        self.all_dates = [];

        self.log.info('Reading Params....')
        self.log.info(self._date)
        self.log.info('File Ready to Use...')
        # self.get_today_records()


    def read_settings(self):
        self.log.info("Reading Settings")
        all_json = ""
        all_keys = ""
        keys = ""
        collection = ""
        reportKeys = ""
        reportManager = ""
        keys = ""
        reader = csv.DictReader(open(CONFIG_PATH + 'stage_packing_settings.txt'), delimiter="\t")
        for row in reader:
            if row["Field"] == "JSON":
                all_json = ast.literal_eval(row["Value"])
            if row["Field"] == "KEYS":
                all_keys = ast.literal_eval(row["Value"])
            if row["Field"] == "COLLECTION":
                collection = row["Value"]
            if row["Field"] == "REPORTKEYS":
                reportKeys = ast.literal_eval(row["Value"])
            if row["Field"] == "REPORTMNG":
                reportManager = ast.literal_eval(row["Value"])
            if row["Field"] == "SEQ":
                keys = row["Value"]
 
        self.readerconfig = ReaderBase()
        # self.properties = self.readerconfig.kpis(all_keys)
        self.config = self.readerconfig.toKeyJSON(all_json)
        self.collection = collection
        self.keys = keys
        self.properties = keys.split(",")
        self.reportManager = reportManager
        self.reportKeys = reportKeys

    def read_from_db_CBB(self, dateparam=""):
        self.log.info("dateparam: %s", dateparam)
        
        _dict = {}
        target_dict = {}
        
        connection = MongoClient('127.0.0.1', username="admin", password="admin123", authSource='analyse_db', authMechanism='SCRAM-SHA-1')
        myDb = connection["analyse_db"]
        #connection = MongoClient('mongodb://localhost:27017/')

        #myDb = connection["abb"]
        #myDb = connection["analyse_db"]
        db = myDb[self.collection]

        dbresult = []
        if dateparam == "":
            dbresult = db.find()
        else:
            yesterdayDate = datetime.strptime(dateparam, '%Y-%m-%d')
            _date2460 = yesterdayDate + timedelta(minutes = (24*60))
            todayDate = _date2460.strftime('%Y-%m-%d')
            selectedDate = yesterdayDate.strftime("%Y-%m-%d")

            to_find = dateparam #"$lt" : new ISODate("2019-01-27T23:59:00.000Z")
            ls_date = todayDate+" 06:59:00"
            gt_date = selectedDate+" 07:00:00"
            lt_tm = time.mktime(datetime.strptime(ls_date,'%Y-%m-%d %H:%M:%S').timetuple())
            gt_tm = time.mktime(datetime.strptime(gt_date,'%Y-%m-%d %H:%M:%S').timetuple())
            to_find = {"$gte": gt_tm, "$lte": lt_tm }
            #print to_find
            dbresult = db.find({self.config["time_stamp"]:to_find}) 
            
        _dict.setdefault("cms", {})
        target_dict.setdefault("cms", {})

        rpmCount = 0
        cbb_weight = 0
        cbb_average_weight = 0
        cbb_stoppage_duration = 0
        cbb_no_of_stopagges = 0
        cbb_accepted_packs = 0
        cbb_usl = 0
        cbb_lsl = 0
        for row in dbresult:
            # for prop in self.properties:
            prop = "cbb"
            _dict.setdefault(prop, {})
            #x = row[self.config["time"]]
            small_prop = prop.lower()
            #d = datetime.strptime(x, '%d/%m/%Y %H:%M:%S')
            #print row[self.config["time"]]
            fbtime = row[self.config["time"]]
            
            self._date = fbtime.strftime("%Y-%m-%d")
            _dict[prop].setdefault(fbtime, {})

            cbb_weight = row[self.config['cbb_weight']] if row.get(self.config["cbb_weight"], "--") != "--" else cbb_weight
            cbb_average_weight = row[self.config['cbb_average_weight']] if row.get(self.config["cbb_average_weight"], "--") != "--" else cbb_average_weight
            cbb_stoppage_duration = row[self.config['cbb_stoppage_duration']] if row.get(self.config["cbb_stoppage_duration"], "--") != "--" else cbb_stoppage_duration
            cbb_no_of_stopagges = row[self.config['cbb_no_of_stopagges']] if row.get(self.config["cbb_no_of_stopagges"], "--") != "--" else cbb_no_of_stopagges
            cbb_accepted_packs = row[self.config['cbb_accepted_packs']] if row.get(self.config["cbb_accepted_packs"], "--") != "--" else cbb_accepted_packs
            cbb_usl = row[self.config['cbb_usl']] if row.get(self.config["cbb_usl"], "--") != "--" else cbb_usl
            cbb_lsl = row[self.config['cbb_lsl']] if row.get(self.config["cbb_lsl"], "--") != "--" else cbb_lsl

            _dict[prop][fbtime]["Weight"] = elib.tonum(cbb_weight)
            _dict[prop][fbtime]["AverageWeight"] = elib.tonum(cbb_average_weight)
            _dict[prop][fbtime]["StoppageDuration"] = elib.tonum(cbb_stoppage_duration)
            _dict[prop][fbtime]["NoOfStopagges"] = elib.tonum(cbb_no_of_stopagges)
            _dict[prop][fbtime]["AcceptedPacks"] = elib.tonum(cbb_accepted_packs)
            _dict[prop][fbtime]["TotalUSL"] = elib.tonum(cbb_usl)
            _dict[prop][fbtime]["TotalLSL"] = elib.tonum(cbb_lsl)
            _dict[prop][fbtime]["Time"] = fbtime                
            _dict[prop][fbtime]["Prop"] = prop
                
        return _dict

    def read_from_db(self, dateparam = ""):
        self.log.info("dateparam: %s", dateparam)
        
        _dict = {}
        target_dict = {}
        
        connection = MongoClient('127.0.0.1', username="admin", password="admin123", authSource='analyse_db', authMechanism='SCRAM-SHA-1')
        myDb = connection["analyse_db"]
        db = myDb[self.collection]

        dbresult = []
        if dateparam == "":
            dbresult = db.find()
        else:
            yesterdayDate = datetime.strptime(dateparam, '%Y-%m-%d')
            _date2460 = yesterdayDate + timedelta(minutes = (24*60))
            todayDate = _date2460.strftime('%Y-%m-%d')
            selectedDate = yesterdayDate.strftime("%Y-%m-%d")

            to_find = dateparam #"$lt" : new ISODate("2019-01-27T23:59:00.000Z")
            ls_date = todayDate+" 06:29:00"
            gt_date = selectedDate+" 06:30:00"
            lt_tm = time.mktime(datetime.strptime(ls_date,'%Y-%m-%d %H:%M:%S').timetuple())
            gt_tm = time.mktime(datetime.strptime(gt_date,'%Y-%m-%d %H:%M:%S').timetuple())
            to_find = {"$gte": gt_tm, "$lte": lt_tm }
            dbresult = db.find({self.config["time_stamp"]:to_find}) 
            
        for prop in self.properties:
            _dict.setdefault(prop, {})
            target_dict.setdefault(prop, {})
        
        rpmCount = 0
        pm_tot_weight_accepted_packs = 0
        pm_no_of_packs_in_accepted_band = 0
        packing_pm_average_rate = 0
        pm_tot_accepted_packs = 0
        pm_tot_rejected_packs = 0
        pm_tot_joint_packs = 0
        pm_tot_lsl = 0
        pm_tot_usl = 0
        pm_no_of_stopagges = 0
        pm_stoppage_duration = 0
        pm_sku = 0
        for row in dbresult:
            for prop in self.properties:
                fbtime = row[self.config["time"]]
                small_prop = prop.lower()
                #d = datetime.strptime(x, '%d/%m/%Y %H:%M:%S')
                #fbtime = d.strftime('%Y-%m-%d %H:%M:%S')
                
                self._date = fbtime.strftime("%Y-%m-%d")
                _dict[prop].setdefault(fbtime, {})
                
                pm_tot_weight_accepted_packs = row[self.config[small_prop + '_tot_weight_accepted_packs']] if row.get(self.config[small_prop + '_tot_weight_accepted_packs'], "--") != "--" else pm_tot_weight_accepted_packs
                pm_no_of_packs_in_accepted_band = row[self.config[small_prop + '_no_of_packs_in_accepted_band']] if row.get(self.config[small_prop + '_no_of_packs_in_accepted_band'], "--") != "--" else pm_no_of_packs_in_accepted_band
                packing_pm_average_rate = elib.tonum(row[self.config['packing_'+small_prop+'_average_rate']]) if row.get(self.config['packing_'+small_prop+'_average_rate'], "--") != "--" else packing_pm_average_rate
                pm_tot_accepted_packs = elib.tonum(row[self.config[small_prop + '_tot_accepted_packs']]) if row.get(self.config[small_prop + '_tot_accepted_packs'],"--") != "--" else pm_tot_accepted_packs
                pm_tot_rejected_packs = elib.tonum(row[self.config[small_prop + "_tot_rejected_packs"]]) if row.get(self.config[small_prop + "_tot_rejected_packs"], "--") != "--" else pm_tot_rejected_packs
                pm_tot_joint_packs = elib.tonum(row[self.config[small_prop + "_tot_joint_packs"]]) if row.get(self.config[small_prop + "_tot_joint_packs"],"--") != "--" else pm_tot_joint_packs
                pm_tot_lsl = elib.tonum(row[self.config[small_prop + "_tot_lsl"]]) if row.get(self.config[small_prop + "_tot_lsl"], "--") != "--" else pm_tot_lsl
                pm_tot_usl = elib.tonum(row[self.config[small_prop + "_tot_usl"]]) if row.get(self.config[small_prop + "_tot_usl"], "--") != "--" else pm_tot_usl
                pm_no_of_stopagges = elib.tonum(row[self.config[small_prop + "_no_of_stopagges"]]) if row.get(self.config[small_prop + "_no_of_stopagges"], "--") != "--" else pm_no_of_stopagges
                pm_stoppage_duration = elib.tonum(row[self.config[small_prop + "_stoppage_duration"]]) if row.get(self.config[small_prop + "_stoppage_duration"], "--") != "--" else pm_stoppage_duration
                pm_sku = elib.tonum(row[self.config[small_prop + "_sku"]]) if row.get(self.config[small_prop + "_sku"], "--") != "--" else pm_sku

                _dict[prop][fbtime]["TotalWeightAcceptedPacks"] = elib.tonum(pm_tot_weight_accepted_packs)
                _dict[prop][fbtime]["PackingAverageRate"] = elib.tonum(packing_pm_average_rate)
                _dict[prop][fbtime]["NoOfPacksInAcceptedBand"] = elib.tonum(pm_no_of_packs_in_accepted_band)
                _dict[prop][fbtime]["TotalAcceptedPacks"] = elib.tonum(pm_tot_accepted_packs)
                _dict[prop][fbtime]["TotalRejectedPacks"] = elib.tonum(pm_tot_rejected_packs)
                _dict[prop][fbtime]["TotalJointPacks"] = elib.tonum(pm_tot_joint_packs)
                _dict[prop][fbtime]["TotalLSL"] = elib.tonum(pm_tot_lsl)
                _dict[prop][fbtime]["TotalUSL"] = elib.tonum(pm_tot_usl)
                _dict[prop][fbtime]["NoOfStopagges"] = elib.tonum(pm_no_of_stopagges)
                _dict[prop][fbtime]["StoppageDuration"] = elib.tonum(pm_stoppage_duration)
                _dict[prop][fbtime]["SKU"] = elib.tonum(pm_sku)
                _dict[prop][fbtime]["Time"] = fbtime                
                _dict[prop][fbtime]["Prop"] = prop
                
        return _dict

    def get_today_cbb_records(self, dateparam = ""):
        self.log.info("Data Push Started...")
        # dateparam = "2018-11-01"
        target_dict = self.read_from_db_CBB(dateparam)
        # print target_dict
        connection = MongoClient('127.0.0.1', username="admin", password="admin123", authSource='analyse_db', authMechanism='SCRAM-SHA-1')
        myDb = connection["analyse_db"]
        self._date = dateparam
        self.log.info("self._date: %s", self._date)
        # # mydb = client['analyse_db']
        dbData = []
        for prop in target_dict:
            # print prop
            for key in target_dict[prop]:
                if target_dict[prop][key] not in ["", None, []]:
                    row = {}
                    row = target_dict[prop][key]
                    row.setdefault("asofdate", self._date)
                    dbData.append(row)
        if dbData != []:
            myDb["packing_cbb_staging"].remove({'asofdate':self._date})
            record_id = myDb["packing_cbb_staging"].insert_many(dbData)
            self.log.info('%s records found', str(len(dbData)))
            self.log.info("DB Push Completed...PackingCBB")
        else:
            self.log.info("No Data...PackingCBB")

    def get_today_records(self, dateparam = ""):
        self.log.info("Data Push Started...")
        # dateparam = "2018-11-01"
        target_dict = self.read_from_db(dateparam)
        # print target_dict
        connection = MongoClient('127.0.0.1', username="admin", password="admin123", authSource='analyse_db', authMechanism='SCRAM-SHA-1')
        myDb = connection["analyse_db"]
        self._date = dateparam
        self.log.info("self._date: %s", self._date)
        # # mydb = client['analyse_db']
        dbData = []
        for prop in target_dict:
            # print prop
            for key in target_dict[prop]:
                if target_dict[prop][key] not in ["", None, []]:
                    row = {}
                    row = target_dict[prop][key]
                    row.setdefault("asofdate", self._date)
                    dbData.append(row)
        if dbData != []:
            myDb["packing_staging_lineB"].remove({'asofdate':self._date})
            record_id = myDb["packing_staging_lineB"].insert_many(dbData)
            self.log.info('%s records found', str(len(dbData)))
            self.log.info("DB Push Completed...Packing")
        else:
            self.log.info("No Data...Packing")
    
    def get_packing_report(self, dateparam):
        result = {}
        self.read_settings()
        yesterdayDate = datetime.strptime(dateparam, '%Y-%m-%d')
        _date2460 = yesterdayDate + timedelta(minutes = (24*60))
        todayDate = _date2460.strftime('%Y-%m-%d')
        selectedDate = yesterdayDate.strftime("%Y-%m-%d")

        selectedDateTime = selectedDate + " 06:30"
        todayDateTime = todayDate + " 05:30"
        timerange = []
        timerange.append(selectedDateTime)
        while selectedDateTime != todayDateTime:
            _date = datetime.strptime(selectedDateTime, '%Y-%m-%d %H:%M')
            _date_60 = _date + timedelta(minutes = 60)
            selectedDateTime = _date_60.strftime('%Y-%m-%d %H:%M')
            timerange.append(selectedDateTime)
        timerange = sorted(timerange)
        out_result = []

        find_dict = {"asofdate":selectedDate}

        connection = MongoClient('127.0.0.1', username="admin", password="admin123", authSource='analyse_db', authMechanism='SCRAM-SHA-1')
        myDb = connection["analyse_db"]
        db = myDb["packing_staging_lineB"]
        item_count = db.count_documents(find_dict)
        if item_count == 0:
            self.log.info("Data not available in staging... Getting From Mains...")
            self.get_today_records(selectedDate)
            find_dict = {"asofdate":selectedDate}
            item_count = db.count_documents(find_dict)
        self.log.info(item_count)

        _dict = {}
        if item_count > 0:
            dbresult = db.find(find_dict)
            for dt in dbresult:
                if dt != []:        
                    if str(dt["Prop"]) not in _dict.keys():
                        _dict.setdefault(str(dt["Prop"]), [])
                    _dict[str(dt["Prop"])].append(dt)
        
        final_dict = {}
        if _dict != {}:
            target_dict = {}
            
            for prop in self.reportKeys:
                out_rows = []
                stage_data = _dict[prop]
                for node in stage_data:
                    xTime = node["Time"]
                    xDateTime =  xTime.strftime("%Y-%m-%d %H:%M")
                    
                    #production
                    # if xDateTime in timerange:
                    packing_average_rate = elib.tonum(node["PackingAverageRate"])
                    tot_weight_accepted_packs = elib.tonum(node["TotalWeightAcceptedPacks"])
                    tot_accepted_packs = elib.tonum(node["TotalAcceptedPacks"])
                    tot_rejected_packs = elib.tonum(node["TotalRejectedPacks"])
                    tot_joint_packs = elib.tonum(node["TotalJointPacks"])
                    tot_lsl = elib.tonum(node["TotalLSL"])
                    tot_usl = elib.tonum(node["TotalUSL"])
                    stopagges = elib.tonum(node["NoOfStopagges"])
                    stoppage_duration = elib.tonum(node["StoppageDuration"])
                    no_of_packs = elib.tonum(node["NoOfPacksInAcceptedBand"])
                    sku = elib.tonum(node["SKU"])
                    
                    elib.dictIncrement(target_dict, xDateTime, "TotalWeightAcceptedPacks", [tot_weight_accepted_packs])
                    elib.dictIncrement(target_dict, xDateTime, "PackingAverageRate", [packing_average_rate])

                    elib.dictIncrement(target_dict, xDateTime, "TotalAcceptedPacks", [tot_accepted_packs])
                    elib.dictIncrement(target_dict, xDateTime, "TotalRejectedPacks", [tot_rejected_packs])
                    elib.dictIncrement(target_dict, xDateTime, "TotalJointPacks", [tot_joint_packs])
                    elib.dictIncrement(target_dict, xDateTime, "TotalLSL", [tot_lsl])
                    elib.dictIncrement(target_dict, xDateTime, "TotalUSL", [tot_usl])

                    elib.dictIncrement(target_dict, xDateTime, "NoOfStopagges", [stopagges])
                    elib.dictIncrement(target_dict, xDateTime, "StoppageDuration", [stoppage_duration])
                    elib.dictIncrement(target_dict, xDateTime, "NoOfPacksInAcceptedBand", [no_of_packs])
                    elib.dictIncrement(target_dict, xDateTime, "SKU", [sku])

                for xtime in timerange:
                    packing_average_rate = max(target_dict.get(xtime,{}).get("PackingAverageRate",[0]))
                    tot_weight_accepted_packs = elib.rnd(max(target_dict.get(xtime,{}).get("TotalWeightAcceptedPacks",[0])),0)
                    tot_accepted_packs = elib.rnd(max(target_dict.get(xtime,{}).get("TotalAcceptedPacks",[0])),0)
                    tot_rejected_packs = elib.rnd(max(target_dict.get(xtime,{}).get("TotalRejectedPacks",[0])),0)
                    tot_joint_packs = elib.rnd(max(target_dict.get(xtime,{}).get("TotalJointPacks",[0])),0)
                    tot_lsl = elib.rnd(max(target_dict.get(xtime,{}).get("TotalLSL",[0])),0)
                    tot_usl = elib.rnd(max(target_dict.get(xtime,{}).get("TotalUSL",[0])),0)
                    stopagges = elib.rnd(max(target_dict.get(xtime,{}).get("NoOfStopagges",[0])),0)
                    stoppage_duration = elib.rnd(max(target_dict.get(xtime,{}).get("StoppageDuration",[0])),0)
                    no_of_packs = elib.rnd(max(target_dict.get(xtime,{}).get("NoOfPacksInAcceptedBand",[0])),0)
                    sku = elib.rnd(max(target_dict.get(xtime,{}).get("SKU",[0])),0)

                    max_rejected = max(target_dict.get(xtime,{}).get("TotalRejectedPacks",[0]))
                    max_accepted = max(target_dict.get(xtime,{}).get("TotalAcceptedPacks",[0]))
                    if max_accepted in [0, 1]:
                        max_accepted = 1
                        avg_eff = max_rejected / 100
                    else:
                        avg_eff = 1 - (max_rejected / max_accepted)
                    efficiency = elib.rnd(avg_eff, 2) * 100

                    elib.dictIncrement(final_dict, xtime,"PackingAverageRate", packing_average_rate)
                    elib.dictIncrement(final_dict, xtime,"TotalWeightAcceptedPacks",tot_weight_accepted_packs)
                    elib.dictIncrement(final_dict, xtime,"TotalAcceptedPacks",tot_accepted_packs)
                    elib.dictIncrement(final_dict, xtime,"TotalRejectedPacks",tot_rejected_packs)
                    elib.dictIncrement(final_dict, xtime,"TotalJointPacks",tot_joint_packs)
                    elib.dictIncrement(final_dict, xtime,"TotalLSL",tot_lsl)
                    elib.dictIncrement(final_dict, xtime,"TotalUSL",tot_usl)
                    elib.dictIncrement(final_dict, xtime,"NoOfStopagges",stopagges)
                    elib.dictIncrement(final_dict, xtime,"StoppageDuration",stoppage_duration)
                    elib.dictIncrement(final_dict, xtime,"NoOfPacksInAcceptedBand",no_of_packs)
                    elib.dictIncrement(final_dict, xtime,"SKU",sku)
                    elib.dictIncrement(final_dict, xtime,"Efficiency",avg_eff)

                    row = {}
                    row.setdefault("Time", xtime)
                    row.setdefault("PackingAverageRate", packing_average_rate)
                    row.setdefault("TotalWeightAcceptedPacks",elib.rnd(tot_weight_accepted_packs, 2))
                    row.setdefault("TotalAcceptedPacks",tot_accepted_packs)
                    row.setdefault("TotalRejectedPacks",tot_rejected_packs)
                    row.setdefault("TotalJointPacks",tot_joint_packs)
                    row.setdefault("TotalLSL",tot_lsl)
                    row.setdefault("TotalUSL",tot_usl)
                    row.setdefault("NoOfStopagges",stopagges)
                    row.setdefault("StoppageDuration",stoppage_duration)
                    row.setdefault("NoOfPacksInAcceptedBand",no_of_packs)
                    row.setdefault("SKU",sku)
                    row.setdefault("Efficiency",str(efficiency) + '%')

                    out_rows.append(row)

                out_result.append({
                    "prop": prop,
                    "data": out_rows
                })
        out_rows = []
        if final_dict != {}:
            for xtime in timerange:
                row = {}
                row.setdefault("Time", xtime)
                row.setdefault("PackingAverageRate", final_dict[xtime]["PackingAverageRate"])
                row.setdefault("TotalWeightAcceptedPacks",elib.rnd(final_dict[xtime]["TotalWeightAcceptedPacks"],2))
                row.setdefault("TotalAcceptedPacks",elib.rnd(final_dict[xtime]["TotalAcceptedPacks"], 0))
                row.setdefault("TotalRejectedPacks",elib.rnd(final_dict[xtime]["TotalRejectedPacks"], 0))
                row.setdefault("TotalJointPacks",elib.rnd(final_dict[xtime]["TotalJointPacks"], 0))
                row.setdefault("TotalLSL",elib.rnd(final_dict[xtime]["TotalLSL"], 0))
                row.setdefault("TotalUSL",elib.rnd(final_dict[xtime]["TotalUSL"], 0))
                row.setdefault("NoOfStopagges",elib.rnd(final_dict[xtime]["NoOfStopagges"], 0))
                row.setdefault("StoppageDuration",elib.rnd(final_dict[xtime]["StoppageDuration"], 0))
                row.setdefault("NoOfPacksInAcceptedBand",elib.rnd(final_dict[xtime]["NoOfPacksInAcceptedBand"], 0))
                row.setdefault("SKU",elib.rnd(final_dict[xtime]["SKU"],  0))

                max_rejected = final_dict[xtime]["TotalRejectedPacks"]
                max_accepted = final_dict[xtime]["TotalAcceptedPacks"]
                if max_accepted in [0, 1]:
                    max_accepted = 1
                    avg_eff = max_rejected / 100
                else:
                    avg_eff = 1 - (max_rejected / max_accepted)
                efficiency = elib.rnd(avg_eff, 2) * 100
                row.setdefault("Efficiency",str(efficiency) + '%')

                out_rows.append(row)
        out_result.insert(0, {
            "prop": "Packing",
            "data": out_rows
        })

        cbb_rows = self.get_cbb_report(dateparam)
        out_result.append({
            "prop":"CBB Overview",
            "data": cbb_rows
        })

        return out_result

    def get_cbb_report(self, dateparam):
        result = {}
        self.read_settings()
        yesterdayDate = datetime.strptime(dateparam, '%Y-%m-%d')
        _date2460 = yesterdayDate + timedelta(minutes = (24*60))
        todayDate = _date2460.strftime('%Y-%m-%d')
        selectedDate = yesterdayDate.strftime("%Y-%m-%d")

        selectedDateTime = selectedDate + " 07:00"
        todayDateTime = todayDate + " 07:00"
        timerange = []
        timerange.append(selectedDateTime)
        while selectedDateTime != todayDateTime:
            _date = datetime.strptime(selectedDateTime, '%Y-%m-%d %H:%M')
            _date_60 = _date + timedelta(minutes = 60)
            selectedDateTime = _date_60.strftime('%Y-%m-%d %H:%M')
            timerange.append(selectedDateTime)
        timerange = sorted(timerange)
        out_result = []

        find_dict = {"asofdate":selectedDate}

        connection = MongoClient('127.0.0.1', username="admin", password="admin123", authSource='analyse_db', authMechanism='SCRAM-SHA-1')
        myDb = connection["analyse_db"]
        # myDb = connection["analyse_db"]
        db = myDb["packing_cbb_staging"]
        item_count = db.count_documents(find_dict)
        if item_count == 0:
            self.log.info("Data not available in staging... Getting From Mains...")
            self.get_today_cbb_records(selectedDate)
            find_dict = {"asofdate":selectedDate}
            item_count = db.count_documents(find_dict)
        self.log.info(item_count)

        _dict = {}
        if item_count > 0:
            dbresult = db.find(find_dict)
            for dt in dbresult:
                if dt != []:        
                    if str(dt["Prop"]) not in _dict.keys():
                        _dict.setdefault(str(dt["Prop"]), [])
                    _dict[str(dt["Prop"])].append(dt)
        
        final_dict = {}
        out_rows = []
        if _dict != {}:
            target_dict = {}
            final_dict = {}
            prop = "cbb"
            stage_data = _dict[prop]
            for node in stage_data:
                xTime = node["Time"]
                xDateTime =  xTime.strftime("%Y-%m-%d %H:%M")

                weight = elib.tonum(node["Weight"])
                averageWeight = elib.tonum(node["AverageWeight"])
                stoppageDuration = elib.tonum(node["StoppageDuration"])
                noOfStopagges = elib.tonum(node["NoOfStopagges"])
                acceptedPacks = elib.tonum(node["AcceptedPacks"])
                tot_usl = elib.tonum(node["TotalUSL"])
                tot_lsl = elib.tonum(node["TotalLSL"])
                if xDateTime in timerange:
                    elib.dictIncrement(target_dict, xDateTime, "Weight", [weight])
                    elib.dictIncrement(target_dict, xDateTime, "AverageWeight", [averageWeight])

                    elib.dictIncrement(target_dict, xDateTime, "StoppageDuration", [stoppageDuration])
                    elib.dictIncrement(target_dict, xDateTime, "NoOfStopagges", [noOfStopagges])
                    elib.dictIncrement(target_dict, xDateTime, "AcceptedPacks", [acceptedPacks])
                    elib.dictIncrement(target_dict, xDateTime, "TotalUSL", [tot_usl])
                    elib.dictIncrement(target_dict, xDateTime, "TotalLSL", [tot_lsl])

            for xtime in timerange:
                weight = max(target_dict.get(xtime,{}).get("Weight",[0]))
                averageWeight = elib.rnd(max(target_dict.get(xtime,{}).get("AverageWeight",[0])),0)
                acceptedPacks = elib.rnd(max(target_dict.get(xtime,{}).get("AcceptedPacks",[0])),0)
                tot_lsl = elib.rnd(max(target_dict.get(xtime,{}).get("TotalLSL",[0])),0)
                tot_usl = elib.rnd(max(target_dict.get(xtime,{}).get("TotalUSL",[0])),0)
                stopagges = elib.rnd(max(target_dict.get(xtime,{}).get("NoOfStopagges",[0])),0)
                stoppage_duration = elib.rnd(max(target_dict.get(xtime,{}).get("StoppageDuration",[0])),0)

                row = {}
                row.setdefault("Time", xtime)
                row.setdefault("Weight", elib.rnd(weight,2))
                row.setdefault("AverageWeight",elib.rnd(averageWeight, 2))
                row.setdefault("AcceptedPacks",acceptedPacks)
                row.setdefault("TotalLSL",tot_lsl)
                row.setdefault("TotalUSL",tot_usl)
                row.setdefault("NoOfStopagges",stopagges)
                row.setdefault("StoppageDuration",stoppage_duration)

                out_rows.append(row)

        return out_rows

    def downloadPackingReport(self, dateparam, out_list):

        selectedDate = dateparam
        fileCompleted = []
        all_rows = []
        data_list = []
        txtfilename = FILE_PATH + "packing_moulder.txt"
        keyheaders = ["Time", "PackingAverageRate", "TotalWeightAcceptedPacks", "TotalAcceptedPacks", "TotalRejectedPacks", "TotalJointPacks", "TotalLSL", "TotalUSL", "NoOfStopagges", "StoppageDuration", "NoOfPacksInAcceptedBand", "SKU", "Efficiency"]
        headers = ["Time", "Packing Average Rate", "Total Weight Accepted Packs", "Total Accepted Packs", "Total Rejected Packs", "Total Joint Packs", "Total LSL", "Total USL", "No Of Stopagges", "Stoppage Duration", "No Of Packs In Accepted Band", "SKU", "Efficiency"]
        cbbkeyheaders = ["Time", "Weight", "AverageWeight", "AcceptedPacks", "TotalLSL", "TotalUSL", "NoOfStopagges", "StoppageDuration"]
        cbbheaders = ["Time", "Weight", "Average Weight", "Accepted Packs", "Total LSL", "Total USL", "No Of Stopagges", "Stoppage Duration"]
        reportKeys = ["Packing"] + self.reportKeys + ["CBB Overview"]
        
        data_list = []
        fileCompleted = []
        s = ""
        
        for node in out_list:
            prop = node["prop"]
            data = node["data"]
            txtfilename = FILE_PATH + node["prop"].lower().replace(" ", "_") + ".txt"
            s = ""
            data_list = []
            if prop != "CBB Overview":
                for hd in headers:
                    s += str(hd)
                    index = headers.index(hd)
                    if index < len(headers) - 1:
                        s += "\t"
                data_list.append(s)

                for datanode in data:
                    s = ""
                    for key in keyheaders:
                        s += str(datanode.get(key,""))
                        index = keyheaders.index(key)
                        if index < len(keyheaders) - 1:
                            s += "\t"
                    data_list.append(s)
            else:
                for hd in cbbheaders:
                    s += str(hd)
                    index = cbbheaders.index(hd)
                    if index < len(cbbheaders) - 1:
                        s += "\t"
                data_list.append(s)

                for datanode in data:
                    s = ""
                    for key in cbbkeyheaders:
                        s += str(datanode.get(key,""))
                        index = cbbkeyheaders.index(key)
                        if index < len(cbbkeyheaders) - 1:
                            s += "\t"
                    data_list.append(s)
            fileAttr = {"txt": txtfilename, "name": node["prop"]}
            outF = open(txtfilename, "w")
            for line in data_list:
                outF.write(line)
                outF.write("\n")
            outF.close()
            fileCompleted.append(fileAttr)

        out_pdf= FILE_PATH + 'Packing_Demo_'+selectedDate+'.pdf'
        intermediate_html = FILE_PATH + 'intermediate.html'
        reportTitle = "Packing Daily Report"

        htmlToAdd = '<div style="margin-left:10px;margin-top:20px;text-align:center;border:1px solid white;">'\
                        '<div style="text-center:left;margin-left:1rem;margin-right:1rem;margin-top:500px;">'\
                            '<img src="' + CONFIG_PATH + 'abz2_big.png" style=""/>'\
                            '<div style="text-align:center;color:#323232;font-size:35px;margin-top:5px;">'\
                                '<span style="color:#323232;font-size:35px;margin-right:2rem;">'+reportTitle+'</span>'\
                            '</div>'\
                            '<div style="text-align:center;color:#323232;font-size:35rem;margin-top:5px;">'\
                                '<span style="color:#323232;font-size:30px;"> Generation Date ('+selectedDate+') </span>'\
                            '</div>'\
                        '</div>'\
                    '</div>'
        newhtmlToAdd = ''
        if os.path.exists(intermediate_html):
            os.remove(intermediate_html)
        for key in reportKeys:
            for fattr in fileCompleted:
                if fattr["name"] == key:
                    df = pd.read_csv(fattr["txt"], delimiter="\t", delim_whitespace=False)
                    intermediate_html = FILE_PATH + 'intermediate.html'
                    self.to_html_pretty(df, intermediate_html,fattr["name"], htmlToAdd, newhtmlToAdd, reportTitle, selectedDate)
                    htmlToAdd = ""
                    newhtmlToAdd = '<div style="margin-left:5px;margin-top:2px;border:1px solid white;">'\
                        '<div style="text-align:left;margin-left:1rem;margin-right:1rem;">'\
                            '<img src="' + CONFIG_PATH + 'abz2_small.png" style="margin-right:100px;"/>'\
                            '<span style="margin-left:120px;text-align:center;color:#323232;font-size:22px;">'\
                                '<span style="color:#323232;font-size:22px;margin-right:2rem;">'+reportTitle+'</span>'\
                            '</span>'\
                            '<span style="text-align:right;color:#323232;font-size:22px;margin-left:130px;">'\
                                '<span style="color:#323232;font-size:22px;"> Generation Date ('+selectedDate+') </span>'\
                            '</span>'\
                        '</div>'\
                    '</div>'
                    os.remove(fattr["txt"])
        options = {'orientation': 'Landscape'}
        # pdfkit.from_file(intermediate_html, out_pdf,options=options,configuration = config)
        pdfkit.from_file(intermediate_html, out_pdf,options=options)
        return out_pdf
    
    def to_html_pretty(self, df, filename='out.html', title='', htmlToAdd='', newhtmlToAdd='', reportTitle='', selectedDate=''):
        ht = ''
        if htmlToAdd != '':
            ht += htmlToAdd
        if title != '':
            ht += '<h1><img src="' + CONFIG_PATH + 'abz2_small.png" style="margin-right:100px;margin-top:5px;"/>'
            ht += '<span style="margin-left:120px;text-align:center;color:#323232;font-size:22px;">'\
                                '<span style="color:#323232;font-size:18px;margin-right:2rem;">'+reportTitle+'</span>'\
                            '</span>'\
                            '<span style="text-align:right;color:#323232;font-size:22px;margin-left:130px;">'\
                                '<span style="color:#323232;font-size:18px;"> Generation Date ('+selectedDate+') </span>'\
                            '</span></h1>'
            ht += '<h2> %s </h2>\n' % title
        ht += df.to_html(classes='wide', escape=False)

        with open(filename, 'a') as f:
             f.write(HTML_TEMPLATE1 + ht + HTML_TEMPLATE2)

    def save_packing_report(self, dateparam):
        self.log.info("Saving Report...Packing")
        out_list = self.get_packing_report(dateparam)
        filename = self.downloadPackingReport(dateparam, out_list)
        path = FILE_PATH
        uuidstr = str(uuid.uuid4())
        filepath = filename

        return filepath
    
    def save_packing_home(self, dateparam):
        self.log.info("Saving Dashboard Report...Packing")
        filename = self.get_packing_home(dateparam)
        path = FILE_PATH
        uuidstr = str(uuid.uuid4())
        filepath = filename

        return filepath


    def get_losses_report(self, dateparam):
        result = {}
        self.read_settings()

        yesterdayDate = datetime.strptime(dateparam, '%Y-%m-%d')
        _date2460 = yesterdayDate + timedelta(minutes = (24*60))
        todayDate = _date2460.strftime('%Y-%m-%d')
        selectedDate = yesterdayDate.strftime("%Y-%m-%d")

        selectedDateTime = selectedDate + " 06:30"
        todayDateTime = todayDate + " 05:30"
        timerange = []
        timerange.append(selectedDateTime)
        while selectedDateTime != todayDateTime:
            _date = datetime.strptime(selectedDateTime, '%Y-%m-%d %H:%M')
            _date_60 = _date + timedelta(minutes = 60)
            selectedDateTime = _date_60.strftime('%Y-%m-%d %H:%M')
            timerange.append(selectedDateTime)
        timerange = sorted(timerange)
        out_result = []

        find_dict = {"asofdate":selectedDate}
        connection = MongoClient('127.0.0.1', username="admin", password="admin123", authSource='analyse_db', authMechanism='SCRAM-SHA-1')
        myDb = connection["analyse_db"]
        db = myDb["packing_staging_lineB"]
        item_count = db.count_documents(find_dict)
        if item_count == 0:
            self.log.info("Data not available in staging... Getting From Mains...")
            self.get_today_records(selectedDate)
            find_dict = {"asofdate":selectedDate}
            item_count = db.count_documents(find_dict)
        self.log.info(item_count)

        _dict = {}
        if item_count > 0:
            dbresult = db.find(find_dict)
            for dt in dbresult:
                if dt != []:        
                    if str(dt["Prop"]) not in _dict.keys():
                        _dict.setdefault(str(dt["Prop"]), [])
                    _dict[str(dt["Prop"])].append(dt)
        find_dict = {"asofdate":todayDate}
        item_count = db.count_documents(find_dict)
        
        if item_count == 0:
            self.log.info("Data not available in staging... Getting From Mains...")
            self.get_today_records(todayDate)
            find_dict = {"asofdate":todayDate}
            item_count = db.count_documents(find_dict)
        self.log.info(item_count)
        if item_count > 0:
            dbresult = db.find(find_dict)            
            for dt in dbresult:
                if dt != []:        
                    if str(dt["Prop"]) not in _dict.keys():
                        _dict.setdefault(str(dt["Prop"]), [])
                    _dict[str(dt["Prop"])].append(dt)
        final_dict = {}
        if _dict != {}:
            target_dict = {}
            
            for prop in self.reportKeys:
                out_rows = []
                stage_data = _dict[prop]
                for node in stage_data:
                    xTime = node["Time"]
                    xDateTime =  xTime.strftime("%Y-%m-%d %H:%M")
                    # if xDateTime in timerange:
                    tot_weight_accepted_packs = elib.rnd(elib.tonum(node["TotalWeightAcceptedPacks"]),2)
                    tot_set_point = elib.rnd(elib.tonum(node["TotalWeightAcceptedPacks"]),2)
                    tot_accepted_packs = elib.tonum(node["TotalAcceptedPacks"])
                    no_of_packs = elib.tonum(node["NoOfPacksInAcceptedBand"])
                    sku = elib.tonum(node["SKU"])

                    elib.dictIncrement(target_dict, xDateTime, "TotalWeightAcceptedPacks", [tot_weight_accepted_packs])
                    elib.dictIncrement(target_dict, xDateTime, "TotalSetPoint", [tot_set_point])
                    elib.dictIncrement(target_dict, xDateTime, "NoOfPacksInAcceptedBand", [no_of_packs])
                    elib.dictIncrement(target_dict, xDateTime, "SKU", [sku])

                for xtime in timerange:
                    tot_weight_accepted_packs = elib.rnd(max(target_dict.get(xtime,{}).get("TotalWeightAcceptedPacks",[0])),0)
                    tot_set_point = elib.rnd(max(target_dict.get(xtime,{}).get("TotalSetPoint",[0])),0)
                    no_of_packs = elib.rnd(max(target_dict.get(xtime,{}).get("NoOfPacksInAcceptedBand",[0])),0)
                    sku = elib.rnd(max(target_dict.get(xtime,{}).get("SKU",[0])),0)

                    give_away_losses = tot_weight_accepted_packs - tot_set_point

                    elib.dictIncrement(final_dict, xtime,"TotalWeightAcceptedPacks", tot_weight_accepted_packs)
                    elib.dictIncrement(final_dict, xtime,"TotalSetPoint",tot_set_point)
                    elib.dictIncrement(final_dict, xtime,"NoOfPacksInAcceptedBand",no_of_packs)
                    elib.dictIncrement(final_dict, xtime,"SKU",sku)
                    elib.dictIncrement(final_dict, xtime,"GiveAwayLoss",give_away_losses)

                    row = {}
                    row.setdefault("Time", xtime)
                    row.setdefault("TotalWeightAcceptedPacks",elib.rnd(tot_weight_accepted_packs, 2))
                    row.setdefault("TotalSetPoint",elib.rnd(tot_set_point, 2))
                    row.setdefault("NoOfPacksInAcceptedBand",no_of_packs)
                    row.setdefault("SKU",sku)
                    row.setdefault("GiveAwayLoss",give_away_losses)

                    out_rows.append(row)

                out_result.append({
                    "prop": prop,
                    "data": out_rows
                })
        out_rows = []
        if final_dict != {}:
            for xtime in timerange:
                row = {}
                row.setdefault("Time", xtime)
                row.setdefault("TotalWeightAcceptedPacks",elib.rnd(final_dict[xtime]["TotalWeightAcceptedPacks"],2))
                row.setdefault("TotalSetPoint",elib.rnd(final_dict[xtime]["TotalSetPoint"], 0))
                row.setdefault("NoOfPacksInAcceptedBand",elib.rnd(final_dict[xtime]["NoOfPacksInAcceptedBand"], 0))
                row.setdefault("SKU",elib.rnd(final_dict[xtime]["SKU"],  0))

                tot_weight_accepted_packs = final_dict[xtime]["TotalWeightAcceptedPacks"]
                tot_set_point = final_dict[xtime]["TotalSetPoint"]
                give_away_losses = tot_weight_accepted_packs - tot_set_point
                
                row.setdefault("GiveAwayLoss",give_away_losses)

                out_rows.append(row)
        out_result.insert(0, {
            "prop": "Packing",
            "data": out_rows
        })

        return out_result

    def downloadLossesReport(self, dateparam, out_list):
        selectedDate = dateparam

        fileCompleted = []
        all_rows = []
        data_list = []
        txtfilename = "losses_report.txt"
        keyheaders = ["Time", "TotalWeightAcceptedPacks", "TotalSetPoint", "NoOfPacksInAcceptedBand", "SKU", "GiveAwayLoss"]
        headers = ["Time", "Total Weight Accepted Packs", "Total Set Point", "No Of Packs In Accepted Band", "SKU", "Give Away Loss"]

        reportKeys = ["Packing"] + self.reportKeys
        
        data_list = []
        fileCompleted = []
        s = ""
        
        for node in out_list:
            data = node["data"]
            txtfilename = node["prop"].lower().replace(" ", "_") + ".txt"
            s = ""
            data_list = []
            for hd in headers:
                s += str(hd)
                index = headers.index(hd)
                if index < len(headers) - 1:
                    s += "\t"
            data_list.append(s)

            for datanode in data:
                s = ""
                for key in keyheaders:
                    s += str(datanode.get(key,""))
                    index = keyheaders.index(key)
                    if index < len(keyheaders) - 1:
                        s += "\t"
                data_list.append(s)
            fileAttr = {"txt": txtfilename, "name": node["prop"]}
            outF = open(txtfilename, "w")
            for line in data_list:
                outF.write(line)
                outF.write("\n")
            outF.close()
            fileCompleted.append(fileAttr)

        out_pdf= FILE_PATH + 'Losses_Demo_'+selectedDate+'.pdf'
        intermediate_html = 'intermediate.html'
        reportTitle = "Losses Daily Report"

        htmlToAdd = '<div style="margin-left:10px;margin-top:20px;text-align:center;border:1px solid white;">'\
                        '<div style="text-center:left;margin-left:1rem;margin-right:1rem;margin-top:500px;">'\
                            '<img src="' + CONFIG_PATH + 'abz2_big.png" style=""/>'\
                            '<div style="text-align:center;color:#323232;font-size:35px;margin-top:5px;">'\
                                '<span style="color:#323232;font-size:35px;margin-right:2rem;">'+reportTitle+'</span>'\
                            '</div>'\
                            '<div style="text-align:center;color:#323232;font-size:35rem;margin-top:5px;">'\
                                '<span style="color:#323232;font-size:30px;"> Generation Date ('+selectedDate+') </span>'\
                            '</div>'\
                        '</div>'\
                    '</div>'
        newhtmlToAdd = ''
        if os.path.exists(intermediate_html):
            os.remove(intermediate_html)
        for key in reportKeys:
            for fattr in fileCompleted:
                if fattr["name"] == key:
                    df = pd.read_csv(fattr["txt"], delimiter="\t", delim_whitespace=False)
                    intermediate_html = 'intermediate.html'
                    self.to_html_pretty(df, intermediate_html,fattr["name"], htmlToAdd, newhtmlToAdd, reportTitle, selectedDate)
                    htmlToAdd = ""
                    newhtmlToAdd = '<div style="margin-left:5px;margin-top:2px;border:1px solid white;">'\
                        '<div style="text-align:left;margin-left:1rem;margin-right:1rem;">'\
                            '<img src="' + CONFIG_PATH + 'abz2_small.png" style="margin-right:100px;"/>'\
                            '<span style="margin-left:120px;text-align:center;color:#323232;font-size:22px;">'\
                                '<span style="color:#323232;font-size:22px;margin-right:2rem;">'+reportTitle+'</span>'\
                            '</span>'\
                            '<span style="text-align:right;color:#323232;font-size:22px;margin-left:130px;">'\
                                '<span style="color:#323232;font-size:22px;"> Generation Date ('+selectedDate+') </span>'\
                            '</span>'\
                        '</div>'\
                    '</div>'
                    os.remove(fattr["txt"])
        options = {'orientation': 'Landscape'}
        # pdfkit.from_file(intermediate_html, out_pdf,options=options,configuration = config)
        pdfkit.from_file(intermediate_html, out_pdf,options=options)
        return out_pdf

    def save_losses_report(self, dateparam):
        self.log.info("Saving Report...Losses")
        out_list = self.get_losses_report(dateparam)
        filename = self.downloadLossesReport(dateparam, out_list)
        path = FILE_PATH
        uuidstr = str(uuid.uuid4())
        filepath = filename

        return filepath
    
    def get_packing_home(self, dateparam):
        result = {}
        self.read_settings()

        yesterdayDate = datetime.strptime(dateparam, '%Y-%m-%d')
        _date2460 = yesterdayDate + timedelta(minutes = (24*60))
        todayDate = _date2460.strftime('%Y-%m-%d')
        selectedDate = yesterdayDate.strftime("%Y-%m-%d")

        selectedDateTime = selectedDate + " 06:30"
        todayDateTime = todayDate + " 05:30"
        timerange = []
        timerange.append(selectedDateTime)
        while selectedDateTime != todayDateTime:
            _date = datetime.strptime(selectedDateTime, '%Y-%m-%d %H:%M')
            _date_60 = _date + timedelta(minutes = 60)
            selectedDateTime = _date_60.strftime('%Y-%m-%d %H:%M')
            timerange.append(selectedDateTime)
        timerange = sorted(timerange)
        out_result = []
        html_list = []

        find_dict = {"asofdate":selectedDate}

        connection = MongoClient('127.0.0.1', username="admin", password="admin123", authSource='analyse_db', authMechanism='SCRAM-SHA-1')
        myDb = connection["analyse_db"]
        db = myDb["packing_staging_lineB"]
        item_count = db.count_documents(find_dict)
        if item_count == 0:
            self.log.info("Data not available in staging... Getting From Mains...")
            self.get_today_records(selectedDate)
            find_dict = {"asofdate":selectedDate}
            item_count = db.count_documents(find_dict)
        self.log.info(item_count)

        _dict = {}
        html_list = []
        if item_count > 0:
            dbresult = db.find(find_dict)
            for dt in dbresult: 
                if dt != []:        
                    if str(dt["Prop"]) not in _dict.keys():
                        _dict.setdefault(str(dt["Prop"]), [])
                    _dict[str(dt["Prop"])].append(dt)
        
        # print _dict
        if _dict != {}:
            target_dict = {}
            production = {}
            packets = {}
            efficiency = {}
            packing_rate = {}
            all_props = {}
            all_props.setdefault("Production", {})
            all_props.setdefault("Packets", {})
            all_props.setdefault("Efficiency", {})
            all_props.setdefault("PackingRate", {})
            legends_format = {
                'TotWeightAcceptedPacks':{
                    'name' : 'Production',
                    'color' : '#74d600',
                    'dashStyle' : 'Solid',
                    'type' : 'column',
                    'y':0,
                    'visible' : True
                },
                'MovingAverage' : {
                    'name' : '2 per. Moving Average(Production)',
                    'color' :'#e34566',
                    'dashStyle' : 'Solid',
                    'type' : 'line',
                    'y':0,
                    'visible' : True
                },
            }

            packing_legends = {
                'TotalAcceptedPacks' : {
                    'name' : 'Accepted',
                    'color' : '#08c',
                    'dashStyle' : 'Solid',
                    'type' : 'column',
                    'y':0,
                    'visible' : True
                },
                "TotalRejectedPacks" : {
                    'name' : 'Rejected',
                    'color' :'#e34566',
                    'dashStyle' : 'Solid',
                    'type' : 'line',
                    'y':1,
                    'visible' : True
                }
            }

            eff_legends_format = {
                'Efficiency':{
                    'name' : 'Efficiency',
                    'color' : '#008080',
                    'dashStyle' : 'Solid',
                    'type' : 'column',
                    'y':0,
                    'visible' : True
                },
                'MovingAverage' : {
                    'name' : '2 per. Moving Average(Efficiency)',
                    'color' :'#f08619',
                    'dashStyle' : 'Solid',
                    'type' : 'line',
                    'y':0,
                    'visible' : True
                },
            }

            packing_rate_legends = {
                'PackingAverageRate' : {
                    'name' : 'Average Packs',
                    'color' : '#ff0000',
                    'dashStyle' : 'Solid',
                    'type' : 'spline',
                    'y':0,
                    'visible' : True
                }
            }
            all_line_series = {}
            all_line_result = {}
            all_pack_line_series = {}
            all_pack_line_result = {}
            all_eff_line_series = {}
            all_eff_line_result = {}
            all_efficiency_donut_series = []
            all_pr_line_series = {}
            all_pr_line_result = {}

            for prop in self.reportKeys:
                production.setdefault(prop, {})
                packets.setdefault(prop, {})
                efficiency.setdefault(prop, {})
                packing_rate.setdefault(prop, {})
                stage_data = _dict[prop]
                #production
                line_series = {}
                line_data = {}
                line_result = {}
                max_pack = 0
                min_pack = 10000
                minTime = ""
                maxTime = ""

                #packets
                pack_line_series = {}
                pack_line_data = {}
                pack_line_result = {}

                #efficiency
                max_eff = 0
                max_eff_time = ""
                min_eff = 10000
                min_eff_time = ""
                eff_line_series = {}
                eff_line_data = {}
                eff_line_result = {}
                efficiency_donut_series = []

                #packing_rate
                pr_line_data = {}
                pr_line_series = {}
                pr_line_result = {}
                for leg in legends_format:
                    line_result[leg] = {
                        'name': legends_format[leg]['name'],
                        'data': [],
                        'yAxis': legends_format[leg]['y'],
                        'type': legends_format[leg]['type'],
                        'color': legends_format[leg]['color'],
                        'visible': legends_format[leg]['visible']
                    }
                for leg in packing_legends:
                    pack_line_result[leg] = {
                        'name': packing_legends[leg]['name'],
                        'data': [],
                        'yAxis': packing_legends[leg]['y'],
                        'type': packing_legends[leg]['type'],
                        'color': packing_legends[leg]['color'],
                        'visible': packing_legends[leg]['visible']
                    }
                for leg in eff_legends_format:
                    eff_line_result[leg] = {
                        'name': eff_legends_format[leg]['name'],
                        'data': [],
                        'yAxis': eff_legends_format[leg]['y'],
                        'type': eff_legends_format[leg]['type'],
                        'color': eff_legends_format[leg]['color'],
                        'visible': eff_legends_format[leg]['visible']
                    }
                for leg in packing_rate_legends:
                    pr_line_result[leg] = {
                        'name': packing_rate_legends[leg]['name'],
                        'data': [],
                        'yAxis': packing_rate_legends[leg]['y'],
                        'type': packing_rate_legends[leg]['type'],
                        'color': packing_rate_legends[leg]['color'],
                        'visible': packing_rate_legends[leg]['visible']
                    }
                for node in stage_data:
                    xTime = node["Time"]
                    xDateTime =  xTime.strftime("%Y-%m-%d %H:%M")
                    
                    #production
                    if xDateTime in timerange:
                        packing_average_rate = elib.tonum(node["PackingAverageRate"])
                        tot_weight_accepted_packs = elib.tonum(node["TotalWeightAcceptedPacks"])
                        elib.dictIncrement1D(target_dict, "TotWeightAcceptedPacks", [tot_weight_accepted_packs])
                        elib.dictIncrement1D(target_dict, "PackingAverageRate", [packing_average_rate])
                        
                        # if packing_average_rate > max_pack:
                        #     max_pack = packing_average_rate
                        #     maxTime = xDateTime
                        # if packing_average_rate < minTime:
                        #     min_pack = packing_average_rate
                        #     minTime = xDateTime
                        
                        elib.dictIncrement(line_data, xDateTime, "TotWeightAcceptedPacks", [tot_weight_accepted_packs])
                        elib.dictIncrement(pr_line_data, xDateTime, "PackingAverageRate", [packing_average_rate])

                    #packing
                        tot_accepted_packs = elib.tonum(node["TotalAcceptedPacks"])
                        tot_rejected_packs = elib.tonum(node["TotalRejectedPacks"])
                        tot_joint_packs = elib.tonum(node["TotalJointPacks"])
                        tot_lsl = elib.tonum(node["TotalLSL"])
                        tot_usl = elib.tonum(node["TotalUSL"])
                        stopagges = elib.tonum(node["NoOfStopagges"])
                        stoppage_duration = elib.tonum(node["StoppageDuration"])
                        if tot_accepted_packs in [0,1]: 
                            effc = tot_rejected_packs / 100
                        else:
                            effc = 1 - (tot_rejected_packs/tot_accepted_packs)
                        effc = elib.rnd(effc, 2) * 100
                        avg_eff = effc * 100

                        # if tot_accepted_packs > max_eff:
                        #     max_eff = tot_accepted_packs
                        #     max_eff_time = xDateTime
                        # if tot_accepted_packs < min_eff:
                        #     min_eff = tot_accepted_packs
                        #     min_eff_time = xDateTime

                        elib.dictIncrement1D(target_dict, "TotalAcceptedPacks", [tot_accepted_packs])
                        elib.dictIncrement1D(target_dict, "TotalRejectedPacks", [tot_rejected_packs])
                        elib.dictIncrement1D(target_dict, "TotalJointPacks", [tot_joint_packs])
                        elib.dictIncrement1D(target_dict, "TotalLSL", [tot_lsl])
                        elib.dictIncrement1D(target_dict, "TotalUSL", [tot_usl])

                        elib.dictIncrement1D(target_dict, "Efficiency", [effc])
                        elib.dictIncrement1D(target_dict, "Stoppages", [stopagges])
                        elib.dictIncrement1D(target_dict, "StoppageDuration", [stoppage_duration])

                        elib.dictIncrement(pack_line_data, xDateTime, "TotalAcceptedPacks", [tot_accepted_packs])
                        elib.dictIncrement(pack_line_data, xDateTime, "TotalRejectedPacks", [tot_rejected_packs])

                        # elib.dictIncrement(eff_line_data, xDateTime, "Efficiency", [effc])

                for xtime in sorted(line_data.keys()):
                    line_series.setdefault(xtime,{})
                    for key in line_data[xtime]:
                        avg = sum(line_data[xtime][key]) / len(line_data[xtime][key])
                        line_series[xtime].setdefault(key, elib.rnd(avg,2))
                        elib.dictIncrement(all_line_series, xtime, key, elib.rnd(avg,2))

                series_keys = sorted(line_series.keys())
                for xtime in series_keys:
                    index = series_keys.index(xtime)
                    if index > 0:
                        firstVal = line_series[series_keys[index-1]]["TotWeightAcceptedPacks"]
                        secondVal = line_series[xtime]["TotWeightAcceptedPacks"]
                        avg = (firstVal + secondVal) / 2
                        line_series[xtime].setdefault("MovingAverage", elib.rnd(avg,2))
                    else:
                        line_series[xtime].setdefault("MovingAverage", None)
                xAxis = []
                for xtime in sorted(line_series.keys()):
                    for leg in legends_format:
                        line_result[leg]["data"].append({
                            "category": xtime[11:],
                            "y": elib.rnd(line_series[xtime][leg],2)
                        })
                    xAxis.append(xtime[11:])
                chartResult = []
                isData = False
                for leg in legends_format:
                    if len(line_result[leg]['data']) > 0:
                        isData = True
                    chartResult.append(line_result[leg])

                chartObj = {}
                chartObj["categories"] = list(set(xAxis))
                chartObj['charttype'] = 'linechart'
                chartObj['id'] = 'line_'+prop.lower().replace(' ', '_')
                chartObj['series'] = chartResult
                chartObj['isData'] = isData
                
                linechart = Highchart()
                lineoptions = {
                    'chart': {
                        # 'type': 'column',
                        'height': 250,
                        'width': 1050,
                        'spacingTop':10,
                        'spacingLeft':5,
                        'spacingBottom':10,
                        'spacingRight':15,
                        # 'marginTop':10,
                        # 'marginLeft':120,
                        # 'marginBottom':10,
                        # 'marginRight':5,  
                        'animation':{
                            'duration': 0
                        }
                    },
                    'credits' : { 'enabled': False },
                    'exporting' : { 'enabled': False },
                    'title': {
                        'text' : '',
                    },
                    'xAxis': {
                        'categories':xAxis,
                        'tickLength': 0,
                        'lineWidth': 0.05,
                        'minPadding':1.5,
                        'type': 'datetime',
                        'labels': {
                            # 'formatter': function(){
                            #     var s = this.value.substring(11);
                            #     return s;
                            # },
                            'rotation': 45,
                            'align': 'left',
                            'overflow': 'justify',
                            'style': {
                                'color': '#000000'
                            }
                        },
                        'title': {
                            'text': ''
                        }
                    },
                    'yAxis': [{
                        'lineWidth': 0.5,
                        'gridLineWidth': 0.5,
                        'gridLineDashStyle':"Dot",
                        'gridLineColor':'#808080',
                        'reversedStacks': False,
                        'opposite':False,
                        'labels': {
                            'enabled': True,
                            'overflow': 'justify',
                            'style': {
                                'color': '#000000'
                            }
                        },
                        'title': {
                            'text': ''
                        },
                        'startOnTick': True
                    },{
                        'lineWidth': 0.5,
                        'gridLineWidth': 0.5,
                        'gridLineDashStyle':"Dot",
                        'opposite':True,
                        'gridLineColor':'#808080',
                        'reversedStacks': False,
                        'labels': {
                            'enabled': True,
                            'overflow': 'justify',
                            'style': {
                                'color': '#000000'
                            }
                        },
                        'title': {
                            'text': ''
                        },
                        'startOnTick': True
                    }],
                    'plotOptions': {
                        'series': {
                            'animation': False,
                            'turboThreshold': 3000
                        },
                        'line' : {
                            'allowPointSelect': False,
                            'dataLabels' : {
                                'enabled' : False
                            },
                            'marker':{
                                'enabled':False
                            }
                        }
                    },
                    'tooltip': {
                        'valueSuffix': '%'
                    },
                }

                linechart.set_dict_options(lineoptions)
                for ln in chartResult:
                    linechart.add_data_set(ln["data"], series_type=ln["type"], name=ln["name"], color=ln["color"])
                linechart.save_file(FILE_PATH + chartObj["id"])
                html_list.append({"id": chartObj["id"], "type":"line"})

                production[prop]["line_column_chart"] = chartObj

                packets[prop].setdefault("TotalAcceptedPacks", max(target_dict["TotalAcceptedPacks"]))
                packets[prop].setdefault("TotalRejectedPacks", max(target_dict["TotalRejectedPacks"]))
                packets[prop].setdefault("TotalJointPacks", max(target_dict["TotalJointPacks"]))
                packets[prop].setdefault("TotalLSL", max(target_dict["TotalLSL"]))
                packets[prop].setdefault("TotalUSL", max(target_dict["TotalUSL"]))

                elib.dictIncrement(all_props, "Packets", "TotalAcceptedPacks", max(target_dict["TotalAcceptedPacks"]))
                elib.dictIncrement(all_props, "Packets", "TotalRejectedPacks", max(target_dict["TotalRejectedPacks"]))
                elib.dictIncrement(all_props, "Packets", "TotalJointPacks", max(target_dict["TotalJointPacks"]))
                elib.dictIncrement(all_props, "Packets", "TotalLSL", max(target_dict["TotalLSL"]))
                elib.dictIncrement(all_props, "Packets", "TotalUSL", max(target_dict["TotalUSL"]))

                for xtime in sorted(pack_line_data.keys()):
                    pack_line_series.setdefault(xtime, {})
                    for key in pack_line_data[xtime]:
                        avg = sum(pack_line_data[xtime][key]) / len(pack_line_data[xtime][key])
                        pack_line_series[xtime].setdefault(key, elib.rnd(avg,2))
                        elib.dictIncrement(all_pack_line_series, xtime, key, elib.rnd(avg,2))
                        if key == "TotalAcceptedPacks":
                            if avg > max_eff:
                                max_eff = elib.rnd(avg,2)
                                max_eff_time = xtime
                            if avg < min_eff:
                                min_eff = elib.rnd(avg,2)
                                min_eff_time = xtime

                pack_series_keys = sorted(pack_line_series.keys())
                packxAxis = []
                for xtime in sorted(pack_line_series.keys()):
                    xtm = xtime[11:]
                    for leg in packing_legends:
                        pack_line_result[leg]["data"].append({
                            "category": xtime,
                            "y": elib.rnd(pack_line_series[xtime][leg],2)
                        })
                    packxAxis.append(xtm)

                packChartResult = []
                isData = False
                for leg in packing_legends:
                    if packing_legends[leg]["type"] == "column":
                        packChartResult.insert(0,pack_line_result[leg])
                    else:
                        packChartResult.append(pack_line_result[leg])

                packChartObj = {}
                packChartObj["categories"] = packxAxis
                packChartObj['charttype'] = 'linechart'
                packChartObj['id'] = 'line_packet_'+prop.lower().replace(' ', '_')
                packChartObj['series'] = packChartResult
                packChartObj['isData'] = isData

                packets[prop]["line_column_chart"] = packChartObj

                packlinechart = Highchart()
                packlineoptions = {
                    'chart': {
                        'type': 'line',
                        'height': 250,
                        'width': 1050,
                        'spacingTop':10,
                        'spacingLeft':5,
                        'spacingBottom':10,
                        'spacingRight':15,
                        # 'marginTop':10,
                        # 'marginLeft':120,
                        # 'marginBottom':10,
                        # 'marginRight':5,  
                        'animation':{
                            'duration': 0
                        }
                    },
                    'credits' : { 'enabled': False },
                    'exporting' : { 'enabled': False },
                    'title': {
                        'text' : '',
                    },
                    'xAxis': {
                        'categories':packxAxis,
                        'tickLength': 0,
                        'lineWidth': 0.05,
                        'minPadding':1.5,
                        'type': 'datetime',
                        'labels': {
                            # 'formatter': function(){
                            #     var s = this.value.substring(11);
                            #     return s;
                            # },
                            'rotation': 45,
                            'align': 'left',
                            'overflow': 'justify',
                            'style': {
                                'color': '#000000'
                            }
                        },
                        'title': {
                            'text': ''
                        }
                    },
                    'yAxis': [{
                        'lineWidth': 0.5,
                        'gridLineWidth': 0.5,
                        'gridLineDashStyle':"Dot",
                        'gridLineColor':'#808080',
                        'reversedStacks': False,
                        'opposite':False,
                        'labels': {
                            'enabled': True,
                            'overflow': 'justify',
                            'style': {
                                'color': '#000000'
                            }
                        },
                        'title': {
                            'text': ''
                        },
                        'startOnTick': True
                    },{
                        'lineWidth': 0.5,
                        'gridLineWidth': 0.5,
                        'gridLineDashStyle':"Dot",
                        'opposite':True,
                        'gridLineColor':'#808080',
                        'reversedStacks': False,
                        'labels': {
                            'enabled': True,
                            'overflow': 'justify',
                            'style': {
                                'color': '#000000'
                            }
                        },
                        'title': {
                            'text': ''
                        },
                        'startOnTick': True
                    }],
                    'plotOptions': {
                        'series': {
                            'animation': False,
                            'turboThreshold': 3000
                        },
                        'line' : {
                            'allowPointSelect': False,
                            'dataLabels' : {
                                'enabled' : False
                            },
                            'marker':{
                                'enabled':False
                            }
                        }
                    },
                    'tooltip': {
                        'valueSuffix': '%'
                    },
                }

                packlinechart.set_dict_options(packlineoptions)
                for ln in packChartResult:
                    packlinechart.add_data_set(ln["data"], series_type=ln["type"], name=ln["name"], color=ln["color"])
                packlinechart.save_file(FILE_PATH + packChartObj["id"])
                html_list.append({"id": packChartObj["id"], "type":"line"})

                if max(target_dict["TotalAcceptedPacks"]) == 0:
                    avg_ae = 1 - (max(target_dict["TotalRejectedPacks"]) / 1 )
                else:
                    avg_ae = 1 - (max(target_dict["TotalRejectedPacks"]) / max(target_dict["TotalAcceptedPacks"]))
                avg_ae = elib.rnd(avg_ae, 2)
                avg_efficiency = avg_ae * 100
                
                for xtime in sorted(pack_line_data.keys()):
                    eff_line_series.setdefault(xtime,{})
                    max_rejected = max(pack_line_data[xtime]["TotalRejectedPacks"])
                    max_accepted = max(pack_line_data[xtime]["TotalAcceptedPacks"])

                    if max_accepted in [0,1]:
                        avg_eff = (max_rejected / 100)
                        max_accepted = 1
                    else:
                        avg_eff = 1 - (max_rejected / max_accepted)
                    avg_eff = elib.rnd(avg_eff, 2) * 100

                    eff_line_series[xtime].setdefault("Efficiency", elib.rnd(avg_eff,2))
                    elib.dictIncrement(all_eff_line_series, xtime, "Efficiency", elib.rnd(avg_eff,2))


                eff_series_keys = sorted(eff_line_series.keys())
                for xtime in eff_series_keys:
                    index = eff_series_keys.index(xtime)
                    if index > 0:
                        firstVal = eff_line_series[eff_series_keys[index-1]]["Efficiency"]
                        secondVal = eff_line_series[xtime]["Efficiency"]
                        avg = (firstVal + secondVal) / 2
                        eff_line_series[xtime].setdefault("MovingAverage", elib.rnd(avg,2))
                    else:
                        eff_line_series[xtime].setdefault("MovingAverage", None)

                effxAxis = []
                for xtime in sorted(eff_line_series.keys()):
                    xtm = xtime[11:]
                    for leg in eff_legends_format:
                        eff_line_result[leg]["data"].append({
                            "category": xtime,
                            "y": elib.rnd(eff_line_series[xtime][leg],2)
                        })
                    effxAxis.append(xtm)
                effchartResult = []
                isData = False
                for leg in eff_legends_format:
                    if len(eff_line_result[leg]['data']) > 0:
                        isData = True
                    effchartResult.append(eff_line_result[leg])

                effchartObj = {}
                effchartObj["categories"] = list(set(effxAxis))
                effchartObj['charttype'] = 'linechart'
                effchartObj['id'] = 'line_efficiency_'+prop.lower().replace(' ', '_')
                effchartObj['series'] = effchartResult
                effchartObj['isData'] = isData

                efflinechart = Highchart()
                efflineoptions = {
                    'chart': {
                        'type': 'line',
                        'height': 250,
                        'width': 900,
                        'spacingTop':10,
                        'spacingLeft':5,
                        'spacingBottom':10,
                        'spacingRight':15,
                        # 'marginTop':10,
                        # 'marginLeft':120,
                        # 'marginBottom':10,
                        # 'marginRight':5,  
                        'animation':{
                            'duration': 0
                        }
                    },
                    'credits' : { 'enabled': False },
                    'exporting' : { 'enabled': False },
                    'title': {
                        'text' : '',
                    },
                    'xAxis': {
                        'categories':effxAxis,
                        'tickLength': 0,
                        'lineWidth': 0.05,
                        'minPadding':1.5,
                        'type': 'datetime',
                        'labels': {
                            # 'formatter': function(){
                            #     var s = this.value.substring(11);
                            #     return s;
                            # },
                            'rotation': 45,
                            'align': 'left',
                            'overflow': 'justify',
                            'style': {
                                'color': '#000000'
                            }
                        },
                        'title': {
                            'text': ''
                        }
                    },
                    'yAxis': [{
                        'lineWidth': 0.5,
                        'gridLineWidth': 0.5,
                        'gridLineDashStyle':"Dot",
                        'gridLineColor':'#808080',
                        'reversedStacks': False,
                        'opposite':False,
                        'labels': {
                            'enabled': True,
                            'overflow': 'justify',
                            'style': {
                                'color': '#000000'
                            }
                        },
                        'title': {
                            'text': ''
                        },
                        'startOnTick': True
                    },{
                        'lineWidth': 0.5,
                        'gridLineWidth': 0.5,
                        'gridLineDashStyle':"Dot",
                        'opposite':True,
                        'gridLineColor':'#808080',
                        'reversedStacks': False,
                        'labels': {
                            'enabled': True,
                            'overflow': 'justify',
                            'style': {
                                'color': '#000000'
                            }
                        },
                        'title': {
                            'text': ''
                        },
                        'startOnTick': True
                    }],
                    'plotOptions': {
                        'series': {
                            'animation': False,
                            'turboThreshold': 3000
                        },
                        'line' : {
                            'allowPointSelect': False,
                            'dataLabels' : {
                                'enabled' : False
                            },
                            'marker':{
                                'enabled':False
                            }
                        }
                    },
                    'tooltip': {
                        'valueSuffix': '%'
                    },
                }

                efflinechart.set_dict_options(efflineoptions)
                for ln in effchartResult:
                    efflinechart.add_data_set(ln["data"], series_type=ln["type"], name=ln["name"], color=ln["color"])
                efflinechart.save_file(FILE_PATH + effchartObj["id"])
                html_list.append({"id": effchartObj["id"], "type":"line"})


                efficiency[prop]["line_column_chart"] = effchartObj
                efficiency_donut_series = []
                efficiency_donut_series.append({
                    'color': "#F08619",
                    'name' : 'Average Efficiency',
                    'y': avg_efficiency
                })

                efficiency_donut_series.append({
                    'color': "#ffea6f",
                    'name' : 'Missed',
                    'y': 100 - avg_efficiency
                })

                percentage = str(avg_efficiency)+ '%'
                donutChartObj = {}
                donutChartObj['id'] = 'pie_'+prop.lower().replace(' ', '_')
                donutChartObj["title"] = percentage
                donutChartObj['series'] = [{'data':efficiency_donut_series, 'name':'Efficiency '}]

                chart = Highchart()
                options = {
                    'chart': {
                        'type': 'pie',
                        'height': 250,
                        'width': 250,
                        'spacingTop':5,
                        'spacingLeft':0,
                        'spacingBottom':5,
                        'spacingRight':0,
                        'animation':{
                            'duration': 0
                        }
                    },
                    'credits' : { 'enabled': False },
                    'exporting' : { 'enabled': False },
                    'title': {
                        'useHTML': True,
                        'text' : '<div class="text-reading text-center" style="font-weight:normal;font-family:Roboto,Helvetica Neue,Helvetica">Alerts <div class="text-center" style="padding-left:7px;font-weight:bold;color:#7f7f7f;">'+str(percentage)+'</div></div>',
                        'align' : 'center',
                        'verticalAlign' : 'middle',
                        'y' : -10
                    },
                    'yAxis': {
                        
                    },
                    'plotOptions': {
                        'pie': {
                            'shadow': False,
                            'center': ['50%', '50%'],
                            'dataLabels' : {
                                'enabled' : False
                            },
                        },
                        'series': {
                            'animation': False,
                            'states' : {
                                'hover' : {
                                    'halo' : {
                                        'size' : 2,
                                    },
                                    'lineWidth' : 1
                                }
                            }
                        }
                    },
                    'tooltip': {
                        'valueSuffix': '%'
                    },
                }
                chart.set_dict_options(options)
                chart.add_data_set(efficiency_donut_series, series_type='pie', name=donutChartObj["id"], size=220, innerSize=195)
                chart.save_file(FILE_PATH + donutChartObj["id"])
                html_list.append({"id": donutChartObj["id"], "type":"pie"})

                efficiency[prop]["pie_chart"] = donutChartObj
                efficiency[prop].setdefault("AverageEfficiency", avg_efficiency)
                efficiency[prop].setdefault("MaxEff", max_eff)
                efficiency[prop].setdefault("MaxEffTime", max_eff_time)
                efficiency[prop].setdefault("MinEff", min_eff)
                efficiency[prop].setdefault("MinEffTime", min_eff_time)
                efficiency[prop].setdefault("Stoppages", max(target_dict["Stoppages"]))
                efficiency[prop].setdefault("StoppageDuration", max(target_dict["StoppageDuration"]))

                elib.dictIncrement(all_props, "Efficiency", "AverageEfficiency", avg_ae)
                elib.dictIncrement(all_props, "Efficiency", "MaxEff", [{"val": elib.rnd(max_eff,2), "date":max_eff_time}])
                elib.dictIncrement(all_props, "Efficiency", "MinEff", [{"val": elib.rnd(min_eff,2), "date":min_eff_time}])
                elib.dictIncrement(all_props, "Efficiency", "Stoppages", max(target_dict["Stoppages"]))
                elib.dictIncrement(all_props, "Efficiency", "StoppageDuration", max(target_dict["StoppageDuration"]))


                for xtime in sorted(pr_line_data.keys()):
                    pr_line_series.setdefault(xtime, {})
                    for key in pr_line_data[xtime]:
                        avg = sum(pr_line_data[xtime][key]) / len(pr_line_data[xtime][key])
                        pr_line_series[xtime].setdefault(key, elib.rnd(avg,2))
                        elib.dictIncrement(all_pr_line_series, xtime, key, elib.rnd(avg,2))
                        if key == "PackingAverageRate":
                            if avg > max_pack:
                                max_pack = elib.rnd(avg,2)
                                maxTime = xtime
                            if avg < min_pack:
                                min_pack = elib.rnd(avg,2)
                                minTime = xtime

                pr_series_keys = sorted(pr_line_series.keys())
                prxAxis = []
                for xtime in sorted(pr_line_series.keys()):
                    xtm = xtime[11:]
                    for leg in packing_rate_legends:
                        pr_line_result[leg]["data"].append({
                            "category": xtime,
                            "y": elib.rnd(pr_line_series[xtime][leg],2)
                        })
                    prxAxis.append(xtm)

                prChartResult = []
                isData = False
                for leg in packing_rate_legends:
                    prChartResult.append(pr_line_result[leg])

                prChartObj = {}
                prChartObj["categories"] = list(set(prxAxis))
                prChartObj['charttype'] = 'linechart'
                prChartObj['id'] = 'line_packet_rate_'+prop.lower().replace(' ', '_')
                prChartObj['series'] = prChartResult
                prChartObj['isData'] = isData

                prlinechart = Highchart()
                prlineoptions = {
                    'chart': {
                        'type': 'line',
                        'height': 250,
                        'width': 1850,
                        'spacingTop':10,
                        'spacingLeft':5,
                        'spacingBottom':10,
                        'spacingRight':15,
                        # 'marginTop':10,
                        # 'marginLeft':120,
                        # 'marginBottom':10,
                        # 'marginRight':5,  
                        'animation':{
                            'duration': 0
                        }
                    },
                    'credits' : { 'enabled': False },
                    'exporting' : { 'enabled': False },
                    'title': {
                        'text' : '',
                    },
                    'xAxis': {
                        'categories':prxAxis,
                        'tickLength': 0,
                        'lineWidth': 0.05,
                        'minPadding':1.5,
                        'type': 'datetime',
                        'labels': {
                            # 'formatter': function(){
                            #     var s = this.value.substring(11);
                            #     return s;
                            # },
                            'rotation': 45,
                            'align': 'left',
                            'overflow': 'justify',
                            'style': {
                                'color': '#000000'
                            }
                        },
                        'title': {
                            'text': ''
                        }
                    },
                    'yAxis': [{
                        'lineWidth': 0.5,
                        'gridLineWidth': 0.5,
                        'gridLineDashStyle':"Dot",
                        'gridLineColor':'#808080',
                        'reversedStacks': False,
                        'opposite':False,
                        'labels': {
                            'enabled': True,
                            'overflow': 'justify',
                            'style': {
                                'color': '#000000'
                            }
                        },
                        'title': {
                            'text': ''
                        },
                        'startOnTick': True
                    },{
                        'lineWidth': 0.5,
                        'gridLineWidth': 0.5,
                        'gridLineDashStyle':"Dot",
                        'opposite':True,
                        'gridLineColor':'#808080',
                        'reversedStacks': False,
                        'labels': {
                            'enabled': True,
                            'overflow': 'justify',
                            'style': {
                                'color': '#000000'
                            }
                        },
                        'title': {
                            'text': ''
                        },
                        'startOnTick': True
                    }],
                    'plotOptions': {
                        'series': {
                            'animation': False,
                            'turboThreshold': 3000
                        },
                        'line' : {
                            'allowPointSelect': False,
                            'dataLabels' : {
                                'enabled' : False
                            },
                            'marker':{
                                'enabled':False
                            }
                        }
                    },
                    'tooltip': {
                        'valueSuffix': '%'
                    },
                }

                prlinechart.set_dict_options(prlineoptions)
                for ln in prChartResult:
                    prlinechart.add_data_set(ln["data"], series_type=ln["type"], name=ln["name"], color=ln["color"])
                prlinechart.save_file(FILE_PATH + prChartObj["id"])
                html_list.append({"id": prChartObj["id"], "type":"line"})

                packing_rate[prop]["line_column_chart"] = prChartObj

                production[prop].setdefault("MaxTotWeightAcceptedPacks", max(elib.rnd(target_dict["TotWeightAcceptedPacks"], 2)))
                avg = sum(target_dict["PackingAverageRate"]) / len(target_dict["PackingAverageRate"])
                production[prop].setdefault("AveragePackingRate", elib.rnd(avg,2))
                production[prop].setdefault("MaxValue", elib.rnd(max_pack,2))
                production[prop].setdefault("MaxTime", maxTime)
                production[prop].setdefault("MinValue", elib.rnd(min_pack,2))
                production[prop].setdefault("MinTime", minTime)

                elib.dictIncrement(all_props, "Production", "MaxTotWeightAcceptedPacks", max(elib.rnd(target_dict["TotWeightAcceptedPacks"], 2)))
                elib.dictIncrement(all_props, "Production", "AveragePackingRate", elib.rnd(avg,2))
                elib.dictIncrement(all_props, "Production", "MaxValue", [{"val": elib.rnd(max_pack,2), "date":maxTime}])
                elib.dictIncrement(all_props, "Production", "MinValue", [{"val": elib.rnd(min_pack,2), "date":minTime}])


                out_result.append({"prop": prop, "production": production[prop], "packets": packets[prop], "efficiency":efficiency[prop], "packing_rate": packing_rate[prop]})
        
            for leg in legends_format:
                all_line_result[leg] = {
                    'name': legends_format[leg]['name'],
                    'data': [],
                    'yAxis': legends_format[leg]['y'],
                    'type': legends_format[leg]['type'],
                    'color': legends_format[leg]['color'],
                    'visible': legends_format[leg]['visible']
                }
            for leg in packing_legends:
                all_pack_line_result[leg] = {
                    'name': packing_legends[leg]['name'],
                    'data': [],
                    'yAxis': packing_legends[leg]['y'],
                    'type': packing_legends[leg]['type'],
                    'color': packing_legends[leg]['color'],
                    'visible': packing_legends[leg]['visible']
                }
            for leg in eff_legends_format:
                all_eff_line_result[leg] = {
                    'name': eff_legends_format[leg]['name'],
                    'data': [],
                    'yAxis': eff_legends_format[leg]['y'],
                    'type': eff_legends_format[leg]['type'],
                    'color': eff_legends_format[leg]['color'],
                    'visible': eff_legends_format[leg]['visible']
                }
            for leg in packing_rate_legends:
                all_pr_line_result[leg] = {
                    'name': packing_rate_legends[leg]['name'],
                    'data': [],
                    'yAxis': packing_rate_legends[leg]['y'],
                    'type': packing_rate_legends[leg]['type'],
                    'color': packing_rate_legends[leg]['color'],
                    'visible': packing_rate_legends[leg]['visible']
                }

            maxValue = max(all_props["Production"]["MaxValue"], key=lambda x:x["val"])
            minValue = min(all_props["Production"]["MinValue"], key=lambda x:x["val"])
            elib.addToDict2(all_props, "Production", "MaxValue", maxValue["val"])
            elib.addToDict2(all_props, "Production", "MaxTime", maxValue["date"])

            elib.addToDict2(all_props, "Production", "MinValue", minValue["val"])
            elib.addToDict2(all_props, "Production", "MinTime", minValue["date"])

            maxEffValue = max(all_props["Efficiency"]["MaxEff"], key=lambda x:x["val"])
            minEffValue = min(all_props["Efficiency"]["MinEff"], key=lambda x:x["val"])
            elib.addToDict2(all_props, "Efficiency", "MaxEff", maxEffValue["val"])
            elib.addToDict2(all_props, "Efficiency", "MaxEffTime", maxEffValue["date"])

            elib.addToDict2(all_props, "Efficiency", "MinEff", minEffValue["val"])
            elib.addToDict2(all_props, "Efficiency", "MinEffTime", minEffValue["date"])

            series_keys = sorted(all_line_series.keys())
            for xtime in series_keys:
                index = series_keys.index(xtime)
                if index > 0:
                    firstVal = all_line_series[series_keys[index-1]]["TotWeightAcceptedPacks"]
                    secondVal = all_line_series[xtime]["TotWeightAcceptedPacks"]
                    avg = (firstVal + secondVal) / 2
                    all_line_series[xtime].setdefault("MovingAverage", elib.rnd(avg,2))
                else:
                    all_line_series[xtime].setdefault("MovingAverage", None)
            xAxis = []
            for xtime in sorted(all_line_series.keys()):
                xtm = xtime[11:]
                for leg in legends_format:
                    all_line_result[leg]["data"].append({
                        "category": xtm,
                        "y": elib.rnd(all_line_series[xtime][leg],2)
                    })
                xAxis.append(xtm)
            chartResult = []

            isData = False
            for leg in legends_format:
                if len(all_line_result[leg]['data']) > 0:
                    isData = True
                chartResult.append(all_line_result[leg])

            chartObj = {}
            chartObj["categories"] = list(set(xAxis))
            chartObj['charttype'] = 'linechart'
            chartObj['id'] = 'line_packing'
            chartObj['series'] = chartResult
            chartObj['isData'] = isData

            linechart = Highchart()
            lineoptions = {
                'chart': {
                    'type': 'line',
                    'height': 250,
                    'width': 1050,
                    'spacingTop':10,
                    'spacingLeft':5,
                    'spacingBottom':10,
                    'spacingRight':15,
                    # 'marginTop':10,
                    # 'marginLeft':120,
                    # 'marginBottom':10,
                    # 'marginRight':5,  
                    'animation':{
                        'duration': 0
                    }
                },
                'credits' : { 'enabled': False },
                'exporting' : { 'enabled': False },
                'title': {
                    'text' : '',
                },
                'xAxis': {
                    'categories':xAxis,
                    'tickLength': 0,
                    'lineWidth': 0.05,
                    'minPadding':1.5,
                    'type': 'datetime',
                    'labels': {
                        # 'formatter': function(){
                        #     var s = this.value.substring(11);
                        #     return s;
                        # },
                        'rotation': 45,
                        'align': 'left',
                        'overflow': 'justify',
                        'style': {
                            'color': '#000000'
                        }
                    },
                    'title': {
                        'text': ''
                    }
                },
                'yAxis': [{
                    'lineWidth': 0.5,
                    'gridLineWidth': 0.5,
                    'gridLineDashStyle':"Dot",
                    'gridLineColor':'#808080',
                    'reversedStacks': False,
                    'opposite':False,
                    'labels': {
                        'enabled': True,
                        'overflow': 'justify',
                        'style': {
                            'color': '#000000'
                        }
                    },
                    'title': {
                        'text': ''
                    },
                    'startOnTick': True
                },{
                    'lineWidth': 0.5,
                    'gridLineWidth': 0.5,
                    'gridLineDashStyle':"Dot",
                    'opposite':True,
                    'gridLineColor':'#808080',
                    'reversedStacks': False,
                    'labels': {
                        'enabled': True,
                        'overflow': 'justify',
                        'style': {
                            'color': '#000000'
                        }
                    },
                    'title': {
                        'text': ''
                    },
                    'startOnTick': True
                }],
                'plotOptions': {
                    'series': {
                        'animation': False,
                        'turboThreshold': 3000
                    },
                    'line' : {
                        'allowPointSelect': False,
                        'dataLabels' : {
                            'enabled' : False
                        },
                        'marker':{
                            'enabled':False
                        }
                    }
                },
                'tooltip': {
                    'valueSuffix': '%'
                },
            }

            linechart.set_dict_options(lineoptions)
            for ln in chartResult:
                linechart.add_data_set(ln["data"], series_type=ln["type"], name=ln["name"], color=ln["color"])
            linechart.save_file(FILE_PATH + chartObj["id"])
            html_list.append({"id": chartObj["id"], "type":"line"})

            all_props["Production"].setdefault("line_column_chart",chartObj)

            all_pack_series_keys = sorted(all_pack_line_series.keys())
            xpackAxis = []
            for xtime in sorted(all_pack_line_series.keys()):
                xtm = xtime[11:]
                for leg in packing_legends:
                    all_pack_line_result[leg]["data"].append({
                        "category": xtm,
                        "y": elib.rnd(all_pack_line_series[xtime][leg],2)
                    })
                xpackAxis.append(xtm)

            all_packChartResult = []
            isData = False
            for leg in packing_legends:
                if packing_legends[leg]["type"] == "column":
                    all_packChartResult.insert(0, all_pack_line_result[leg])
                else:
                    all_packChartResult.append(all_pack_line_result[leg])

            packChartObj = {}
            packChartObj["categories"] = list(set(xpackAxis))
            packChartObj['charttype'] = 'linechart'
            packChartObj['id'] = 'line_packet_packing'
            packChartObj['series'] = all_packChartResult
            packChartObj['isData'] = isData

            # packxAxis = sorted(all_pack_series_keys.keys())

            packlinechart = Highchart()
            packlineoptions = {
                'chart': {
                    'type': 'line',
                    'height': 250,
                    'width': 1050,
                    'spacingTop':10,
                    'spacingLeft':5,
                    'spacingBottom':10,
                    'spacingRight':15,
                    # 'marginTop':10,
                    # 'marginLeft':120,
                    # 'marginBottom':10,
                    # 'marginRight':5,  
                    'animation':{
                        'duration': 0
                    }
                },
                'credits' : { 'enabled': False },
                'exporting' : { 'enabled': False },
                'title': {
                    'text' : '',
                },
                'xAxis': {
                    'categories':xpackAxis,
                    'tickLength': 0,
                    'lineWidth': 0.05,
                    'minPadding':1.5,
                    'type': 'datetime',
                    'labels': {
                        # 'formatter': function(){
                        #     var s = this.value.substring(11);
                        #     return s;
                        # },
                        'rotation': 45,
                        'align': 'left',
                        'overflow': 'justify',
                        'style': {
                            'color': '#000000'
                        }
                    },
                    'title': {
                        'text': ''
                    }
                },
                'yAxis': [{
                    'lineWidth': 0.5,
                    'gridLineWidth': 0.5,
                    'gridLineDashStyle':"Dot",
                    'gridLineColor':'#808080',
                    'reversedStacks': False,
                    'opposite':False,
                    'labels': {
                        'enabled': True,
                        'overflow': 'justify',
                        'style': {
                            'color': '#000000'
                        }
                    },
                    'title': {
                        'text': ''
                    },
                    'startOnTick': True
                },{
                    'lineWidth': 0.5,
                    'gridLineWidth': 0.5,
                    'gridLineDashStyle':"Dot",
                    'opposite':True,
                    'gridLineColor':'#808080',
                    'reversedStacks': False,
                    'labels': {
                        'enabled': True,
                        'overflow': 'justify',
                        'style': {
                            'color': '#000000'
                        }
                    },
                    'title': {
                        'text': ''
                    },
                    'startOnTick': True
                }],
                'plotOptions': {
                    'series': {
                        'animation': False,
                        'turboThreshold': 3000
                    },
                    'line' : {
                        'allowPointSelect': False,
                        'dataLabels' : {
                            'enabled' : False
                        },
                        'marker':{
                            'enabled':False
                        }
                    }
                },
                'tooltip': {
                    'valueSuffix': '%'
                },
            }

            packlinechart.set_dict_options(packlineoptions)
            for ln in all_packChartResult:
                packlinechart.add_data_set(ln["data"], series_type=ln["type"], name=ln["name"], color=ln["color"])
            packlinechart.save_file(FILE_PATH + packChartObj["id"])
            html_list.append({"id": packChartObj["id"], "type":"line"})

            all_props["Packets"].setdefault("line_column_chart", packChartObj)

            eff_series_keys = sorted(all_eff_line_series.keys())
            for xtime in eff_series_keys:
                index = eff_series_keys.index(xtime)
                if index > 0:
                    firstVal = all_eff_line_series[eff_series_keys[index-1]]["Efficiency"]
                    secondVal = all_eff_line_series[xtime]["Efficiency"]
                    avg = (firstVal + secondVal) / 2
                    all_eff_line_series[xtime].setdefault("MovingAverage", elib.rnd(avg,2))
                else:
                    all_eff_line_series[xtime].setdefault("MovingAverage", None)

            effxAxis = []
            for xtime in sorted(all_eff_line_series.keys()):
                xtm = xtime[11:]
                for leg in eff_legends_format:
                    all_eff_line_result[leg]["data"].append({
                        "category": xtm,
                        "y": elib.rnd(all_eff_line_series[xtime][leg],2)
                    })
                effxAxis.append(xtm)
            effchartResult = []
            isData = False
            for leg in eff_legends_format:
                if len(all_eff_line_result[leg]['data']) > 0:
                    isData = True
                effchartResult.append(all_eff_line_result[leg])

            effchartObj = {}
            effchartObj["categories"] = list(set(effxAxis))
            effchartObj['charttype'] = 'linechart'
            effchartObj['id'] = 'line_efficiency_packing'
            effchartObj['series'] = effchartResult
            effchartObj['isData'] = isData

            efflinechart = Highchart()
            efflineoptions = {
                'chart': {
                    'type': 'line',
                    'height': 250,
                    'width': 900,
                    'spacingTop':10,
                    'spacingLeft':5,
                    'spacingBottom':10,
                    'spacingRight':15,
                    # 'marginTop':10,
                    # 'marginLeft':120,
                    # 'marginBottom':10,
                    # 'marginRight':5,  
                    'animation':{
                        'duration': 0
                    }
                },
                'credits' : { 'enabled': False },
                'exporting' : { 'enabled': False },
                'title': {
                    'text' : '',
                },
                'xAxis': {
                    'categories':effxAxis,
                    'tickLength': 0,
                    'lineWidth': 0.05,
                    'minPadding':1.5,
                    'type': 'datetime',
                    'labels': {
                        # 'formatter': function(){
                        #     var s = this.value.substring(11);
                        #     return s;
                        # },
                        'rotation': 45,
                        'align': 'left',
                        'overflow': 'justify',
                        'style': {
                            'color': '#000000'
                        }
                    },
                    'title': {
                        'text': ''
                    }
                },
                'yAxis': [{
                    'lineWidth': 0.5,
                    'gridLineWidth': 0.5,
                    'gridLineDashStyle':"Dot",
                    'gridLineColor':'#808080',
                    'reversedStacks': False,
                    'opposite':False,
                    'labels': {
                        'enabled': True,
                        'overflow': 'justify',
                        'style': {
                            'color': '#000000'
                        }
                    },
                    'title': {
                        'text': ''
                    },
                    'startOnTick': True
                },{
                    'lineWidth': 0.5,
                    'gridLineWidth': 0.5,
                    'gridLineDashStyle':"Dot",
                    'opposite':True,
                    'gridLineColor':'#808080',
                    'reversedStacks': False,
                    'labels': {
                        'enabled': True,
                        'overflow': 'justify',
                        'style': {
                            'color': '#000000'
                        }
                    },
                    'title': {
                        'text': ''
                    },
                    'startOnTick': True
                }],
                'plotOptions': {
                    'series': {
                        'animation': False,
                        'turboThreshold': 3000
                    },
                    'line' : {
                        'allowPointSelect': False,
                        'dataLabels' : {
                            'enabled' : False
                        },
                        'marker':{
                            'enabled':False
                        }
                    }
                },
                'tooltip': {
                    'valueSuffix': '%'
                },
            }

            efflinechart.set_dict_options(efflineoptions)
            for ln in effchartResult:
                efflinechart.add_data_set(ln["data"], series_type=ln["type"], name=ln["name"], color=ln["color"])
            efflinechart.save_file(FILE_PATH + effchartObj["id"])
            html_list.append({"id": effchartObj["id"], "type":"line"})

            all_props["Efficiency"].setdefault("line_column_chart", effchartObj)
            avg_ae = (all_props["Efficiency"]["AverageEfficiency"]/5) * 100
            all_props["Efficiency"]["AverageEfficiency"] = avg_ae
            efficiency_donut_series = []
            efficiency_donut_series.append({
                'color': "#F08619",
                'name' : 'Average Efficiency',
                'y': avg_ae
            })

            efficiency_donut_series.append({
                'color': "#ffea6f",
                'name' : 'Missed',
                'y': 100 - avg_ae
            })

            percentage = str(avg_ae)+ '%'
            donutChartObj = {}
            donutChartObj['id'] = 'pie_packing'
            donutChartObj["title"] = percentage
            donutChartObj['series'] = [{'data':efficiency_donut_series, 'name':'Efficiency'}]

            chart = Highchart()
            options = {
                'chart': {
                    'type': 'pie',
                    'height': 250,
                    'width': 250,
                    'spacingTop':5,
                    'spacingLeft':0,
                    'spacingBottom':15,
                    'spacingRight':0,
                    'animation':{
                        'duration': 0
                    }
                },
                'credits' : { 'enabled': False },
                'exporting' : { 'enabled': False },
                'title': {
                    'useHTML': True,
                    'text' : '<div class="text-reading text-center" style="font-weight:normal;font-family:Roboto,Helvetica Neue,Helvetica">Alerts <div class="text-center" style="padding-left:7px;font-weight:bold;color:#7f7f7f;">'+str(percentage)+'</div></div>',
                    'align' : 'center',
                    'verticalAlign' : 'middle',
                    'y' : -10
                },
                'yAxis': {
                    
                },
                'plotOptions': {
                    'pie': {
                        'shadow': False,
                        'center': ['50%', '50%'],
                        'dataLabels' : {
                            'enabled' : False
                        },
                    },
                    'series': {
                        'animation': False,
                        'states' : {
                            'hover' : {
                                'halo' : {
                                    'size' : 2,
                                },
                                'lineWidth' : 1
                            }
                        }
                    }
                },
                'tooltip': {
                    'valueSuffix': '%'
                },
            }
            chart.set_dict_options(options)
            chart.add_data_set(efficiency_donut_series, series_type='pie', name=donutChartObj["id"], size=220, innerSize=195)
            chart.save_file(FILE_PATH + donutChartObj["id"])
            html_list.append({"id": donutChartObj["id"], "type":"pie"})

            all_props["Efficiency"].setdefault("pie_chart",donutChartObj)

            prxAxis = []
            pr_series_keys = sorted(all_pr_line_series.keys())
            for xtime in sorted(all_pr_line_series.keys()):
                xtm = xtime[11:]
                for leg in packing_rate_legends:
                    all_pr_line_result[leg]["data"].append({
                        "category": xtm,
                        "y": elib.rnd(all_pr_line_series[xtime][leg],2)
                    })
                prxAxis.append(xtm)

            prChartResult = []
            isData = False
            for leg in packing_rate_legends:
                prChartResult.append(all_pr_line_result[leg])

            prChartObj = {}
            prChartObj["categories"] = list(set(prxAxis))
            prChartObj['charttype'] = 'linechart'
            prChartObj['id'] = 'line_packet_rate_packing'
            prChartObj['series'] = prChartResult
            prChartObj['isData'] = isData

            prlinechart = Highchart()
            prlineoptions = {
                'chart': {
                    'type': 'line',
                    'height': 250,
                    'width': 1850,
                    'spacingTop':10,
                    'spacingLeft':5,
                    'spacingBottom':10,
                    'spacingRight':15,
                    # 'marginTop':10,
                    # 'marginLeft':120,
                    # 'marginBottom':10,
                    # 'marginRight':5,  
                    'animation':{
                        'duration': 0
                    }
                },
                'credits' : { 'enabled': False },
                'exporting' : { 'enabled': False },
                'title': {
                    'text' : '',
                },
                'xAxis': {
                    'categories':prxAxis,
                    'tickLength': 0,
                    'lineWidth': 0.05,
                    'minPadding':1.5,
                    'type': 'datetime',
                    'labels': {
                        # 'formatter': function(){
                        #     var s = this.value.substring(11);
                        #     return s;
                        # },
                        'rotation': 45,
                        'align': 'left',
                        'overflow': 'justify',
                        'style': {
                            'color': '#000000'
                        }
                    },
                    'title': {
                        'text': ''
                    }
                },
                'yAxis': [{
                    'lineWidth': 0.5,
                    'gridLineWidth': 0.5,
                    'gridLineDashStyle':"Dot",
                    'gridLineColor':'#808080',
                    'reversedStacks': False,
                    'opposite':False,
                    'labels': {
                        'enabled': True,
                        'overflow': 'justify',
                        'style': {
                            'color': '#000000'
                        }
                    },
                    'title': {
                        'text': ''
                    },
                    'startOnTick': True
                },{
                    'lineWidth': 0.5,
                    'gridLineWidth': 0.5,
                    'gridLineDashStyle':"Dot",
                    'opposite':True,
                    'gridLineColor':'#808080',
                    'reversedStacks': False,
                    'labels': {
                        'enabled': True,
                        'overflow': 'justify',
                        'style': {
                            'color': '#000000'
                        }
                    },
                    'title': {
                        'text': ''
                    },
                    'startOnTick': True
                }],
                'plotOptions': {
                    'series': {
                        'animation': False,
                        'turboThreshold': 3000
                    },
                    'line' : {
                        'allowPointSelect': False,
                        'dataLabels' : {
                            'enabled' : False
                        },
                        'marker':{
                            'enabled':False
                        }
                    }
                },
                'tooltip': {
                    'valueSuffix': '%'
                },
            }

            prlinechart.set_dict_options(prlineoptions)
            for ln in prChartResult:
                prlinechart.add_data_set(ln["data"], series_type=ln["type"], name=ln["name"], color=ln["color"])
            prlinechart.save_file(FILE_PATH + prChartObj["id"])
            html_list.append({"id": prChartObj["id"], "type":"line"})

            all_props["PackingRate"].setdefault("line_column_chart", prChartObj)
            # print all_props
            out_result.insert(0, {"prop": "Packing", "production": all_props["Production"], "packets": all_props["Packets"], "efficiency":all_props["Efficiency"], "packing_rate": all_props["PackingRate"]})
        
        for ht in html_list:
            self.htmltoImage(ht["id"], ht["type"])

        out_pdf= FILE_PATH + 'Packing_Dashboard_'+selectedDate+'.pdf'
        intermediate_html = FILE_PATH + 'intermediate.html'

        htmlToAdd = '<div style="margin-left:10px;margin-top:5px;text-align:center;border:1px solid white;">'\
                        '<div style="text-center:left;margin-left:1rem;margin-right:1rem;margin-top:300px;">'\
                            '<img src="' + CONFIG_PATH + 'abz2_big.png" style=""/>'\
                            '<div style="text-align:center;color:#323232;font-size:35px;margin-top:7px;">'\
                                '<span style="color:#323232;font-size:35px;margin-right:2rem;">Packing Daily Report</span>'\
                            '</div>'\
                            '<div style="text-align:center;color:#323232;font-size:35rem;margin-top:5px;">'\
                                '<span style="color:#323232;font-size:30px;"> Generation Date ('+selectedDate+') </span>'\
                            '</div>'\
                        '</div>'\
                    '</div>'

        if os.path.exists(intermediate_html):
            os.remove(intermediate_html)
        
        index = 0
        imagesToDelete = []
        ht = ""
        allreportKeys = self.reportKeys
        allreportKeys.insert(0, "Packing")

        for node in out_result:
            propname = node["prop"].lower()
            production = node["production"]
            packets = node["packets"]
            efficiency = node["efficiency"]
            packing_rate = node["packing_rate"]

            production_linename = FILE_PATH + 'line_'+propname+'.png'
            packets_linename = FILE_PATH + 'line_packet_'+propname+'.png'
            efficiency_piename = FILE_PATH + 'pie_'+propname+'.png'
            efficiency_linename = FILE_PATH + 'line_efficiency_'+propname+'.png'
            packing_rate_linename = FILE_PATH + 'line_packet_rate_'+propname+'.png'

            # if index == 0 or index % 2 == 0: 
            ht = ""
            ht += '<div class="flex flex--col flex__item>'\
                    '<div class="flex flex--col flex__item custom-holder-large" style="width:120%;">'\
                        '<div class="flex flex--col flex__item">'\
                            '<div class="flex flex--row flex--middle cnt-sub" style="height: 30px;width: 100%;">'\
                                '<div class="hdr-txt2 pointer" style="margin-left:1rem;padding-left: 1rem;padding-right:1rem;">'+node["prop"]+'</div>'\
                            '</div>'\
                            '<div class="flex flex--row flex--middle cnt-sub-3" style="height:35px; width:100%">'\
                                '<div class="hdr-txt3 pointer" style="margin-left:1rem;">Production</div>'\
                            '</div>'\
                            '<div class="flex flex--row flex__item">'\
                                '<div class="flex flex--col flex__item custom-holder-2" style="width:28%;">'\
                                    '<div class="flex flex--row flex--middle cnt-sub-2" style="height:25px; width:100%">'\
                                        '<div class="hdr-txt3 pointer" style="margin-left:1rem;padding-left: 1rem;padding-right:1rem;">Summary</div>'\
                                    '</div>'\
                                    '<div class="flex flex--row flex--center flex__item margin--all">'\
                                        '<div class="flex flex--col flex__item" style="">'\
                                            '<div class="flex flex__item flex--middle margin--left overview-header-border" style="">'\
                                                '<div class="flex__item text-left" style="margin-left:5px;">Total</div>'\
                                            '</div>'\
                                            '<div class="flex flex__item flex--middle margin--left overview-header-border">'\
                                                '<div class="flex__item text-left" style="margin-left:5px;">Average Rate</div>'\
                                            '</div>'\
                                            '<div class="flex flex__item flex--middle margin--left overview-header-border">'\
                                                '<div class="flex__item text-left" style="margin-left:5px;">Max Rate</div>'\
                                            '</div>'\
                                            '<div class="flex flex__item flex--middle margin--left overview-header-border" style="border-bottom:1px solid #e9e9e9;">' \
                                                '<div class="flex__item text-left" style="margin-left:5px;">Min Rate</div>'\
                                            '</div>'\
                                        '</div>'\
                                        '<div class="flex flex--col flex__item" style="">'\
                                            '<div class="flex flex__item flex--middle flex--right text-large overview-value-border" style="">'\
                                                '<div class="flex__item text-right" style="margin-right:2px;">'+str(production["MaxTotWeightAcceptedPacks"])+' Kg</div>'\
                                            '</div>'\
                                            '<div class="flex flex__item flex--middle flex--right text-large overview-value-border">'\
                                                '<div class="flex__item text-right" style="margin-right:2px;">'+str(production["AveragePackingRate"])+' U/Hr</div>'\
                                            '</div>'\
                                            '<div class="flex flex__item flex--middle flex--right text-large overview-value-border">'\
                                                '<div class="flex__item text-right" style="margin-right:2px;">'+str(production["MaxValue"])+' U/Hr</div>'\
                                            '</div>'\
                                            '<div class="flex flex__item flex--middle flex--right text-large overview-value-border" style="border-bottom:1px solid #e9e9e9;">' \
                                                '<div class="flex__item text-right" style="margin-right:2px;">'+str(production["MinValue"])+' U/Hr</div>'\
                                            '</div>'\
                                        '</div>'\
                                        '<div class="flex flex--col flex__item" style="">'\
                                            '<div class="flex flex__item flex--middle flex--right text-large margin--right overview-value-border">'\
                                                '<div class="flex__item text-right" style="margin-right:10px;color:white;">'+str(production["MaxTime"])+'</div>'\
                                            '</div>'\
                                            '<div class="flex flex__item flex--middle flex--right text-large margin--right overview-value-border">'\
                                                '<div class="flex__item text-right" style="margin-right:10px;color:white;">'+str(production["MinTime"])+'</div>'\
                                            '</div>'\
                                            '<div class="flex flex__item flex--middle flex--right text-large margin--right overview-value-border">'\
                                                '<div class="flex__item text-right" style="margin-right:10px;">'+str(production["MaxTime"])+'</div>'\
                                            '</div>'\
                                            '<div class="flex flex__item flex--middle flex--right text-large margin--right overview-value-border" style="border-bottom:1px solid #e9e9e9;">' \
                                                '<div class="flex__item text-right" style="margin-right:10px;">'+str(production["MinTime"])+'</div>'\
                                            '</div>'\
                                        '</div>'\
                                    '</div>'\
                                '</div>'\
                                '<div class="flex flex--col flex__item__2 custom-holder-2" style="">'\
                                    '<div class="flex flex--row flex--middle cnt-sub-2" style="height:25px; width:100%">'\
                                        '<div class="hdr-txt3 pointer" style="margin-left:1rem;padding-left: 1rem;padding-right:1rem;">Trend</div>'\
                                    '</div>'\
                                    '<div class="flex flex__item" style="margin-left:5px;">'\
                                        '<img height="250" src="'+production_linename+'"/>'\
                                    '</div>'\
                                '</div>'\
                            '</div>'\
                            '<div class="flex flex--row flex--middle cnt-sub-3" style="height:35px; width:100%">'\
                                '<div class="hdr-txt3 pointer" style="margin-left:1rem;">Packets</div>'\
                            '</div>'\
                            '<div class="flex flex--row flex__item">'\
                                '<div class="flex flex--col flex__item custom-holder-2" style="width:28%;">'\
                                    '<div class="flex flex--row flex--middle cnt-sub-2" style="height:25px; width:100%">'\
                                        '<div class="hdr-txt3 pointer" style="margin-left:1rem;padding-left: 1rem;padding-right:1rem;">Acceptance Vs Rejection Summary</div>'\
                                    '</div>'\
                                    '<div class="flex flex--row flex--center flex__item margin--all" style="margin-right:20px;">'\
                                        '<div class="flex flex--col flex__item" style="">'\
                                            '<div class="flex flex__item flex--middle margin--left overview-header-border">'\
                                                '<div class="flex__item text-left" style="margin-left:5px;">Accepted</div>'\
                                            '</div>'\
                                            '<div class="flex flex__item flex--middle margin--left overview-header-border">'\
                                                '<div class="flex__item text-left" style="margin-left:5px;">Rejected</div>'\
                                            '</div>'\
                                            '<div class="flex flex__item flex--middle margin--left overview-header-border">'\
                                                '<div class="flex__item text-left" style="margin-left:5px;">Joint Packs</div>'\
                                            '</div>'\
                                            '<div class="flex flex__item flex--middle margin--left overview-header-border">' \
                                                '<div class="flex__item text-left" style="margin-left:5px;">LSL</div>'\
                                            '</div>'\
                                            '<div class="flex flex__item flex--middle margin--left overview-header-border" style="border-bottom:1px solid #e9e9e9;">' \
                                                '<div class="flex__item text-left" style="margin-left:5px;">USL</div>'\
                                            '</div>'\
                                        '</div>'\
                                        '<div class="flex flex--col flex__item" style="">'\
                                            '<div class="flex flex__item flex--middle flex--right text-large overview-value-border">'\
                                                '<div class="flex__item text-right" style="margin-right:10px;">'+str(packets["TotalAcceptedPacks"])+'</div>'\
                                            '</div>'\
                                            '<div class="flex flex__item flex--middle flex--right text-large overview-value-border">'\
                                                '<div class="flex__item text-right" style="margin-right:10px;">'+str(packets["TotalRejectedPacks"])+'</div>'\
                                            '</div>'\
                                            '<div class="flex flex__item flex--middle flex--right text-large overview-value-border">'\
                                                '<div class="flex__item text-right" style="margin-right:10px;">'+str(packets["TotalJointPacks"])+'</div>'\
                                            '</div>'\
                                            '<div class="flex flex__item flex--middle flex--right text-large overview-value-border">' \
                                                '<div class="flex__item text-right" style="margin-right:10px;">'+str(packets["TotalLSL"])+'</div>'\
                                            '</div>'\
                                            '<div class="flex flex__item flex--middle flex--right text-large overview-value-border" style="border-bottom:1px solid #e9e9e9;">' \
                                                '<div class="flex__item text-right" style="margin-right:10px;">'+str(packets["TotalUSL"])+'</div>'\
                                            '</div>'\
                                        '</div>'\
                                    '</div>'\
                                '</div>'\
                                '<div class="flex flex--col flex__item__2 custom-holder-2" style="">'\
                                    '<div class="flex flex--row flex--middle cnt-sub-2" style="height:25px; width:100%">'\
                                        '<div class="hdr-txt3 pointer" style="margin-left:1rem;padding-left: 1rem;padding-right:1rem;">Trend</div>'\
                                    '</div>'\
                                    '<div class="flex flex__item" style="margin-left:5px;">'\
                                        '<img height="250" src="'+packets_linename+'"/>'\
                                    '</div>'\
                                '</div>'\
                            '</div>'\
                            '<div class="flex flex--row flex--middle cnt-sub-3" style="height:35px; width:100%">'\
                                '<div class="hdr-txt3 pointer" style="margin-left:1rem;">Packing Efficiency</div>'\
                            '</div>'\
                            '<div class="flex flex--row flex__item">'\
                                '<div class="flex flex--col flex__item custom-holder-2" style="width:35%;">'\
                                    '<div class="flex flex--row flex--middle cnt-sub-2" style="height:25px; width:100%">'\
                                        '<div class="hdr-txt3 pointer" style="margin-left:1rem;padding-left: 1rem;padding-right:1rem;">Efficiency</div>'\
                                    '</div>'\
                                    '<div class="flex flex--row flex--center flex__item margin--all" style="margin-right:10px;">'\
                                        '<div class="flex flex--col flex__item" style="">'\
                                            '<div class="flex flex__item flex--middle overview-header-border">'\
                                                '<div class="flex__item text-left ellipsis" style="margin-left:5px;margin-right:2px;">Average</div>'\
                                            '</div>'\
                                            '<div class="flex flex__item flex--middle  overview-header-border">'\
                                                '<div class="flex__item text-left ellipsis" style="margin-left:5px;margin-right:2px;">Max</div>'\
                                            '</div>'\
                                            '<div class="flex flex__item flex--middle overview-header-border">'\
                                                '<div class="flex__item text-left ellipsis" style="margin-left:5px;margin-right:2px;">Min</div>'\
                                            '</div>'\
                                            '<div class="flex flex__item flex--middle overview-header-border">' \
                                                '<div class="flex__item text-left ellipsis" style="margin-left:5px;margin-right:2px;">Stoppages</div>'\
                                            '</div>'\
                                            '<div class="flex flex__item flex--middle overview-header-border" style="border-bottom:1px solid #e9e9e9;">' \
                                                '<div class="flex__item text-left ellipsis" style="margin-left:5px;margin-right:2px;">Stoppage Duration</div>'\
                                            '</div>'\
                                        '</div>'\
                                        '<div class="flex flex--col flex__item" style="">'\
                                            '<div class="flex flex__item flex--middle text-medium overview-value-border">'\
                                                '<div class="flex__item text-right ellipsis" style="margin-right:2px;margin-left:2px;">'+str(efficiency["AverageEfficiency"])+'%</div>'\
                                            '</div>'\
                                            '<div class="flex flex__item flex--middle text-medium overview-value-border">'\
                                                '<div class="flex__item text-right ellipsis" style="margin-right:2px;margin-left:2px;">'+str(efficiency["MaxEff"])+'%</div>'\
                                            '</div>'\
                                            '<div class="flex flex__item flex--middle text-medium overview-value-border">'\
                                                '<div class="flex__item text-right ellipsis" style="margin-right:2px;margin-left:2px;">'+str(efficiency["MinEff"])+'%</div>'\
                                            '</div>'\
                                            '<div class="flex flex__item flex--middle text-medium overview-value-border">' \
                                                '<div class="flex__item text-right ellipsis" style="margin-right:2px;margin-left:2px;">'+str(efficiency["Stoppages"])+' Nos</div>'\
                                            '</div>'\
                                            '<div class="flex flex__item flex--middle text-medium overview-value-border" style="border-bottom:1px solid #e9e9e9;">' \
                                                '<div class="flex__item text-right ellipsis" style="margin-right:2px;margin-left:2px;">'+str(efficiency["StoppageDuration"])+' Mins</div>'\
                                            '</div>'\
                                        '</div>'\
                                        '<div class="flex flex--col flex__item" style="">'\
                                            '<div class="flex flex__item flex--middle text-medium overview-value-border">'\
                                                '<div class="flex__item text-right ellipsis" style="color:white;margin-right:2px;">'+str(efficiency["MaxEffTime"])+'</div>'\
                                            '</div>'\
                                            '<div class="flex flex__item flex--middle text-medium overview-value-border">'\
                                                '<div class="flex__item text-right ellipsis" style="margin-right:2px;">'+str(efficiency["MaxEffTime"])+'</div>'\
                                            '</div>'\
                                            '<div class="flex flex__item flex--middle text-medium overview-value-border">'\
                                                '<div class="flex__item text-right ellipsis" style="margin-right:2px;">'+str(efficiency["MinEffTime"])+'</div>'\
                                            '</div>'\
                                            '<div class="flex flex__item flex--middle text-medium overview-value-border">' \
                                                '<div class="flex__item text-right ellipsis" style="color:white;margin-right:2px;">'+str(efficiency["MaxEffTime"])+'</div>'\
                                            '</div>'\
                                            '<div class="flex flex__item flex--middle text-medium overview-value-border" style="border-bottom:1px solid #e9e9e9;">' \
                                                '<div class="flex__item text-right ellipsis" style="color:white;margin-right:2px;">'+str(efficiency["MaxEffTime"])+'</div>'\
                                            '</div>'\
                                        '</div>'\
                                    '</div>'\
                                '</div>'\
                                '<div class="flex flex--col flex__item__2 custom-holder-2" style="width:26%">'\
                                    '<div class="flex flex--row flex--middle cnt-sub-2" style="height:25px; width:100%">'\
                                        '<div class="hdr-txt3 pointer" style="margin-left:1rem;padding-left: 1rem;padding-right:1rem;">Average</div>'\
                                    '</div>'\
                                    '<div class="flex flex__item" style="margin-left:10px;">'\
                                        '<img src="'+efficiency_piename+'"/>'\
                                    '</div>'\
                                '</div>'\
                                '<div class="flex flex--col flex__item__2 custom-holder-2" style="width:70%;">'\
                                    '<div class="flex flex--row flex--middle cnt-sub-2" style="height:25px; width:100%">'\
                                        '<div class="hdr-txt3 pointer" style="margin-left:1rem;padding-left: 1rem;padding-right:1rem;">Trend</div>'\
                                    '</div>'\
                                    '<div class="flex flex__item" style="margin-left:5px;">'\
                                        '<img height="250" src="'+efficiency_linename+'"/>'\
                                    '</div>'\
                                '</div>'\
                            '</div>'\
                            '<div class="flex flex--row flex--middle cnt-sub-3" style="height:35px; width:100%">'\
                                '<div class="hdr-txt3 pointer" style="margin-left:1rem;">Packing Rate</div>'\
                            '</div>'\
                            '<div class="flex flex--row flex__item">'\
                                '<div class="flex flex--col flex__item__3 custom-holder-2" style="">'\
                                    '<div class="flex flex--row flex--middle cnt-sub-2" style="height:25px; width:100%">'\
                                        '<div class="hdr-txt3 pointer" style="margin-left:1rem;padding-left: 1rem;padding-right:1rem;">Trend</div>'\
                                    '</div>'\
                                    '<div class="flex flex__item flex--stretch" style="margin-left:5px;">'\
                                        '<img height="250" src="'+packing_rate_linename+'"/>'\
                                    '</div>'\
                                '</div>'\
                            '</div>'\
                        '</div>'\
                    '</div>'\
                '</div>'
            imagesToDelete.append(production_linename)
            imagesToDelete.append(efficiency_piename)
            imagesToDelete.append(efficiency_linename)
            imagesToDelete.append(packets_linename)
            imagesToDelete.append(packing_rate_linename) 
            self.to_html_pretty_2(ht, intermediate_html, prop, htmlToAdd, "Packing Daily Report", selectedDate)
            htmlToAdd = ""
        options = {
            "page-size": "A3",
            # "orientation": "Landscape",
            # 'dpi':400
        }
        if index == 0:
            self.to_html_pretty_2(ht, intermediate_html, "", htmlToAdd, "Packing Daily Report", selectedDate)
        # pdfkit.from_file(intermediate_html, out_pdf, configuration=config, options=options)
        pdfkit.from_file(intermediate_html, out_pdf, options=options)
        for img in imagesToDelete:
            if os.path.exists(img):
                os.remove(img)

        return out_pdf

    def to_html_pretty_2(self, ht, filename='out.html', title='', htmlToAdd="", reportTitle = '', selectedDate=''):
        htm = ''
        if htmlToAdd != "":
            htm += htmlToAdd
        if title != '':
            htm += '<h1><div class="flex flex--col flex__item flex--center">'
            htm += '<span style="text-align:left;width:20%;"> <img src="' + CONFIG_PATH + 'abz2_small.png" align:left/></span>'
            htm += '<span style="margin-left:30rem;width:60%; text-align:center;color:#323232;">'\
                        '<span style="color:#323232;font-size:22px;">'+reportTitle+'</span>'\
                    '</span>'\
                    '<span style="margin-left:18rem;width:20%;text-align:right;color:#323232;">'\
                        '<span style="color:#323232;font-size:22px;"> Generation Date ('+selectedDate+') </span>'\
                    '</span></div></h1>'
            # htm += '<h2> %s </h2>\n' % title
        htm += ht

        with open(filename, 'a') as f:
             f.write(HTML_TEMPLATE3 + htm + HTML_TEMPLATE2)

    def htmltoImage(self, ht, chartType):
        self.log.info(ht+'.html ---to--- '+ ht+'.png')
        htmlname = ht+".html"
        pngname = ht+".png"
        options = {
            'format': 'png',
            'crop-h': '530',
            'crop-w': '530',
            'crop-x': '3',
            'crop-y': '3',
            'encoding': "UTF-8",
        }
        if chartType == "line":
            options = {
                'format': 'png',
                #'crop-h': '530',
                #'crop-w': '630',
                'crop-x': '3',
                'crop-y': '3',
                'encoding': "UTF-8",
            }   

        # imgkit.from_file(FILE_PATH + htmlname, FILE_PATH + pngname, options=options, config=image_config)
        imgkit.from_file(FILE_PATH + htmlname, FILE_PATH + pngname, options=options)
        os.remove(FILE_PATH + htmlname)


if __name__ == "__main__":
    dbPManager = PRun()
    dbPManager.get_today_records("2019-04-18")
    # dbPManager.get_today_cbb_records("2018-11-01")
    dbPManager.save_packing_home("2019-04-18")
    # dbPManager.save_losses_report("2019-11-01")
