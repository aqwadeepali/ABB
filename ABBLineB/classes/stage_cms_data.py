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

CONFIG_PATH = str(os.path.realpath(__file__))
CONFIG_PATH = CONFIG_PATH.replace("stage_cms_data.pyc", "")
CONFIG_PATH = CONFIG_PATH.replace("stage_cms_data.pyo", "")
CONFIG_PATH = CONFIG_PATH.replace("stage_cms_data.py", "")
CONFIG_PATH = CONFIG_PATH + "data/"

FILE_PATH = str(os.path.realpath(__file__))
FILE_PATH = FILE_PATH.replace("stage_cms_data.pyc", "")
FILE_PATH = FILE_PATH.replace("stage_cms_data.pyo", "")
FILE_PATH = FILE_PATH.replace("stage_cms_data.py", "")
FILE_PATH = FILE_PATH + "../dbpush/data/"

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

class CMSRun():
    def __init__(self):
        
        self.collection = ""
        self.properties = ""
        self.reportKeys = []
        self.reportManager = {}
        self.log = getLogger()
        self.read_settings()

        self._date = "";
        self.all_dates = [];

        self.log.info('Reading Params....CMS')
        self.log.info('File Ready to Use...CMS')
        #print 'File Ready to Use...CMS'
        # self.get_today_records()


    def read_settings(self):
        #print "Reading Settings"
        all_json = ""
        all_keys = ""
        keys = ""
        collection = ""
        reportKeys = ""
        reportManager = ""
        keys = ""
        reader = csv.DictReader(open(CONFIG_PATH + 'stage_cms_settings.txt'), delimiter="\t")
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

    def read_from_db(self, dateparam = ""):
        self.log.info("CMS dateparam: %s", dateparam)
        
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
            _dict[prop].setdefault("CreamerRatioSP", [])
            _dict[prop].setdefault("CreamerRatioActual", [])
            _dict[prop].setdefault("MaidaActual", [])
            _dict[prop].setdefault("CreamActual", [])
            _dict[prop].setdefault("Time", [])
            target_dict.setdefault(prop, {})
        
        creamRatioSP = 0
        creamRatioActual = 0
        maidaActual = 0
        creamActual = 0
        for row in dbresult:
            for prop in self.properties:                 
                keyprop = prop.lower().replace(' ', '_')
                fbtime = row[self.config["time"]]
                
                self._date = fbtime.strftime("%Y-%m-%d")
                _dict[prop].setdefault(fbtime, {})
                creamRatioSP = row[self.config['cream_ratio_sp']] if row.get(self.config['cream_ratio_sp'], "--") != "--" else creamRatioSP
                creamRatioActual = elib.tonum(row[self.config['cream_ratio_actual']]) if row.get(self.config['cream_ratio_sp'], "--") != "--" else creamRatioActual
                maidaActual = elib.tonum(row[self.config['maida_actual']]) if row.get(self.config['maida_actual'], "--") != "--" else maidaActual
                creamActual = elib.tonum(row[self.config["cream_actual"]]) if row.get(self.config['cream_actual'], "--") != "--" else creamActual

                _dict[prop][fbtime]["CreamerRatioSP"] = elib.tonum(creamRatioSP)
                _dict[prop][fbtime]["CreamerRatioActual"] = elib.tonum(creamRatioActual)
                _dict[prop][fbtime]["MaidaActual"] = elib.tonum(maidaActual)
                _dict[prop][fbtime]["CreamActual"] = creamActual
                _dict[prop][fbtime]["Time"] = fbtime
                _dict[prop][fbtime]["Prop"] = prop
                
        return _dict

    def get_today_records(self, dateparam = ""):
        self.log.info("Data Push Started...CMS")
        # dateparam = "2018-11-01"
        target_dict = self.read_from_db(dateparam)
        # print target_dict
        connection = MongoClient('127.0.0.1', username="admin", password="admin123", authSource='analyse_db', authMechanism='SCRAM-SHA-1')
        myDb = connection["analyse_db"]
        self._date = dateparam
        self.log.info("CMS self._date: %s", self._date)
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
            myDb["cms_staging_lineB"].remove({'asofdate':self._date})
            record_id = myDb["cms_staging_lineB"].insert_many(dbData)
            print len(dbData),' records found'
            print "DB Push Completed...CMS"
            self.log.info('CMS %s records found', str(len(dbData)))
            self.log.info("DB Push Completed...CMS")
        else:
            print "No Data...CMS"

    def get_cms_report(self, dateparam):
        result = {}
        
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

        find_dict = {"asofdate":selectedDate}
        connection = MongoClient('127.0.0.1', username="admin", password="admin123", authSource='analyse_db', authMechanism='SCRAM-SHA-1')

        myDb = connection["analyse_db"]
        # myDb = connection["analyse_db"]
        db = myDb["cms_staging_lineB"]
        item_count = db.count_documents(find_dict)
        if item_count == 0:
            #print "Data not available in staging... Getting From Mains..."
            self.get_today_records(selectedDate)
            find_dict = {"asofdate":selectedDate}
            item_count = db.count_documents(find_dict)
        #print item_count
        
        _dict = {}
        if item_count > 0:
            dbresult = db.find(find_dict)
            for dt in dbresult:
                if dt != []:        
                    if str(dt["Prop"]) not in _dict.keys():
                        _dict.setdefault(str(dt["Prop"]), [])
                    _dict[str(dt["Prop"])].append(dt)
        # find_dict = {"asofdate":todayDate}

        # item_count = db.count_documents(find_dict)
        
        # if item_count == 0:
        #     #print "Data not available in staging... Getting From Mains..."
        #     self.get_today_records(todayDate)
        #     find_dict = {"asofdate":todayDate}
        #     item_count = db.count_documents(find_dict)
        # #print item_count
        # if item_count > 0:
        #     dbresult = db.find(find_dict)            
        #     for dt in dbresult:
        #         if dt != []:        
        #             if str(dt["Prop"]) not in _dict.keys():
        #                 _dict.setdefault(str(dt["Prop"]), [])
        #             _dict[str(dt["Prop"])].append(dt)

        if _dict != {}:

            target_dict = {}
            final_dict = {}
            for prop in self.reportKeys:
                minNum = 0
                maxNum = -1
                maxTime = ""
                minTime = ""
                result = {}
                line_data_qty = {}
                line_data_ratio = {}
                line_result_qty = {}
                line_result_ratio = {}
                stage_data = _dict[prop]
                for node in stage_data:
            
                    xTime = node["Time"]
                    xDateTime =  xTime.strftime("%Y-%m-%d %H:%M")

                    if xDateTime in timerange:
                        maida_actual = elib.tonum(node["MaidaActual"])
                        cream_actual = elib.tonum(node["CreamActual"])
                        cream_ratio_actual = elib.tonum(node["CreamerRatioActual"])
                        cream_ratio_sp = elib.tonum(node["CreamerRatioSP"])
                        thput = maida_actual + cream_actual

                        elib.dictIncrement(target_dict, xDateTime, "MaidaActual", maida_actual)
                        elib.dictIncrement(target_dict, xDateTime, "CreamActual", cream_actual)
                        elib.dictIncrement(target_dict, xDateTime, "Throughput", thput)
                        elib.dictIncrement(target_dict, xDateTime, "CreamRatioActual", cream_ratio_actual)
                        elib.dictIncrement(target_dict, xDateTime, "CreamRatioSP", cream_ratio_sp)

                for xDate in timerange:
                    row = {}
                    row.setdefault("Time", xDate)
                    if xDate in target_dict.keys():
                        for key in target_dict[xDate]:
                            row.setdefault(key, target_dict[xDate][key])
                    out_result.append(row)

        return out_result

    def downloadCMSReport(self, out_report, dateparam):
        yesterdayDate = datetime.strptime(dateparam, '%Y-%m-%d')
        _date2460 = yesterdayDate + timedelta(minutes = (24*60))
        todayDate = _date2460.strftime('%Y-%m-%d')
        selectedDate = yesterdayDate.strftime("%Y-%m-%d")

        txtfilename = "cms_report.txt"

        data_list = []
        s = ""
        headers =  ["Time", "Set Cream Ratio", "Actual Cream Ratio", "Maida Qty", "Cream Qty", "Throughput Rate"]
        keyheaders = ["Time", "CreamRatioSP", "CreamRatioActual", "MaidaActual", "CreamActual", "Throughput"]

        for hd in headers:
            s += str(hd)
            index = headers.index(hd)
            if index < len(headers) - 1:
                s += "\t"
        data_list.append(s)

        for node in out_report:
            s = ""
            for key in keyheaders:
                s += str(node.get(key,"-"))
                index = keyheaders.index(key)
                if index < len(keyheaders) - 1:
                    s += "\t"
            data_list.append(s)

        outF = open(txtfilename, "w")
        for line in data_list:
            outF.write(line)
            outF.write("\n")
        outF.close()

        out_pdf= FILE_PATH + 'CMS_Report_'+selectedDate+'.pdf'
        intermediate_html = 'intermediate.html'
        reportTitle = "CMS Daily Report"

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
        
        df = pd.read_csv(txtfilename, delimiter="\t", delim_whitespace=False)
        intermediate_html = 'intermediate.html'
        self.to_html_pretty(df, intermediate_html, "CMS Daily Report", htmlToAdd, reportTitle, selectedDate)
        htmlToAdd = ""
        os.remove(txtfilename)
        # pdfkit.from_file(intermediate_html, out_pdf, configuration=config)
        pdfkit.from_file(intermediate_html, out_pdf)
        return out_pdf

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

    def get_cms_home(self, dateparam):
        # try:
        result = {}
        # params = self.get_params(request)
        self.read_settings()
        # dateparam = params.get('selectedDate', False)
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
        
        db = myDb["cms_staging_lineB"]
        item_count = db.count_documents(find_dict)
        if item_count == 0:
            self.log.debug("Data not available in staging... Getting From Mains...")
            self.get_today_records(selectedDate)
            find_dict = {"asofdate":selectedDate}
            item_count = db.count_documents(find_dict)
        self.log.debug(item_count)
        line_color = {
            'CreamActual': '#662441',
            'MaidaActual': '#e34566',
            'CreamRatioSP': '#74d600',
            'CreamRatioActual': '#08c'
        }
        _legend1 = {
            'CreamActual':{
                'name' : 'Cream',
                # 'color' : '#3eb308',
                'color' : line_color['CreamActual'],
                'dashStyle' : 'Solid',
                'type' : 'line',
                'y':0,
                'visible' : True
            },
            'MaidaActual' : {
                'name' : 'Maida',
                # 'color' : '#3eb308',
                'color' : line_color['MaidaActual'],
                'dashStyle' : 'Solid',
                'type' : 'line',
                'y':0,
                'visible' : True
            }
        }
        _legend2 = {
            'CreamRatioSP':{
                'name' : 'Cream Ratio SP',
                # 'color' : '#3eb308',
                'color' : line_color['CreamRatioSP'],
                'dashStyle' : 'Solid',
                'type' : 'line',
                'y':0,
                'visible' : True
            },
            'CreamRatioActual' : {
                'name' : 'Cream Ratio Actual',
                # 'color' : '#3eb308',
                'color' : line_color['CreamRatioActual'],
                'dashStyle' : 'Solid',
                'type' : 'line',
                'y':0,
                'visible' : True
            }
        }

        _dict = {}
        html_list = []
        if item_count > 0:
            dbresult = db.find(find_dict)
            for dt in dbresult:
                if dt != []:        
                    if str(dt["Prop"]) not in _dict.keys():
                        _dict.setdefault(str(dt["Prop"]), [])
                    _dict[str(dt["Prop"])].append(dt)
        # find_dict = {"asofdate":todayDate}
        # myDb = self.mongo["cms_staging_lineB"]
        # item_count = myDb.count_documents(find_dict)

        # if item_count == 0:
        #     self.log.debug("Data not available in staging... Getting From Mains...")
        #     self.dbManager.get_today_records(todayDate)
        #     find_dict = {"asofdate":todayDate}
        #     item_count = myDb.count_documents(find_dict)
        # self.log.debug(item_count)
        # if item_count > 0:
        #     dbresult = myDb.find(find_dict)            
        #     for dt in dbresult:
        #         if dt != []:        
        #             if str(dt["Prop"]) not in _dict.keys():
        #                 _dict.setdefault(str(dt["Prop"]), [])
        #             _dict[str(dt["Prop"])].append(dt)

        if _dict != {}:

            target_dict = {}
            final_dict = {}
            for prop in self.reportKeys:
                minNum = 10000
                maxNum = -1
                maxTime = ""
                minTime = ""
                result = {}
                line_data_qty = {}
                line_data_ratio = {}
                line_result_qty = {}
                line_result_ratio = {}
                line_series_qty = {}
                line_series_ratio = {}
                for leg in _legend1:
                    line_result_qty[leg] = {
                        'name': _legend1[leg]['name'],
                        'data': [],
                        'yAxis': _legend1[leg]['y'],
                        'type': _legend1[leg]['type'],
                        'color': _legend1[leg]['color'],
                        'visible': _legend1[leg]['visible']
                    }
                for leg in _legend2:
                    line_result_ratio[leg] = {
                        'name': _legend2[leg]['name'],
                        'data': [],
                        'yAxis': _legend2[leg]['y'],
                        'type': _legend2[leg]['type'],
                        'color': _legend2[leg]['color'],
                        'visible': _legend2[leg]['visible']
                    }
                stage_data = _dict[prop]
                for node in stage_data:
            
                    xTime = node["Time"]
                    xDateTime =  xTime.strftime("%Y-%m-%d %H:%M")

                    if xDateTime in timerange:
                        maida_actual = elib.tonum(node["MaidaActual"])
                        cream_actual = elib.tonum(node["CreamActual"])
                        thput = maida_actual + cream_actual
                        cream_ratio_actual = elib.tonum(node["CreamerRatioActual"])
                        cream_ratio_sp = elib.tonum(node["CreamerRatioSP"])

                        elib.dictIncrement1D(target_dict, "TotalMaida", maida_actual)
                        elib.dictIncrement1D(target_dict, "TotalCream", cream_actual)
                        elib.dictIncrement1D(target_dict, "Throughput", thput)

                        if(cream_ratio_actual > 0):
                            elib.dictIncrement1D(target_dict, "CreamRatioActual", [cream_ratio_actual])
                        else:
                            if "CreamRatioActual" not in target_dict:
                                target_dict.setdefault("CreamRatioActual", [0])


                        if maxNum < cream_ratio_actual:
                            maxNum = cream_ratio_actual
                            maxTime = xDateTime
                        if minNum >= cream_ratio_actual:
                            minNum = cream_ratio_actual
                            minTime = xDateTime
                        if maida_actual > 0:
                            elib.dictIncrement(line_data_qty, xDateTime, "MaidaActual", [maida_actual])
                        else:
                            if xDateTime not in line_data_qty.keys():
                                line_data_qty.setdefault(xDateTime, {}).setdefault("MaidaActual", [0])
                            elif "MaidaActual" not in line_data_qty[xDateTime].keys():
                                line_data_qty[xDateTime].setdefault("MaidaActual", [0])
                        if cream_actual > 0:
                            elib.dictIncrement(line_data_qty, xDateTime, "CreamActual", [cream_actual])
                        else:
                            if xDateTime not in line_data_qty.keys():
                                line_data_qty.setdefault(xDateTime, {}).setdefault("CreamActual", [0])
                            elif "CreamActual" not in line_data_qty[xDateTime].keys():
                                line_data_qty[xDateTime].setdefault("CreamActual", [0])

                        if cream_ratio_sp > 0:
                            elib.dictIncrement(line_data_ratio, xDateTime, "CreamRatioSP", [cream_ratio_sp])
                        else:
                            if xDateTime not in line_data_ratio.keys():
                                line_data_ratio.setdefault(xDateTime, {}).setdefault("CreamRatioSP", [0])
                            elif "MaidaActual" not in line_data_ratio[xDateTime].keys():
                                line_data_ratio[xDateTime].setdefault("CreamRatioSP", [0])
                        if cream_ratio_actual > 0:
                            elib.dictIncrement(line_data_ratio, xDateTime, "CreamRatioActual", [cream_ratio_actual])
                        else:
                            if xDateTime not in line_data_ratio.keys():
                                line_data_ratio.setdefault(xDateTime, {}).setdefault("CreamRatioActual", [0])
                            elif "CreamRatioActual" not in line_data_ratio[xDateTime].keys():
                                line_data_ratio[xDateTime].setdefault("CreamRatioActual", [0])

                for xtime in line_data_qty.keys():
                    line_series_qty.setdefault(xtime,{})
                    for key in line_data_qty[xtime]:
                        maxNum = max(line_data_qty[xtime][key])
                        line_series_qty[xtime].setdefault(key, maxNum)
                for xtime in line_data_ratio.keys():
                    line_series_ratio.setdefault(xtime,{})
                    for key in line_data_ratio[xtime]:
                        maxNum = max(line_data_ratio[xtime][key])
                        line_series_ratio[xtime].setdefault(key, maxNum)
                        
                for xtime in sorted(line_series_qty.keys()):
                    for leg in _legend1:
                        line_result_qty[leg]["data"].append({
                            "category": xtime,
                            "y": elib.rnd(line_series_qty[xtime][leg],2)
                        })
                for xtime in sorted(line_series_ratio.keys()):
                    for leg in _legend2:
                        line_result_ratio[leg]["data"].append({
                            "category": xtime,
                            "y": elib.rnd(line_series_ratio[xtime][leg],2)
                        })

                chartQtyResult = []
                isData = False
                for leg in _legend1:
                    if len(line_result_qty[leg]['data']) > 0:
                        isData = True
                    chartQtyResult.append(line_result_qty[leg])

                xAxis = []
                for x in sorted(line_series_qty.keys()):
                    xAxis.append(x[11:])

                chartObjQty = {}
                chartObjQty["categories"] = sorted(line_series_qty.keys())
                chartObjQty['charttype'] = 'linechart'
                chartObjQty['id'] = 'line_qty_'+prop.lower().replace(' ', '_')
                chartObjQty['series'] = chartQtyResult
                chartObjQty['isData'] = isData

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
                for ln in chartQtyResult:
                    linechart.add_data_set(ln["data"], series_type=ln["type"], name=ln["name"], color=ln["color"])
                linechart.save_file(FILE_PATH + chartObjQty["id"])
                html_list.append({"id": chartObjQty["id"], "type":"line"})

                chartRatioResult = []
                isData = False
                for leg in _legend2:
                    if len(line_result_ratio[leg]['data']) > 0:
                        isData = True
                    chartRatioResult.append(line_result_ratio[leg])

                xAxis1 = []
                for x in sorted(line_series_qty.keys()):
                    xAxis1.append(x[11:])

                chartObjRatio = {}
                chartObjRatio["categories"] = sorted(line_series_ratio.keys())
                chartObjRatio['charttype'] = 'linechart'
                chartObjRatio['id'] = 'line_ratio_'+prop.lower().replace(' ', '_')
                chartObjRatio['series'] = chartRatioResult
                chartObjRatio['isData'] = isData

                linechartRatio = Highchart()
                lineoptions1 = {
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
                        'categories':xAxis1,
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

                linechartRatio.set_dict_options(lineoptions1)
                for ln in chartRatioResult:
                    linechartRatio.add_data_set(ln["data"], series_type=ln["type"], name=ln["name"], color=ln["color"])
                linechartRatio.save_file(FILE_PATH + chartObjRatio["id"])
                html_list.append({"id": chartObjRatio["id"], "type":"line"})

                totalMaida = target_dict["TotalMaida"]
                totalCream = target_dict["TotalCream"]
                thoughput = target_dict["Throughput"]
                average = sum(target_dict["CreamRatioActual"])/ len(target_dict["CreamRatioActual"])

                final_dict = {}
                final_dict["line_chart_qty"] = chartObjQty
                final_dict["line_chart_ratio"] = chartObjRatio

                final_dict.setdefault("Average", elib.rnd(elib.tonum(average,"float"),2))
                final_dict.setdefault("Max", elib.rnd(maxNum, 2))
                final_dict.setdefault("Min", elib.rnd(minNum, 2))
                final_dict.setdefault("MaxTime", maxTime)
                final_dict.setdefault("MinTime", minTime)
                final_dict.setdefault("TotalCream", totalCream)
                final_dict.setdefault("TotalMaida", totalMaida)
                final_dict.setdefault("Throughput", thoughput)

                out_result.append({"prop": prop, "data": final_dict})

            for ht in html_list:
                self.htmltoImage(ht["id"], ht["type"])

            out_pdf= FILE_PATH + 'CMS_Dashboard_'+selectedDate+'.pdf'
            intermediate_html = FILE_PATH + 'intermediate.html'

            htmlToAdd = '<div style="margin-left:10px;margin-top:5px;text-align:center;border:1px solid white;">'\
                            '<div style="text-center:left;margin-left:1rem;margin-right:1rem;margin-top:500px;">'\
                                '<img src="' + CONFIG_PATH + 'abz2_big.png" style=""/>'\
                                '<div style="text-align:center;color:#323232;font-size:35px;margin-top:7px;">'\
                                    '<span style="color:#323232;font-size:35px;margin-right:2rem;">CMS Daily Report</span>'\
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
                lineqtyname = FILE_PATH + 'line_qty_'+str(propname)+'.png'
                linerationame = FILE_PATH + 'line_ratio_'+str(propname)+'.png'
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
                                        '<div class="hdr-txt3 pointer" style="margin-left:1rem;padding-left: 1rem;padding-right:1rem;">Summary</div>'\
                                    '</div>'\
                                    '<div class="flex flex--row flex--center flex__item margin--all">'\
                                        '<div class="flex flex--col flex__item" style="">'\
                                            '<div class="flex flex__item flex--middle margin--left" style="">'\
                                                '<div class="flex__item text-left" style="margin-left:10px;">Quantity</div>'\
                                            '</div>'\
                                            '<div class="flex flex__item flex--middle margin--left overview-header-border" style="">'\
                                                '<div class="flex__item text-left" style="margin-left:10px;">Total Maida</div>'\
                                            '</div>'\
                                            '<div class="flex flex__item flex--middle margin--left overview-header-border">'\
                                                '<div class="flex__item text-left" style="margin-left:10px;">Total Cream</div>'\
                                            '</div>'\
                                            '<div class="flex flex__item flex--middle margin--left overview-header-border" style="border-bottom:1px solid #e9e9e9;">'\
                                                '<div class="flex__item text-left" style="margin-left:10px;">Throughput</div>'\
                                            '</div>'\
                                            '<div class="flex flex__item flex--middle margin--left margin--top">'\
                                                '<div class="flex__item text-left" style="margin-left:10px;">Cream Ratio</div>'\
                                            '</div>'\
                                            '<div class="flex flex__item flex--middle margin--left overview-header-border">'\
                                                '<div class="flex__item text-left" style="margin-left:10px;">Average</div>'\
                                            '</div>'\
                                            '<div class="flex flex__item flex--middle margin--left overview-header-border">'\
                                                '<div class="flex__item text-left" style="margin-left:10px;">Max</div>'\
                                            '</div>'\
                                            '<div class="flex flex__item flex--middle margin--left overview-header-border" style="border-bottom:1px solid #e9e9e9;">' \
                                                '<div class="flex__item text-left" style="margin-left:10px;">Min</div>'\
                                            '</div>'\
                                        '</div>'\
                                        '<div class="flex flex--col flex__item" style="">'\
                                            '<div class="flex flex__item flex--middle margin--left">'\
                                                '<div class="flex__item text-left" style="margin-left:10px;color:white;">Quantity</div>'\
                                            '</div>'\
                                            '<div class="flex flex__item flex--middle flex--right text-large overview-value-border" style="">'\
                                                '<div class="flex__item text-right" style="margin-right:2px;">'+str(propData.get("TotalMaida","-"))+' Kg</div>'\
                                            '</div>'\
                                            '<div class="flex flex__item flex--middle flex--right text-large overview-value-border">'\
                                                '<div class="flex__item text-right" style="margin-right:2px;">'+str(propData.get("TotalCream","-"))+' Kg</div>'\
                                            '</div>'\
                                            '<div class="flex flex__item flex--middle flex--right text-large overview-value-border" style="border-bottom:1px solid #e9e9e9;">'\
                                                '<div class="flex__item text-right" style="margin-right:2px;">'+str(propData.get("Throughput","-"))+' Kg</div>'\
                                            '</div>'\
                                            '<div class="flex flex__item flex--middle margin--left margin--top">'\
                                                '<div class="flex__item text-left" style="margin-left:10px;color:white;">Current</div>'\
                                            '</div>'\
                                            '<div class="flex flex__item flex--middle flex--right text-large overview-value-border">'\
                                                '<div class="flex__item text-right" style="margin-right:2px;">'+str(propData.get("Average","-"))+' A</div>'\
                                            '</div>'\
                                            '<div class="flex flex__item flex--middle flex--right text-large overview-value-border">'\
                                                '<div class="flex__item text-right" style="margin-right:2px;">'+str(propData.get("Max","-"))+' A</div>'\
                                            '</div>'\
                                            '<div class="flex flex__item flex--middle flex--right text-large overview-value-border" style="border-bottom:1px solid #e9e9e9;">'\
                                                '<div class="flex__item text-right" style="margin-right:2px;">'+str(propData.get("Min","-"))+' A</div>'\
                                            '</div>'\
                                        '</div>'\
                                        '<div class="flex flex--col flex__item" style="">'\
                                            '<div class="flex flex__item flex--middle margin--left">'\
                                                '<div class="flex__item text-left" style="margin-left:10px;color:white;">Quantity</div>'\
                                            '</div>'\
                                            '<div class="flex flex__item flex--middle flex--right text-large margin--right overview-value-border" style="">'\
                                                '<div class="flex__item text-right" style="margin-right:10px;color:white;">'+str(propData.get("MaxTime","-"))+'</div>'\
                                            '</div>'\
                                            '<div class="flex flex__item flex--middle flex--right text-large margin--right overview-value-border">'\
                                                '<div class="flex__item text-right" style="margin-right:10px;color:white;">'+str(propData.get("MaxTime","-"))+'</div>'\
                                            '</div>'\
                                            '<div class="flex flex__item flex--middle flex--right text-large margin--right overview-value-border" style="border-bottom:1px solid #e9e9e9;">'\
                                                '<div class="flex__item text-right" style="margin-right:10px;color:white;">'+str(propData.get("MinTime","-"))+'</div>'\
                                            '</div>'\
                                            '<div class="flex flex__item flex--middle margin--left margin--top">'\
                                                '<div class="flex__item text-left" style="margin-left:10px;color:white;">Current</div>'\
                                            '</div>'\
                                            '<div class="flex flex__item flex--middle flex--right text-large margin--right overview-value-border">'\
                                                '<div class="flex__item text-right" style="margin-right:10px;color:white;">'+str(propData.get("CurrentMaxTime","-"))+'</div>'\
                                            '</div>'\
                                            '<div class="flex flex__item flex--middle flex--right text-large margin--right overview-value-border">'\
                                                '<div class="flex__item text-right" style="margin-right:10px;">'+str(propData.get("MaxTime","-"))+'</div>'\
                                            '</div>'\
                                            '<div class="flex flex__item flex--middle flex--right text-large margin--right overview-value-border" style="border-bottom:1px solid #e9e9e9;">'\
                                                '<div class="flex__item text-right" style="margin-right:10px;">'+str(propData.get("MinTime","-"))+'</div>'\
                                            '</div>'\
                                        '</div>'\
                                    '</div>'\
                                '</div>'\
                                '<div class="flex flex--col flex__item__3 custom-holder-2" style="width:70%;">'\
                                    '<div class="flex flex--row flex--middle cnt-sub-2" style="height:25px; width:100%;">'\
                                        '<div class="hdr-txt3 pointer" style="margin-left:1rem;padding-left: 1rem;padding-right:1rem;">Trend</div>'\
                                    '</div>'\
                                    '<div class="flex flex__item" style="margin:10px;width:100%;">'\
                                        '<img height="400" src="'+lineqtyname+'"/>'\
                                    '</div>'\
                                '</div>'\
                            '</div>'\
                            '<div class="flex flex--row flex__item">'\
                                '<div class="flex flex--col flex__item custom-holder-2" style="width:25%;">'\
                                    '<div class="flex flex--row flex--middle cnt-sub-4" style="height:25px; width:100%;">'\
                                        '<div class="hdr-txt3 pointer" style="margin-left:1rem;padding-left: 1rem;padding-right:1rem;color:white;">Summary</div>'\
                                    '</div>'\
                                    '<div class="flex flex--row flex--center flex__item margin--all">'\
                                        '<div class="flex flex--col flex__item" style="">'\
                                            '<div class="flex flex__item flex--middle margin--left" style="">'\
                                                '<div class="flex__item text-left" style="margin-left:10px;color:white;">Quantity</div>'\
                                            '</div>'\
                                            '<div class="flex flex__item flex--middle margin--left overview-header-border" style="border-color:white;">'\
                                                '<div class="flex__item text-left" style="margin-left:10px;color:white;">Total Maida</div>'\
                                            '</div>'\
                                            '<div class="flex flex__item flex--middle margin--left overview-header-border" style="border-color:white;">'\
                                                '<div class="flex__item text-left" style="margin-left:10px;color:white;">Total Cream</div>'\
                                            '</div>'\
                                            '<div class="flex flex__item flex--middle margin--left overview-header-border" style="border-color:white;">'\
                                                '<div class="flex__item text-left" style="margin-left:10px;color:white;">Throughput</div>'\
                                            '</div>'\
                                            '<div class="flex flex__item flex--middle margin--left margin--top">'\
                                                '<div class="flex__item text-left" style="margin-left:10px;color:white;">Cream Ratio</div>'\
                                            '</div>'\
                                            '<div class="flex flex__item flex--middle margin--left overview-header-border" style="border-color:white;">'\
                                                '<div class="flex__item text-left" style="margin-left:10px;color:white;">Average</div>'\
                                            '</div>'\
                                            '<div class="flex flex__item flex--middle margin--left overview-header-border" style="border-color:white;">'\
                                                '<div class="flex__item text-left" style="margin-left:10px;color:white;">Max</div>'\
                                            '</div>'\
                                            '<div class="flex flex__item flex--middle margin--left overview-header-border" style="border-color:white;">' \
                                                '<div class="flex__item text-left" style="margin-left:10px;color:white;">Min</div>'\
                                            '</div>'\
                                        '</div>'\
                                        '<div class="flex flex--col flex__item" style="">'\
                                            '<div class="flex flex__item flex--middle margin--left">'\
                                                '<div class="flex__item text-left" style="margin-left:10px;color:white;">Quantity</div>'\
                                            '</div>'\
                                            '<div class="flex flex__item flex--middle flex--right text-large overview-value-border" style="border-color:white;">'\
                                                '<div class="flex__item text-right" style="margin-right:2px;color:white;">'+str(propData.get("TotalMaida","-"))+' Kg</div>'\
                                            '</div>'\
                                            '<div class="flex flex__item flex--middle flex--right text-large overview-value-border" style="border-color:white;">'\
                                                '<div class="flex__item text-right" style="margin-right:2px;color:white;">'+str(propData.get("TotalCream","-"))+' Kg</div>'\
                                            '</div>'\
                                            '<div class="flex flex__item flex--middle flex--right text-large overview-value-border" style="border-color:white;">'\
                                                '<div class="flex__item text-right" style="margin-right:2px;color:white;">'+str(propData.get("Throughput","-"))+' Kg</div>'\
                                            '</div>'\
                                            '<div class="flex flex__item flex--middle margin--left margin--top">'\
                                                '<div class="flex__item text-left" style="margin-left:10px;color:white;">Current</div>'\
                                            '</div>'\
                                            '<div class="flex flex__item flex--middle flex--right text-large overview-value-border" style="border-color:white;">'\
                                                '<div class="flex__item text-right" style="margin-right:2px;color:white;">'+str(propData.get("Average","-"))+' A</div>'\
                                            '</div>'\
                                            '<div class="flex flex__item flex--middle flex--right text-large overview-value-border" style="border-color:white;">'\
                                                '<div class="flex__item text-right" style="margin-right:2px;color:white;">'+str(propData.get("Max","-"))+' A</div>'\
                                            '</div>'\
                                            '<div class="flex flex__item flex--middle flex--right text-large overview-value-border" style="border-color:white;">'\
                                                '<div class="flex__item text-right" style="margin-right:2px;color:white;">'+str(propData.get("Min","-"))+' A</div>'\
                                            '</div>'\
                                        '</div>'\
                                        '<div class="flex flex--col flex__item" style="">'\
                                            '<div class="flex flex__item flex--middle margin--left">'\
                                                '<div class="flex__item text-left" style="margin-left:10px;color:white;">Quantity</div>'\
                                            '</div>'\
                                            '<div class="flex flex__item flex--middle flex--right text-large margin--right overview-value-border" style="border-color:white;">'\
                                                '<div class="flex__item text-right" style="margin-right:10px;color:white;">'+str(propData.get("MaxTime","-"))+'</div>'\
                                            '</div>'\
                                            '<div class="flex flex__item flex--middle flex--right text-large margin--right overview-value-border" style="border-color:white;">'\
                                                '<div class="flex__item text-right" style="margin-right:10px;color:white;">'+str(propData.get("MaxTime","-"))+'</div>'\
                                            '</div>'\
                                            '<div class="flex flex__item flex--middle flex--right text-large margin--right overview-value-border" style="border-color:white;">'\
                                                '<div class="flex__item text-right" style="margin-right:10px;color:white;">'+str(propData.get("MinTime","-"))+'</div>'\
                                            '</div>'\
                                            '<div class="flex flex__item flex--middle margin--left margin--top">'\
                                                '<div class="flex__item text-left" style="margin-left:10px;color:white;">Current</div>'\
                                            '</div>'\
                                            '<div class="flex flex__item flex--middle flex--right text-large margin--right overview-value-border" style="border-color:white;">'\
                                                '<div class="flex__item text-right" style="margin-right:10px;color:white;">'+str(propData.get("CurrentMaxTime","-"))+'</div>'\
                                            '</div>'\
                                            '<div class="flex flex__item flex--middle flex--right text-large margin--right overview-value-border" style="border-color:white;">'\
                                                '<div class="flex__item text-right" style="margin-right:10px;color:white;">'+str(propData.get("MaxTime","-"))+'</div>'\
                                            '</div>'\
                                            '<div class="flex flex__item flex--middle flex--right text-large margin--right overview-value-border" style="border-color:white;">'\
                                                '<div class="flex__item text-right" style="margin-right:10px;color:white;">'+str(propData.get("MinTime","-"))+'</div>'\
                                            '</div>'\
                                        '</div>'\
                                    '</div>'\
                                '</div>'\
                                '<div class="flex flex--col flex__item__3 custom-holder-2" style="width:70%;">'\
                                    '<div class="flex flex--row flex--middle cnt-sub-2" style="height:25px; width:100%;">'\
                                        '<div class="hdr-txt3 pointer" style="margin-left:1rem;padding-left: 1rem;padding-right:1rem;">Trend</div>'\
                                    '</div>'\
                                    '<div class="flex flex__item" style="margin:10px;width:100%;">'\
                                        '<img height="400" src="'+linerationame+'"/>'\
                                    '</div>'\
                                '</div>'\
                            '</div>'\
                        '</div>'\
                    '</div>'
                index += 1
                imagesToDelete.append(lineqtyname)
                imagesToDelete.append(linerationame)
                if index % 2 == 0: 
                    ht += '</div>'
                    self.to_html_pretty_2(ht, intermediate_html, prop, htmlToAdd, "CMS Daily Report", selectedDate)
                    htmlToAdd = ""
                elif index >= len(self.reportKeys) and index % 2 != 0:
                    ht += '</div>'
                    self.to_html_pretty_2(ht, intermediate_html, prop, htmlToAdd, "CMS Daily Report", selectedDate)
                    htmlToAdd = ""
            # return jsonify(Results=out_result)
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

    def save_cms_home(self, dateparam):
        # self.log.info("Saving Dashboard Report...CMS")
        filename = self.get_cms_home(dateparam)
        path = FILE_PATH
        uuidstr = str(uuid.uuid4())
        filepath = filename

        return filepath

    def save_cms_report(self, dateparam):
        #print "Saving Report..."
        out_list = self.get_cms_report(dateparam)
        filename = self.downloadCMSReport(out_list, dateparam)
        path = FILE_PATH
        uuidstr = str(uuid.uuid4())
        filepath = filename

        #zip_name = "CMS_Reports_"+uuidstr+".zip"
        #zip_file = path + zip_name
        #print 'Creating archive ' + zip_name
        #zf = zipfile.ZipFile(zip_file, mode='w')
        #compression = zipfile.ZIP_DEFLATED

        #zf.write(filepath, os.path.basename(filepath), compress_type=compression)
        return filepath

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
    dbCMSManager = CMSRun()
    dbCMSManager.get_today_records("2019-07-13")
    moulder_report = dbCMSManager.save_cms_home("2019-07-13")