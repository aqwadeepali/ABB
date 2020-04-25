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
import copy

import logging
import logging.config
from logging import getLogger, INFO, ERROR, WARNING, CRITICAL, NOTSET, DEBUG, Formatter
from concurrent_log_handler import ConcurrentRotatingFileHandler

# path_wkthmltopdf = r'C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe'
# config = pdfkit.configuration(wkhtmltopdf=path_wkthmltopdf)

CONFIG_PATH = str(os.path.realpath(__file__))
CONFIG_PATH = CONFIG_PATH.replace("stage_bori_data.pyc", "")
CONFIG_PATH = CONFIG_PATH.replace("stage_bori_data.pyo", "")
CONFIG_PATH = CONFIG_PATH.replace("stage_bori_data.py", "")
CONFIG_PATH = CONFIG_PATH + "data/"

FILE_PATH = str(os.path.realpath(__file__))
FILE_PATH = FILE_PATH.replace("stage_bori_data.pyc", "")
FILE_PATH = FILE_PATH.replace("stage_bori_data.pyo", "")
FILE_PATH = FILE_PATH.replace("stage_bori_data.py", "")
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


HTML_TEMPLATE2 = '</body></html>'

class BRun():
    def __init__(self):
        
        self.collection = ""
        self.properties = ""
        self.reportKeys = []
        self.reportManager = {}
        self.log = getLogger()
        self.read_settings()

        self._date = "";
        self.all_dates = [];

        self.log.info('Reading Params....Bori')
        self.log.info('File Ready to Use...Bori')

    def read_settings(self):
        self.log.info("Reading Settings...Bori")
        all_json = ""
        all_keys = ""
        keys = ""
        collection = ""
        reportKeys = ""
        reportManager = ""
        keys = ""
        reader = csv.DictReader(open(CONFIG_PATH + 'stage_bori_settings.txt'), delimiter="\t")
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
        self.log.info("Bori dateparam: %s", dateparam)
        yesterdayDate = datetime.strptime(dateparam, '%Y-%m-%d')
        _date2460 = yesterdayDate + timedelta(minutes = (24*60))
        todayDate = _date2460.strftime('%Y-%m-%d')
        selectedDate = yesterdayDate.strftime("%Y-%m-%d")
        _dict = {}
        target_dict = {}
        
        connection = MongoClient('127.0.0.1', username="admin", password="admin123", authSource='analyse_db', authMechanism='SCRAM-SHA-1')
        myDb = connection["analyse_db"]
        db = myDb[self.collection]
        dbresult = []
        if dateparam == "":
            dbresult = db.find()
        else:
            to_find = dateparam 
            ls_date = str(todayDate)+" 05:59:00"
            gt_date = str(selectedDate)+" 06:00:00"

            lt_tm = time.mktime(datetime.strptime(ls_date,'%Y-%m-%d %H:%M:%S').timetuple())
            gt_tm = time.mktime(datetime.strptime(gt_date,'%Y-%m-%d %H:%M:%S').timetuple())
            to_find = {"$gte": gt_tm, "$lte": lt_tm }
            #print to_find
            dbresult = db.find({self.config["time_stamp"]:to_find}) 
            
        for prop in self.properties:
            _dict.setdefault(prop, {})
            target_dict.setdefault(prop, {})
        fbactual = 0
        fbset = 0
        allTime = []

        for row in dbresult:

            for prop in self.properties:
                keyprop = prop.lower().replace(' ', '_')
                
                bool_value = elib.tonum(row[self.config[keyprop+'_bool']], 'int')
                if bool_value == 1:
                    xfbtime = row[self.config["time"]]
                    fbtime = xfbtime.strftime('%Y-%m-%d %H:%M:%S')
                    
                    self._date = xfbtime.strftime("%Y-%m-%d")

                    fbcount_key = str(self.config['batch_count'])
                    fbset_key = str(self.config[keyprop+'_set'])
                    fbactualweight_key = str(self.config[keyprop+'_act'])

                    fbcount = elib.tonum(row.get(fbcount_key, -1), 'int') if row.get(fbcount_key, "") != "" else -1
                    fbset = elib.tonum(row.get(fbset_key, 0))
                    fbactualweight = elib.tonum(row.get(fbactualweight_key, 0))

                    if fbcount not in _dict[prop].keys():
                        _dict[prop].setdefault(fbcount, {}).setdefault("Set", [])
                        _dict[prop].setdefault(fbcount, {}).setdefault("ActualWeight", [])
                        _dict[prop].setdefault(fbcount, {}).setdefault("Time", [])
                        _dict[prop].setdefault(fbcount, {}).setdefault("Batch", "")
                    _dict[prop][fbcount]["Set"].append(fbset)
                    _dict[prop][fbcount]["ActualWeight"].append(fbactualweight)
                    _dict[prop][fbcount]["Time"].append(fbtime)
                    _dict[prop][fbcount][fbtime] = {
                        "Time": fbtime,
                        "ActualWeight": fbactualweight,
                        "Set": fbset,
                        "Batch": fbcount
                    }
                    _dict[prop][fbcount]["Batch"] = fbcount
                    allTime.append(fbtime)
        
        return _dict

    def get_today_records(self, dateparam = ""):
        self.log.info("Data Push Started...Bori")
        # dateparam = "2018-11-01"
        target_dict = self.read_from_db(dateparam)
        # print target_dict
        connection = MongoClient('127.0.0.1', username="admin", password="admin123", authSource='analyse_db', authMechanism='SCRAM-SHA-1')
        self._date = dateparam
        self.log.info("Bori self._date: %s", self._date)
        myDb = connection['analyse_db']
        dbData = []
        for prop in target_dict:
            # print prop,'---', target_dict[prop]
            # print "==================================================="
            for key in sorted(target_dict[prop].keys()):
                if target_dict[prop][key] not in ["", None, []]:
                     row = {}
                     row = target_dict[prop][key]
                     row.setdefault("asofdate", self._date)
                     row.setdefault("Prop", prop)
                     dbData.append(row)

        if dbData != []:
            myDb["bori_staging"].remove({'asofdate':self._date})
            record_id = myDb["bori_staging"].insert_many(dbData)
            self.log.info('Bori %s records found', str(len(dbData)))
            self.log.info("DB Push Completed...Bori")
        else:
            self.log.info("No Data...Bori")

    def find2ndMax(self, _list, lastMax):
        maxNum = _list[0]
        secondMax = ""
        for item in _list:
            if item != lastMax:
                if maxNum < item:
                    secondMax = copy.deepcopy(maxNum)
                    maxNum = item
        return maxNum


    def get_bori_report(self, dateparam):
        result = False
        selectedDate = dateparam
        yesterdayDate = datetime.strptime(dateparam, '%Y-%m-%d')
        _date2460 = yesterdayDate + timedelta(minutes = (24*60))
        todayDate = _date2460.strftime('%Y-%m-%d')
        selectedDate = yesterdayDate.strftime("%Y-%m-%d")

        selectedDateTime = selectedDate + " 06:00"
        todayDateTime = todayDate + " 05:59"
        timerange = []
        timerange.append(selectedDateTime)
        while selectedDateTime != todayDateTime:
            _date = datetime.strptime(selectedDateTime, '%Y-%m-%d %H:%M')
            _date_60 = _date + timedelta(minutes = 1)
            selectedDateTime = _date_60.strftime('%Y-%m-%d %H:%M')
            timerange.append(selectedDateTime)
        timerange = sorted(timerange)
        # print timerange
        out_result = []
        footer_data = {}
        allTotalFinal = 0
        _dict = {}

        find_dict = {"asofdate":selectedDate}
        
        connection = MongoClient('127.0.0.1', username="admin", password="admin123", authSource='analyse_db', authMechanism='SCRAM-SHA-1')

        #myDb = connection["abb"]
        myDb = connection["analyse_db"]
        db = myDb["bori_staging_lineB"]

        item_count = db.count_documents(find_dict)
        if item_count == 0:
            self.log.info("Data not available in staging... Getting From Mains...Bori")
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
            all_result = {}
            line_result = []
            finalValue = 0
            allTotalFinal = 0
            for prop in self.reportKeys:
                stage_data = _dict.get(prop, {})
                if stage_data != {}:
                    initialValue = 0
                    totalFinal = 0
                    new_stage_data = sorted(stage_data, key=lambda k: k['Time'])
                    loopCount = 0
                    for node in new_stage_data:
                        row = {}
                        if node["Batch"] != -1:
                            # print node["Time"],'---', node["Batch"], '---', node["ActualWeight"]
                            maxActual = max(node.get("ActualWeight", [0]))
                            maxSet = max(node.get("Set", [0]))
                            maxTime = max(node.get("Time", [""]))

                            maxIndex = node["Time"].index(maxTime) if node.get("Time", [""]) != [""] else -1
                            if maxIndex != -1:
                                batch = node["Batch"]
                                setValue = maxSet
                                realValue = node[maxTime]["ActualWeight"]
                                val = realValue - initialValue
                                newMaxTime = copy.deepcopy(maxTime)
                                
                                timeLength = len(node.get("Time", [""]))
                                # print batch, '---', setValue,'---', initialValue,'---', realValue,'---', val,'---', timeLength
                                if loopCount in [0, '0']:
                                    val = 0
                                if val < 0:
                                    initialValue = 0
                                    val = 0#realValue - initialValue

                                finalValue = copy.deepcopy(val)
                                totalFinal += finalValue
                                allTotalFinal += finalValue

                                elib.dictIncrement3D(all_result, newMaxTime, batch, prop+"_Set", setValue)
                                elib.dictIncrement3D(all_result, newMaxTime, batch, prop+"_Initial", initialValue)
                                elib.dictIncrement3D(all_result, newMaxTime, batch, prop+"_Actual", realValue)
                                elib.dictIncrement3D(all_result, newMaxTime, batch, prop+"_Final", finalValue)
                                elib.dictIncrement3D(all_result, newMaxTime, batch, prop+"_Time", maxTime)
                                realValue = copy.deepcopy(node[maxTime]["ActualWeight"])
                                initialValue = copy.deepcopy(realValue)
                                loopCount += 1
                    footer_data.setdefault(prop+"_Total", elib.tonum(totalFinal,'int'))

            for tm in sorted(all_result.keys()):
                for bt in sorted(all_result[tm].keys()):
                    row = {}
                    row.setdefault("Batch", bt)
                    row.setdefault("Time", tm)
                    for prop in self.reportKeys:
                        row.setdefault(prop+"_Set", elib.tonum(all_result[tm][bt].get(prop+"_Set", 0),'int'))
                        row.setdefault(prop+"_Initial", elib.tonum(all_result[tm][bt].get(prop+"_Initial", 0),'int'))
                        row.setdefault(prop+"_Actual", elib.tonum(all_result[tm][bt].get(prop+"_Actual", 0),'int'))
                        row.setdefault(prop+"_Final", elib.tonum(all_result[tm][bt].get(prop+"_Final", 0),'int'))
                    out_result.append(row)

            # path = "trialText.txt"
            # with open(path, 'wb') as f:
            #     w = csv.DictWriter(f, out_result[0].keys(), dialect = "excel-tab")
            #     w.writeheader()
            #     w.writerows(out_result)
            # print out_result
        return {"data": out_result, "footer_data": footer_data, "allTotal": allTotalFinal}

    def downloadBoriReport(self, out_data, dateparam):
        yesterdayDate = datetime.strptime(dateparam, '%Y-%m-%d')
        _date2460 = yesterdayDate + timedelta(minutes = (24*60))
        todayDate = _date2460.strftime('%Y-%m-%d')
        selectedDate = yesterdayDate.strftime("%Y-%m-%d")

        fileCompleted = []
        all_rows = []
        subheaders = ["Set", "Actual", "Final"]
        headkeys = ["Set", "Actual", "Final"]
        headers =  []
        keyheaders = ["Batch", "Time"]

        for mode in self.reportKeys:
            for node in subheaders:
                headers.append(node)
                keyheaders.append(mode.lower().replace(" ", "_") + "_" + headkeys[subheaders.index(node)])

        hpstack = []
        hpstack.append({"rowspan":2, "colspan":1, "name": "Batch"})
        hpstack.append({"rowspan":2, "colspan":1, "name": "Time"})
        for prop in self.reportKeys:
            hpstack.append({"rowspan":1, "colspan":3, "name": prop })

        ht = ''
        ht += '<table><thead><tr><th style=""></th>'
        for hd in hpstack:
            if hd["name"] in ["Batch", "Time"]:
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
        
        out_report = out_data["data"]
        for node in out_report:
            rowcnt += 1
            ht += '<tr style="text-align: right;">'
            ht += '<td style="">'+str(rowcnt)+'</td>'
            for key in keyheaders:
                ht += '<td style="">'+str(node.get(key,"-"))+'</td>'

        rowcnt += 1
        footer_data = out_data["footer_data"]
        ht += '<tr style="text-align: right;">'
        ht += '<td style="">'+str(rowcnt)+'</td>'
        ht += '<td colspan="2" style="">Total All: '+str(elib.tonum(out_data["allTotal"],'int'))+'</td>'
        for prop in self.reportKeys:
            ht += '<td colspan="3" style="">Total: '+str(footer_data.get(prop+"_Total",0))+'</td>'

        ht += '</tbody></table>'

        out_pdf= FILE_PATH + 'Bori_Report_'+selectedDate+'.pdf'
        intermediate_html = FILE_PATH + 'intermediate.html'
        reportTitle = "Bori Daily Report"

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
        self.to_html_pretty_report(ht, intermediate_html, "Bori Daily Report", htmlToAdd, reportTitle, selectedDate)
        htmlToAdd = ""
        # options = {'orientation': 'Landscape'}
        # pdfkit.from_file(intermediate_html, out_pdf, configuration=config)
        pdfkit.from_file(intermediate_html, out_pdf)
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

    def save_bori_report(self, dateparam):
        self.log.info("Saving Report...Bori")
        out_list = self.get_bori_report(dateparam)
        filename = self.downloadBoriReport(out_list, dateparam)
        path = FILE_PATH
        uuidstr = str(uuid.uuid4())
        filepath = filename

        return filepath

if __name__ == "__main__":
    dbBoriManager = BRun()
    dbBoriManager.get_today_records("2019-03-23")
    bori_report = dbBoriManager.save_bori_report("2019-03-23")
    # downtime_report = dbBoriManager.save_bori_report("2019-03-08")