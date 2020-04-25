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
CONFIG_PATH = CONFIG_PATH.replace("stage_oven_data.pyc", "")
CONFIG_PATH = CONFIG_PATH.replace("stage_oven_data.pyo", "")
CONFIG_PATH = CONFIG_PATH.replace("stage_oven_data.py", "")
CONFIG_PATH = CONFIG_PATH + "data/"

FILE_PATH = str(os.path.realpath(__file__))
FILE_PATH = FILE_PATH.replace("stage_oven_data.pyc", "")
FILE_PATH = FILE_PATH.replace("stage_oven_data.pyo", "")
FILE_PATH = FILE_PATH.replace("stage_oven_data.py", "")
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

class ORun():
    def __init__(self):
        
        self.collection = ""
        self.properties = ""
        self.reportKeys = []
        self.reportManager = {}
        self.recipeKeys = []
        self.recipeName = {}
        self.recipeSet = {}


        self.log = getLogger()
        self.read_settings()

        self._date = "";
        self.all_dates = [];

        self.log.info('Reading Params....Oven')
        self.log.info('File Ready to Use...Oven')
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
        reader = csv.DictReader(open(CONFIG_PATH + 'stage_oven_settings.txt'), delimiter="\t")
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
            if row["Field"] == "RECIPE":
                recipeKeys = ast.literal_eval(row["Value"])
            if row["Field"] == "RECIPENAME":
                recipeName = ast.literal_eval(row["Value"])
            if row["Field"] == "RECIPESET":
                recipeSet = ast.literal_eval(row["Value"])
 
        self.readerconfig = ReaderBase()
        # self.properties = self.readerconfig.kpis(all_keys)
        self.config = self.readerconfig.toKeyJSON(all_json)
        self.collection = collection
        self.keys = keys
        self.properties = keys.split(",")
        self.reportManager = reportManager
        self.reportKeys = reportKeys
        self.recipeKeys = recipeKeys
        self.recipeName = recipeName
        self.recipeSet = recipeSet

    def read_from_db(self, dateparam = ""):
        self.log.info("Oven dateparam: %s", dateparam)
        
        _dict = {}
        target_dict = {}
        
        connection = MongoClient('127.0.0.1', username="admin", password="admin123", authSource='analyse_db', authMechanism='SCRAM-SHA-1')
        myDb = connection["analyse_db"]
        
        db = myDb[self.collection]
        # myDb = connection["analyse_db"]
        # db = myDb[self.collection]
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
            
        for propkey in self.properties:
            prop = elib.trim(propkey)
            _dict.setdefault(prop, {})
            _dict[prop].setdefault("SetPoint", [])
            _dict[prop].setdefault("Actual", [])
            _dict[prop].setdefault("Time", [])
            target_dict.setdefault(prop, {})
        moulder_rpm_actual = 0
        fbactual = 0
        fbset = 0
        fbfreq = 0
        baking_time = 0
        rpmCount = 0
        recipe_no = 1
        for row in dbresult:
            for prop in self.properties:                 
                keyprop = elib.trim(prop).lower().replace(' ', '_')
                fbtime = row[self.config["time"]]
            
                # d = datetime.strptime(x, '%d/%m/%Y %H:%M:%S')
                # fbtime = d.strftime('%Y-%m-%d %H:%M:%S')
                
                self._date = fbtime.strftime("%Y-%m-%d")
                _dict[prop].setdefault(fbtime, {})
                fbactual = row[self.config[keyprop+'_temp_actual']] if row.get(self.config[keyprop+'_temp_actual'], "--") != "--" else fbactual
                fbset = elib.tonum(row[self.config[keyprop+'_temp_sp']]) if row.get(self.config[keyprop+'_temp_sp'], "--") != "--" else fbset
                baking_time = elib.tonum(row[self.config["baking_time"]]) if row.get(self.config["baking_time"], "--") != "--" else baking_time
                recipe_no = elib.tonum(row[self.config["recipe_no"]], "int") if row.get(self.config["recipe_no"], "--") != "--" else recipe_no

                _dict[prop][fbtime]["SetPoint"] = elib.tonum(fbset)
                _dict[prop][fbtime]["Actual"] = elib.tonum(fbactual)
                _dict[prop][fbtime]["Time"] = fbtime
                _dict[prop][fbtime]["BakingTime"] = baking_time
                _dict[prop][fbtime]["RecipeValue"] = recipe_no
                _dict[prop][fbtime]["Prop"] = prop
                
        return _dict

    def get_today_records(self, dateparam = ""):
        self.log.info("Data Push Started...Oven")
        # dateparam = "2018-11-01"
        target_dict = self.read_from_db(dateparam)
        # print target_dict
        connection = MongoClient('127.0.0.1', username="admin", password="admin123", authSource='analyse_db', authMechanism='SCRAM-SHA-1')
        # connection = MongoClient('mongodb://localhost:27017/')
        myDb = connection["analyse_db"]
        self._date = dateparam
        self.log.info("Oven self._date: %s", self._date)
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
            # _to_push = {
            #     "asofdate": self._date,
            #     "identifier": "Moulder",
            #     "staging": dbData
            # }
            myDb["oven_staging"].remove({'asofdate':self._date})
            record_id = myDb["oven_staging"].insert_many(dbData)
            self.log.info('Oven %s records found', str(len(dbData)))
            self.log.info("DB Push Completed...Oven")
        else:
            self.log.info("No Data...Oven")

    def get_oven_report(self, dateparam):
        result = False
        selectedDate = dateparam
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
        _dict = {}

        find_dict = {"asofdate":selectedDate}
        
        connection = MongoClient('127.0.0.1', username="admin", password="admin123", authSource='analyse_db', authMechanism='SCRAM-SHA-1')

        myDb = connection["analyse_db"]
        # myDb = connection["analyse_db"]
        db = myDb["oven_staging"]

        item_count = db.count_documents(find_dict)
        if item_count == 0:
            self.log.info("Data not available in staging... Getting From Mains...Oven")
            self.get_today_records(selectedDate)
            find_dict = {"asofdate":selectedDate}
            item_count = db.count_documents(find_dict)
        self.log.info(item_count)
        if item_count > 0:
            dbresult = db.find(find_dict)
            for dt in dbresult:
                if dt != []:        
                    if str(dt["Prop"]) not in _dict.keys():
                        _dict.setdefault(str(dt["Prop"]), [])
                    _dict[str(dt["Prop"])].append(dt)

        
        if _dict != {}:
            line_result = {}
            downTime = {}
            for prop in self.reportKeys:
                stage_data = _dict[prop]

                line_data = {}
                line_result.setdefault(prop, {})
                for node in stage_data:
                    setpoint = elib.tonum(node["SetPoint"])
                    actual_num = elib.tonum(node["Actual"])
                    # current_num = elib.tonum(node["Frequency"])
                    baking_time = elib.tonum(node["BakingTime"])

                    xTime = node["Time"]
                    xDateTime =  xTime.strftime("%Y-%m-%d %H:%M")
                    if xDateTime in timerange:
                        if baking_time > 0:
                            elib.dictIncrement(line_data, xDateTime, "BakingTime", [baking_time])
                        else:
                            if xDateTime not in line_data.keys():
                                line_data.setdefault(xDateTime, {}).setdefault("BakingTime", [0])
                            elif "BakingTime" not in line_data[xDateTime].keys():
                                line_data[xDateTime].setdefault("BakingTime", [0])

                        if actual_num > 0:
                            elib.dictIncrement(line_data, xDateTime, "Actual", [actual_num])
                            elib.dictIncrement(line_data, xDateTime, "SetPoint", [elib.tonum(node["SetPoint"])])
                        else:
                            if xDateTime not in line_data.keys():
                                line_data.setdefault(xDateTime, {}).setdefault("Actual", [0])
                                line_data.setdefault(xDateTime, {}).setdefault("SetPoint", [0])
                            elif "Actual" not in line_data[xDateTime]:
                                line_data[xDateTime].setdefault("Actual", [0])
                                line_data[xDateTime].setdefault("SetPoint", [0])
                        # if current_num > 0:
                        #     elib.dictIncrement(line_data, xDateTime, "CurrentActual", [current_num])
                        # else:
                        #     if xDateTime not in line_data.keys():
                        #         line_data.setdefault(xDateTime, {}).setdefault("CurrentActual", [0])
                        #     elif "CurrentActual" not in line_data[xDateTime].keys():
                        #         line_data[xDateTime].setdefault("CurrentActual", [0])
                for xTime in line_data:
                    avg_baking = sum(line_data[xTime]["BakingTime"])/len(line_data[xTime]["BakingTime"])
                    avg_actual = sum(line_data[xTime]["Actual"])/len(line_data[xTime]["Actual"])
                    avg_setpoint = sum(line_data[xTime]["SetPoint"])/len(line_data[xTime]["SetPoint"])
                    # avg_current_actual = sum(line_data[xTime]["CurrentActual"])/len(line_data[xTime]["CurrentActual"])

                    line_result[prop].setdefault(xTime, {}).setdefault("BakingTime", elib.rnd(avg_baking, 0))
                    line_result[prop].setdefault(xTime, {}).setdefault("Actual", elib.rnd(avg_actual, 2))
                    line_result[prop].setdefault(xTime, {}).setdefault("SetPoint", elib.rnd(avg_setpoint, 2))
                    # line_result[prop].setdefault(xTime, {}).setdefault("Current", elib.rnd(avg_current_actual, 2))

            for xTime in timerange:
                row = {}
                for prop in self.reportKeys:
                    newProp = prop.lower().replace(' ', '_')
                    if xTime in line_result[prop].keys():
                        if "xTime" not in row.keys():
                            row.setdefault("xTime", xTime)
                        if "BakingTime" not in row.keys():
                            newbakingTime = time.strftime('%H:%M:%S', time.gmtime(line_result[prop][xTime]["BakingTime"]))
                            row.setdefault("bakingTime", newbakingTime)
                        row.setdefault(newProp+"_Actual", line_result[prop][xTime]["Actual"])
                        row.setdefault(newProp+"_SetPoint", line_result[prop][xTime]["SetPoint"])
                        # row.setdefault(newProp+"_Current", line_result[prop][xTime]["Current"])
                if row != {}:
                    out_result.append(row)

        return out_result

    def downloadOvenReport(self, out_report, dateparam):

        yesterdayDate = datetime.strptime(dateparam, '%Y-%m-%d')
        _date2460 = yesterdayDate + timedelta(minutes = (24*60))
        todayDate = _date2460.strftime('%Y-%m-%d')
        selectedDate = yesterdayDate.strftime("%Y-%m-%d")

        # todayDate = datetime.now();
        # dts_time = time.mktime(todayDate.timetuple()) * 1000

        fileCompleted = []
        all_rows = []
        data_list = []
        txtfilename = FILE_PATH + "reports_moulder.txt"
        subheaders = ["Set Temp", "Actual Temp"]
        headkeys = ["SetPoint", "Actual"]
        headers =  []
        keyheaders = ["xTime"]

        for mode in self.reportKeys:
            for node in subheaders:
                headers.append(node)
                keyheaders.append(mode.lower().replace(" ", "_") + "_" + headkeys[subheaders.index(node)])
        # headers.append("Oven Baking Time")
        keyheaders.append("bakingTime")

        hpstack = []
        hpstack.append({"rowspan":2, "colspan":1, "name": "Time"})
        for prop in self.reportKeys:
            hpstack.append({"rowspan":1, "colspan":2, "name": prop })
        hpstack.append({"rowspan":2, "colspan":1, "name": "Oven Baking Time"})


        ht = ''
        ht += '<table><thead><tr><th style=""></th>'
        for hd in hpstack:
            if hd["name"] == "Time":
                ht += '<th rowspan="'+str(hd['rowspan'])+'" colspan="'+str(hd['colspan'])+'" style="min-width: 90;">'+hd["name"]+'</th>'
            else:
                ht += '<th rowspan="'+str(hd['rowspan'])+'" colspan="'+str(hd['colspan'])+'" style="">'+hd["name"]+'</th>'
        rowcnt = 0
        ht += '</tr>'
        ht += '<tr style="text-align: right;">'
        ht += '<th style=""></td>'
        for node in headers:
            ht += '<th style="">'+node+'</th>'
        ht += '</tr>'
        ht += '</thead><tbody>'
        

        for node in out_report:
            rowcnt += 1
            ht += '<tr style="text-align: right;">'
            ht += '<td style="">'+str(rowcnt)+'</td>'
            for key in keyheaders:
                ht += '<td style="">'+str(node.get(key,"-"))+'</td>'
        ht += '</tbody></table>'


        out_pdf= FILE_PATH + 'Oven_Report_'+selectedDate+'.pdf'
        intermediate_html = FILE_PATH + 'intermediate.html'
        reportTitle = "Oven Daily Report"

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
        
        intermediate_html = FILE_PATH + 'intermediate.html'
        self.to_html_pretty_report(ht, intermediate_html, "Oven Daily Report", htmlToAdd, reportTitle, selectedDate)
        htmlToAdd = ""

        options = {'orientation': 'Landscape'}
        # pdfkit.from_file(intermediate_html, out_pdf, options=options, configuration = config)
        pdfkit.from_file(intermediate_html, out_pdf, options=options)
        return out_pdf

    def to_html_pretty_report(self, df, filename='out.html', title='', htmlToAdd='',reportTitle='', selectedDate=''):
        htm = ''
        if htmlToAdd != '':
            htm += htmlToAdd
        if title != '':
            htm += '<h1><img src="' + CONFIG_PATH + 'abz2_small.png" style="margin-right:100px;margin-top:5px;"/>'
            htm += '<span style="margin-left:110px;text-align:center;color:#323232;font-size:22px;">'\
                                '<span style="color:#323232;font-size:18px;margin-right:2rem;">'+reportTitle+'</span>'\
                            '</span>'\
                            '<span style="text-align:right;color:#323232;font-size:22px;margin-left:110px;">'\
                                '<span style="color:#323232;font-size:18px;"> Generation Date ('+selectedDate+') </span>'\
                            '</span></h1>'
            htm += '<h2> %s </h2>\n' % title
        htm += df
        with open(filename, 'a') as f:
             f.write(HTML_TEMPLATE1 + htm + HTML_TEMPLATE2)
        
    def to_html_pretty(self, df, filename='out.html', title='', htmlToAdd='',reportTitle='', selectedDate=''):
        ht = ''
        if htmlToAdd != '':
            ht += htmlToAdd
        if title != '':
            ht += '<h1><img src="' + CONFIG_PATH + 'abz2_small.png" style="margin-right:100px;margin-top:5px;"/>'
            ht += '<span style="margin-left:110px;text-align:center;color:#323232;font-size:22px;">'\
                                '<span style="color:#323232;font-size:18px;margin-right:2rem;">'+reportTitle+'</span>'\
                            '</span>'\
                            '<span style="text-align:right;color:#323232;font-size:22px;margin-left:110px;">'\
                                '<span style="color:#323232;font-size:18px;"> Generation Date ('+selectedDate+') </span>'\
                            '</span></h1>'
            ht += '<h2> %s </h2>\n' % title
        ht += df.to_html(classes='wide', escape=False)

        with open(filename, 'a') as f:
             f.write(HTML_TEMPLATE1 + ht + HTML_TEMPLATE2)


    def save_oven_report(self, dateparam):
        self.log.info("Saving Report...Oven")
        out_list = self.get_oven_report(dateparam)
        filename = self.downloadOvenReport(out_list, dateparam)
        path = FILE_PATH
        uuidstr = str(uuid.uuid4())
        filepath = filename

        return filepath

    def save_oven_home(self, dateparam):
        self.log.info("Saving Dashboard Report...Oven")
        filename = self.get_oven_home(dateparam)
        path = FILE_PATH
        uuidstr = str(uuid.uuid4())
        filepath = filename

        return filepath

    def get_oven_home(self, dateparam):
        self.read_settings()
        result = False

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
        # myDb = connection["analyse_db"]
        db = myDb["oven_staging"]

        item_count = db.count_documents(find_dict)
        if item_count == 0:
            self.log.info("Data not available in staging... Getting From Mains...")
            self.get_today_records(selectedDate)
            find_dict = {"asofdate":selectedDate}
            item_count = db.count_documents(find_dict)
        self.log.info(item_count)
        line_color = {
            'SetPoint': '#662441',
            'Actual': '#e34566',
            'CurrentSetPoint': '#74d600',
            'CurrentActual': '#08c'
        }
        legends_format = {
            'SetPoint':{
                'name' : 'Set Temp',
                # 'color' : '#3eb308',
                'color' : line_color['SetPoint'],
                'dashStyle' : 'Solid',
                'type' : 'line',
                'y':0,
                'visible' : True
            },
            'Actual' : {
                'name' : 'Actual Temp',
                # 'color' : '#3eb308',
                'color' : line_color['Actual'],
                'dashStyle' : 'Solid',
                'type' : 'line',
                'y':0,
                'visible' : True
            }
        }
        _dict = {}
        _averageBakingTime = []
        bakingChartObj = {}
        baking_dict = {}
        baking_line_data = {}
        baking_series = {}
        baking_time_category = []
        baking_legends = {}
        baking_result = {}
        if item_count > 0:
            dbresult = db.find(find_dict)
            for dt in dbresult:
                if dt != []:        
                    if str(dt["Prop"]) not in _dict.keys():
                        _dict.setdefault(str(dt["Prop"]), [])
                    _dict[str(dt["Prop"])].append(dt)
        
        if _dict != {}:
            target_dict = {}
            final_dict = {}
            minNum = 10000
            maxNum = -1
            maxTime = ""
            minTime = ""
            setminNum = 10000
            setmaxNum = -1
            setmaxTime = ""
            setminTime = ""
            result = {}
            line_data = {}
            line_result = {}
            line_series = []
            baking_dict = {}
            baking_line_data = {}
            baking_series = {} 
            baking_time_category = []
            baking_legends = {}
            baking_result = {}

            for prop in self.reportKeys:
                # if prop == "Moulder":
                minNum = 10000
                maxNum = -1
                maxTime = ""
                minTime = ""
                setminNum = 10000
                setmaxNum = -1
                setmaxTime = ""
                setminTime = ""
                cminNum = 0
                cmaxNum = -1
                cmaxTime = ""
                cminTime = ""
                line_series = {}
                line_data = {}
                line_result = {}
                for leg in legends_format:
                    line_result[leg] = {
                        'name': legends_format[leg]['name'],
                        'data': [],
                        'yAxis': legends_format[leg]['y'],
                        'type': legends_format[leg]['type'],
                        'color': legends_format[leg]['color'],
                        'visible': legends_format[leg]['visible']
                    }
                stage_data = _dict[prop]
                for node in stage_data:
                    actual_num = elib.tonum(node["Actual"])
                    setpoint = elib.tonum(node["SetPoint"])
                    recipeValue = node["RecipeValue"]
                    # current_num = elib.tonum(node["Frequency"])
                    bakingTime =elib.tonum(node["BakingTime"],"float")
                    if bakingTime != 0:
                        elib.dictIncrement1D(baking_dict, recipeValue, [bakingTime])

                    xTime = node["Time"]
                    xDateTime =  xTime.strftime("%Y-%m-%d %H:%M")
                    # print xDateTime,'---', actual_num
                    if xDateTime in timerange:
                        if actual_num > 0:
                            elib.dictIncrement1D(target_dict, "Actual", actual_num)
                            elib.dictIncrement1D(target_dict, "MinMax", [actual_num])
                        else:
                            elib.dictIncrement1D(target_dict, "Actual", 0)
                            elib.dictIncrement1D(target_dict, "MinMax", [0])

                        if setpoint > 0:
                            elib.dictIncrement1D(target_dict, "SetPoint", setpoint)
                            elib.dictIncrement1D(target_dict, "SetMinMax", [setpoint])
                        else:
                            elib.dictIncrement1D(target_dict, "SetPoint", 0)
                            elib.dictIncrement1D(target_dict, "SetMinMax", [0])

                        if bakingTime != 0:
                            elib.dictIncrement(baking_line_data, recipeValue, xDateTime, [bakingTime])

                        if actual_num > 0:
                            elib.dictIncrement(line_data, xDateTime, "Actual", [actual_num])
                        else:
                            if xDateTime not in line_data.keys():
                                line_data.setdefault(xDateTime, {}).setdefault("Actual", [0])
                                line_data.setdefault(xDateTime, {}).setdefault("SetPoint", [0])
                            elif "Actual" not in line_data[xDateTime]:
                                line_data[xDateTime].setdefault("Actual", [0])
                                line_data[xDateTime].setdefault("SetPoint", [0])

                        if setpoint > 0:
                            elib.dictIncrement(line_data, xDateTime, "SetPoint", [elib.tonum(node["SetPoint"])])
                        else:
                            if xDateTime not in line_data.keys():
                                line_data.setdefault(xDateTime, {}).setdefault("SetPoint", [0])
                            elif "SetPoint" not in line_data[xDateTime]:
                                line_data[xDateTime].setdefault("SetPoint", [0])

                for xtime in line_data.keys():
                    line_series.setdefault(xtime,{})
                    for key in line_data[xtime]:
                        avg = sum(line_data[xtime][key]) / len(line_data[xtime][key])
                        line_series[xtime].setdefault(key, avg)

                        if key == "Actual":
                            if maxNum < avg:
                                maxNum = avg
                                maxTime = xtime
                            if minNum >= avg:
                                minNum = avg
                                minTime = xtime
                        if key == "SetPoint":
                            if setmaxNum < avg:
                                setmaxNum = avg
                                setmaxTime = xtime
                            if setminNum >= avg:
                                setminNum = avg
                                setminTime = xtime
                        
                for xtime in sorted(line_series.keys()):
                    for leg in legends_format:
                        line_result[leg]["data"].append({
                            "category": xtime,
                            "y": elib.rnd(line_series[xtime][leg],2)
                        })

                average = target_dict.get("Actual",0) / len(target_dict.get("MinMax",[0]))
                average_set = target_dict.get("SetPoint",0) / len(target_dict.get("SetMinMax",[0]))
                # average_current = target_dict["CurrentActual"] / len(target_dict["CurrentMinMax"])

                chartResult = []
                isData = False
                for leg in legends_format:
                    if len(line_result[leg]['data']) > 0:
                        isData = True
                    chartResult.append(line_result[leg])

                chartObj = {}
                chartObj["categories"] = sorted(line_series.keys())
                chartObj['charttype'] = 'linechart'
                chartObj['id'] = 'line_'+prop.lower().replace(' ', '_')
                chartObj['series'] = chartResult
                chartObj['isData'] = isData
                xAxis = []
                for x in sorted(line_series.keys()):
                    xAxis.append(x[11:])

                linechart = Highchart()
                lineoptions = {
                    'chart': {
                        'type': 'line',
                        'height': 400,
                        'width': 1100,
                        'spacingTop':10,
                        'spacingLeft':5,
                        'spacingBottom':10,
                        'spacingRight':55,
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
                        }
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
                        }
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
                
                final_dict = {}
                final_dict["line_chart"] = chartObj

                final_dict.setdefault("Average", elib.rnd(elib.tonum(average,"float"),2))
                final_dict.setdefault("SetAverage", elib.rnd(elib.tonum(average_set,"float"),2))
                # final_dict.setdefault("CurrentAverage", elib.rnd(elib.tonum(average_current,"float"),2))
                final_dict.setdefault("Max", elib.rnd(maxNum, 2))
                final_dict.setdefault("Min", elib.rnd(minNum, 2))
                final_dict.setdefault("MaxTime", maxTime)
                final_dict.setdefault("MinTime", minTime)

                final_dict.setdefault("SetMax", elib.rnd(setmaxNum, 2))
                final_dict.setdefault("SetMin", elib.rnd(setminNum, 2))
                final_dict.setdefault("SetMaxTime", setmaxTime)
                final_dict.setdefault("SetMinTime", setminTime)
                # final_dict.setdefault("CurrentMax", elib.rnd(cmaxNum, 2))
                # final_dict.setdefault("CurrentMin", elib.rnd(cminNum, 2))
                # final_dict.setdefault("CurrentMaxTime", cmaxTime)
                # final_dict.setdefault("CurrentMinTime", cminTime)

                out_result.append({"prop": prop, "data": final_dict})
        for recKey in self.recipeKeys:
                baking_series.setdefault(recKey, {})
                baking_legends = {}
                averageRow = {}
                baking_result = {}
                baking_time_category = []
                xAxis = []
                bakingData = baking_dict.get(elib.tonum(recKey,"int"), [])
                lenData = len(bakingData) if len(bakingData) > 0 else 1
                sumData = sum(bakingData) if len(bakingData) > 1 else bakingData[0] if len(bakingData) == 1 else 0
                avgData = sumData / lenData
                if avgData == 0:
                    newbakingTime = "-"
                else:
                    newbakingTime = time.strftime('%H:%M:%S', time.gmtime(avgData))
                setList = self.recipeSet[recKey].split(".")
                setvalue = 0
                setminValue = setList[0].split('m')
                setmin = elib.tonum(setminValue[0])
                setsec = 0
                if len(setList) > 1:
                    setSecValue = setList[1].split("s")
                    setsec = elib.tonum(setSecValue[0])

                if setsec == 0:
                    setvalue = setmin
                else:
                    setvalue = setmin + (setsec/60)
                
                if newbakingTime == "-":
                    efficiency = "-"
                else:
                    actList = newbakingTime.split(":")
                    actminvalue = elib.tonum(actList[1])
                    actsec = elib.tonum(actList[2])


                    actvalue = actminvalue + (actsec/60)
                    efficiency = (1 - ((actvalue - setvalue) / setvalue)) * 100

                averageRow.setdefault("name", self.recipeName[recKey])
                averageRow.setdefault("SetPoint", self.recipeSet[recKey])
                if avgData == 0:
                    newbakingTime = "-"
                else:
                    newbakingTime = time.strftime('%H:%M:%S', time.gmtime(avgData))

                averageRow.setdefault("name", self.recipeName[recKey])
                averageRow.setdefault("SetPoint", self.recipeSet[recKey])
                averageRow.setdefault("recKey", recKey)
                
                averageRow.setdefault("Actual", newbakingTime)
                averageRow.setdefault("Efficiency", elib.rnd(efficiency,2))
                
                baking_legends.setdefault(self.recipeName[recKey]+"_SetPoint", {
                    'name' : self.recipeName[recKey]+ ' Standard Time',
                    # 'color' : '#3eb308',
                    'key':'SetPoint',
                    'color' : line_color['SetPoint'],
                    'dashStyle' : 'Solid',
                    'type' : 'line',
                    'y':0,
                    'visible' : True
                })

                baking_legends.setdefault(self.recipeName[recKey]+"_Actual", {
                    'name' : self.recipeName[recKey]+ ' Actual Time',
                    # 'color' : '#3eb308',
                    'key':'Actual',
                    'color' : line_color['Actual'],
                    'dashStyle' : 'Solid',
                    'type' : 'line',
                    'y':0,
                    'visible' : True
                })

                lineData = baking_line_data.get(elib.tonum(recKey, "int"), {})

                for xtime in lineData:
                    if xtime not in baking_time_category:
                        baking_time_category.append(xtime)

                    bData = lineData.get(xtime, [0])
                    blen = len(bData) if len(bData) > 0 else 1
                    bsum = sum(bData) if len(bData) > 1 else bData[0] if len(bData) == 1 else 0
                    bavg = bsum / blen
                    plotval = bavg/60

                    # avg = sum(line_data[xtime][key]) / len(line_data[xtime][key])
                    baking_series[recKey].setdefault(xtime, elib.rnd(plotval,2))

                for leg in sorted(baking_legends.keys()):
                    baking_result[leg] = {
                        'name': baking_legends[leg]['name'],
                        'data': [],
                        'yAxis': baking_legends[leg]['y'],
                        'type': baking_legends[leg]['type'],
                        'color': baking_legends[leg]['color'],
                        'visible': baking_legends[leg]['visible']
                    }


                for xtime in sorted(baking_time_category):
                    for leg in sorted(baking_legends.keys()):
                        legKey = baking_legends[leg]["key"]
                        if legKey == "SetPoint":
                            setValue = self.recipeSet[recKey].split(".")
                            setminValue = setValue[0].split('m')
                            setmin = elib.tonum(setminValue[0])
                            setsec = 0
                            if len(setValue) > 1:
                                setSecValue = setValue[1].split("s")
                                setsec = elib.tonum(setSecValue[0])

                            if setsec == 0:
                                yvalue = setmin
                            else:
                                yvalue = setmin + (setsec / 60)

                            baking_result[leg]["data"].append({
                                "category": xtime[11:],
                                "y": elib.rnd(yvalue, 2)
                            })
                        else:
                            baking_result[leg]["data"].append({
                                "category": xtime[11:],
                                "y": elib.rnd(baking_series[recKey].get(xtime,0), 2)
                            })
                    xAxis.append(xtime[11:])
                bakingchartResult = []
                isData = False
                for leg in sorted(baking_result.keys(), reverse=True):
                    if len(baking_result[leg]['data']) > 0:
                        isData = True
                    bakingchartResult.append(baking_result[leg])

                bakingChartObj = {}
                bakingChartObj["categories"] = sorted(baking_time_category)
                bakingChartObj['charttype'] = 'linechart'
                bakingChartObj['id'] = 'line_baking_efficiency_'+recKey
                bakingChartObj['series'] = bakingchartResult
                bakingChartObj['isData'] = isData
                averageRow.setdefault("chart", bakingChartObj)

                bakinglinechart = Highchart()
                bakinglineoptions = {
                    'chart': {
                        'type': 'line',
                        'height': 400,
                        'width': 1100,
                        'spacingTop':10,
                        'spacingLeft':5,
                        'spacingBottom':10,
                        'spacingRight':55,
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
                        'categories':sorted(xAxis),
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
                        }
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
                        }
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

                bakinglinechart.set_dict_options(bakinglineoptions)
                for ln in bakingchartResult:
                    bakinglinechart.add_data_set(ln["data"], series_type=ln["type"], name=ln["name"], color=ln["color"])
                bakinglinechart.save_file(FILE_PATH + bakingChartObj["id"])
                html_list.append({"id": bakingChartObj["id"], "type":"line"})

                _averageBakingTime.append(averageRow)

        for ht in html_list:
            self.htmltoImage(ht["id"], ht["type"])

        out_pdf= FILE_PATH + 'Oven_Dashboard_'+selectedDate+'.pdf'
        intermediate_html = FILE_PATH + 'intermediate.html'

        htmlToAdd = '<div style="margin-left:10px;margin-top:5px;text-align:center;border:1px solid white;">'\
                        '<div style="text-center:left;margin-left:1rem;margin-right:1rem;margin-top:500px;">'\
                            '<img src="' + CONFIG_PATH + 'abz2_big.png" style=""/>'\
                            '<div style="text-align:center;color:#323232;font-size:35px;margin-top:7px;">'\
                                '<span style="color:#323232;font-size:35px;margin-right:2rem;">Oven Daily Report</span>'\
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
        for prop in self.reportKeys:
            propname = prop.lower().replace(" ", "_")
            propData = self.getPropData(out_result, prop)
            imgname = FILE_PATH + "line_"+str(propname)+".png"
            if index == 0 or index % 2 == 0: 
                ht = ""
                ht += '<div class="flex flex--col flex__item>'
            ht += '<div class="flex flex--col flex__item custom-holder" style="width:120%;">'\
                    '<div class="flex flex--col flex__item">'\
                        '<div class="flex flex--row flex--middle cnt-sub" style="height: 30px;width: 100%;">'\
                            '<div class="hdr-txt2 pointer" style="margin-left:1rem;padding-left: 1rem;padding-right:1rem;">'+prop+'</div>'\
                            '</div>'\
                        '</div>'\
                        '<div class="flex flex--row flex__item">'\
                            '<div class="flex flex--col flex__item custom-holder-2" style="width:25%;">'\
                                '<div class="flex flex--row flex--middle cnt-sub-2" style="height:25px; width:100%">'\
                                    '<div class="hdr-txt3 pointer" style="margin-left:1rem;padding-left: 1rem;padding-right:1rem;">Overview</div>'\
                                '</div>'\
                                '<div class="flex flex--row flex--center flex__item margin--all">'\
                                    '<div class="flex flex--col flex__item" style="">'\
                                        '<div class="flex flex__item flex--middle margin--left" style="">'\
                                            '<div class="flex__item text-left" style="margin-left:10px;">&#8451;</div>'\
                                        '</div>'\
                                        '<div class="flex flex__item flex--middle margin--left overview-header-border" style="">'\
                                            '<div class="flex__item text-left" style="margin-left:10px;">Average</div>'\
                                        '</div>'\
                                        '<div class="flex flex__item flex--middle margin--left overview-header-border">'\
                                            '<div class="flex__item text-left" style="margin-left:10px;">Max</div>'\
                                        '</div>'\
                                        '<div class="flex flex__item flex--middle margin--left overview-header-border" style="border-bottom:1px solid #e9e9e9;">'\
                                            '<div class="flex__item text-left" style="margin-left:10px;">Min</div>'\
                                        '</div>'\
                                        '<div class="flex flex__item flex--middle margin--left margin--top" style="">'\
                                            '<div class="flex__item text-left" style="margin-left:10px;">&#8451;</div>'\
                                        '</div>'\
                                        '<div class="flex flex__item flex--middle margin--left overview-header-border" style="">'\
                                            '<div class="flex__item text-left" style="margin-left:10px;">Set Average</div>'\
                                        '</div>'\
                                        '<div class="flex flex__item flex--middle margin--left overview-header-border">'\
                                            '<div class="flex__item text-left" style="margin-left:10px;">Set Max</div>'\
                                        '</div>'\
                                        '<div class="flex flex__item flex--middle margin--left overview-header-border" style="border-bottom:1px solid #e9e9e9;">'\
                                            '<div class="flex__item text-left" style="margin-left:10px;">Set Min</div>'\
                                        '</div>'\
                                    '</div>'\
                                    '<div class="flex flex--col flex__item" style="">'\
                                        '<div class="flex flex__item flex--middle margin--left">'\
                                            '<div class="flex__item text-left" style="margin-left:10px;color:white;">&#8451;</div>'\
                                        '</div>'\
                                        '<div class="flex flex__item flex--middle flex--right text-large overview-value-border" style="">'\
                                            '<div class="flex__item text-right" style="margin-right:2px;">'+str(propData["Average"])+' &#8451;</div>'\
                                        '</div>'\
                                        '<div class="flex flex__item flex--middle flex--right text-large overview-value-border">'\
                                            '<div class="flex__item text-right" style="margin-right:2px;">'+str(propData["Max"])+' &#8451;</div>'\
                                        '</div>'\
                                        '<div class="flex flex__item flex--middle flex--right text-large overview-value-border" style="border-bottom:1px solid #e9e9e9;">'\
                                            '<div class="flex__item text-right" style="margin-right:2px;">'+str(propData["Min"])+' &#8451;</div>'\
                                        '</div>'\
                                        '<div class="flex flex__item flex--middle margin--left margin--top">'\
                                            '<div class="flex__item text-left" style="margin-left:10px;color:white;">&#8451;</div>'\
                                        '</div>'\
                                        '<div class="flex flex__item flex--middle flex--right text-large overview-value-border" style="">'\
                                            '<div class="flex__item text-right" style="margin-right:2px;">'+str(propData["SetAverage"])+' &#8451;</div>'\
                                        '</div>'\
                                        '<div class="flex flex__item flex--middle flex--right text-large overview-value-border">'\
                                            '<div class="flex__item text-right" style="margin-right:2px;">'+str(propData["SetMax"])+' &#8451;</div>'\
                                        '</div>'\
                                        '<div class="flex flex__item flex--middle flex--right text-large overview-value-border" style="border-bottom:1px solid #e9e9e9;">'\
                                            '<div class="flex__item text-right" style="margin-right:2px;">'+str(propData["SetMin"])+' &#8451;</div>'\
                                        '</div>'\
                                    '</div>'\
                                    '<div class="flex flex--col flex__item" style="">'\
                                        '<div class="flex flex__item flex--middle margin--left">'\
                                            '<div class="flex__item text-left" style="margin-left:10px;color:white;">&#8451;</div>'\
                                        '</div>'\
                                        '<div class="flex flex__item flex--middle flex--right text-large margin--right overview-value-border" style="">'\
                                            '<div class="flex__item text-right" style="margin-right:10px;color:white;">'+str(propData["MaxTime"])+'</div>'\
                                        '</div>'\
                                        '<div class="flex flex__item flex--middle flex--right text-large margin--right overview-value-border">'\
                                            '<div class="flex__item text-right" style="margin-right:10px;">'+str(propData["MaxTime"])+'</div>'\
                                        '</div>'\
                                        '<div class="flex flex__item flex--middle flex--right text-large margin--right overview-value-border" style="border-bottom:1px solid #e9e9e9;">'\
                                            '<div class="flex__item text-right" style="margin-right:10px;">'+str(propData["MinTime"])+'</div>'\
                                        '</div>'\
                                        '<div class="flex flex__item flex--middle flex--right text-large margin--right overview-value-border" style="">'\
                                            '<div class="flex__item text-right" style="margin-right:10px;color:white;">'+str(propData["SetMaxTime"])+'</div>'\
                                        '</div>'\
                                        '<div class="flex flex__item flex--middle flex--right text-large margin--right overview-value-border">'\
                                            '<div class="flex__item text-right" style="margin-right:10px;">'+str(propData["SetMaxTime"])+'</div>'\
                                        '</div>'\
                                        '<div class="flex flex__item flex--middle flex--right text-large margin--right overview-value-border" style="border-bottom:1px solid #e9e9e9;">'\
                                            '<div class="flex__item text-right" style="margin-right:10px;">'+str(propData["SetMinTime"])+'</div>'\
                                        '</div>'\
                                    '</div>'\
                                '</div>'\
                            '</div>'\
                            '<div class="flex flex--col flex__item__3 custom-holder-2" style="width:70%;">'\
                                '<div class="flex flex--row flex--middle cnt-sub-2" style="height:25px; width:100%;">'\
                                    '<div class="hdr-txt3 pointer" style="margin-left:1rem;padding-left: 1rem;padding-right:1rem;">Temperature</div>'\
                                '</div>'\
                                '<div class="flex flex__item" style="margin:10px;width:100%;">'\
                                    '<img height="400" src="'+imgname+'"/>'\
                                '</div>'\
                            '</div>'\
                        '</div>'\
                    '</div>'\
                  '</div>'
            index += 1
            imagesToDelete.append(imgname)
            if index % 2 == 0: 
                ht += '</div>'
                self.to_html_pretty_2(ht, intermediate_html, prop, htmlToAdd, "Oven Daily Report", selectedDate)
                htmlToAdd = ""
            # elif index >= len(self.reportKeys) and index % 2 != 0:
            #     # ht += '</div>'
            #     self.to_html_pretty_2(ht, intermediate_html, prop, htmlToAdd, "Oven Daily Report", selectedDate)
            #     htmlToAdd = ""
        newindex = 0
        for summary in _averageBakingTime:
            prop = summary["recKey"]
            imgname = FILE_PATH + "line_baking_efficiency_"+str(prop)+".png"
            if index == 0 or index % 2 == 0: 
                ht = ""
                ht = '<div class="flex flex--col flex__item>'
            ht += '<div class="flex flex--col flex__item custom-holder" style="width:120%;">'\
                    '<div class="flex flex--col flex__item">'\
                        '<div class="flex flex--row flex--middle cnt-sub" style="height: 30px;width: 100%;">'\
                            '<div class="hdr-txt2 pointer" style="margin-left:1rem;padding-left: 1rem;padding-right:1rem;">Baking Time '+summary["name"]+'</div>'\
                            '</div>'\
                        '</div>'\
                        '<div class="flex flex--row flex__item">'\
                            '<div class="flex flex--col flex__item custom-holder-2" style="width:25%;">'\
                                '<div class="flex flex--row flex--middle cnt-sub-2" style="height:25px; width:100%">'\
                                    '<div class="hdr-txt3 pointer" style="margin-left:1rem;padding-left: 1rem;padding-right:1rem;">Summary</div>'\
                                '</div>'\
                                '<div class="flex flex--row flex--center flex__item margin--all">'\
                                    '<div class="flex flex--col flex__item" style="">'\
                                        '<div class="flex flex__item flex--middle margin--left text-large overview-header-border" style="">'\
                                            '<div class="flex__item text-left" style="margin-left:10px;">Standard Time</div>'\
                                        '</div>'\
                                        '<div class="flex flex__item flex--middle margin--left text-large overview-header-border" style="border-bottom:1px solid #e9e9e9;">'\
                                            '<div class="flex__item text-left" style="margin-left:10px;">Average Actual Time</div>'\
                                        '</div>'\
                                        '<div class="flex flex__item flex--middle margin--left text-large overview-header-border" style="border-bottom:1px solid #e9e9e9;">'\
                                            '<div class="flex__item text-left" style="margin-left:10px;">Efficiency</div>'\
                                        '</div>'\
                                    '</div>'\
                                    '<div class="flex flex--col flex__item" style="">'\
                                        '<div class="flex flex__item flex--middle flex--right text-large overview-value-border">'\
                                            '<div class="flex__item text-right" style="margin-right:2px;">'+str(summary["SetPoint"])+'</div>'\
                                        '</div>'\
                                        '<div class="flex flex__item flex--middle flex--right text-large overview-value-border" style="border-bottom:1px solid #e9e9e9;">'\
                                            '<div class="flex__item text-right" style="margin-right:2px;">'+str(summary["Actual"])+'</div>'\
                                        '</div>'\
                                        '<div class="flex flex__item flex--middle flex--right text-large overview-value-border" style="border-bottom:1px solid #e9e9e9;">'\
                                            '<div class="flex__item text-right" style="margin-right:2px;">'+str(summary["Efficiency"])+'</div>'\
                                        '</div>'\
                                    '</div>'\
                                '</div>'\
                            '</div>'\
                            '<div class="flex flex--col flex__item__3 custom-holder-2" style="width:70%;">'\
                                '<div class="flex flex--row flex--middle cnt-sub-2" style="height:25px; width:100%;">'\
                                    '<div class="hdr-txt3 pointer" style="margin-left:1rem;padding-left: 1rem;padding-right:1rem;">Temp Trend</div>'\
                                '</div>'\
                                '<div class="flex flex__item" style="margin:10px;width:100%;">'\
                                    '<img height="400" src="'+imgname+'"/>'\
                                '</div>'\
                            '</div>'\
                        '</div>'\
                    '</div>'\
                '</div>'
            index += 1
            newindex += 1
            imagesToDelete.append(imgname)
            if index % 2 == 0: 
                ht += '</div>'
                self.to_html_pretty_2(ht, intermediate_html, prop, htmlToAdd, "Oven Daily Report", selectedDate)
                htmlToAdd = ""
            elif newindex >= len(_averageBakingTime) and index % 2 != 0:
                ht += '</div>'
                self.to_html_pretty_2(ht, intermediate_html, prop, htmlToAdd, "Oven Daily Report", selectedDate)
                htmlToAdd = ""
        
        options = {
            "orientation": "Landscape",
        }
        # pdfkit.from_file(intermediate_html, out_pdf, options=options, configuration=config)
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

    def getPropData(self, out_list, identifier):
        result = {}
        for node in out_list:
            propname = node["prop"].lower().replace(" ", "_")
            if node["prop"] == identifier:
                result = node["data"]
                break
        return result

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
    dbMoulderManager = ORun()
    dbMoulderManager.get_today_records("2019-04-18")
    moulder_report = dbMoulderManager.save_oven_home("2019-04-10")
