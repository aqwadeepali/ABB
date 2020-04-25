import os, sys, csv, time
import elib
import datetime
import time
import ast
import json
from datetime import timedelta
from stage_model import ReaderBase
from time import strftime
from pymongo import MongoClient
import pandas as pd
import pdfkit
import uuid
import zipfile
import re
from decimal import Decimal
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
CONFIG_PATH = CONFIG_PATH.replace("stage_data.pyc", "")
CONFIG_PATH = CONFIG_PATH.replace("stage_data.pyo", "")
CONFIG_PATH = CONFIG_PATH.replace("stage_data.py", "")
CONFIG_PATH = CONFIG_PATH + "data/"

FILE_PATH = str(os.path.realpath(__file__))
FILE_PATH = FILE_PATH.replace("stage_data.pyc", "")
FILE_PATH = FILE_PATH.replace("stage_data.pyo", "")
FILE_PATH = FILE_PATH.replace("stage_data.py", "")
FILE_PATH = FILE_PATH.replace("classes", "")
FILE_PATH = FILE_PATH + "dbpush/data/"

TWOPLACES = Decimal(10) ** -2

HTML_TEMPLATE1 = '<html><head><style>'\
  'h1 {text-align: center;font-family: Helvetica, Arial, sans-serif; page-break-before: always;}'\
  'h2 {text-align: center;font-family: Helvetica, Arial, sans-serif;}'\
  'h3 {text-align: center;font-family: Helvetica, Arial, sans-serif;}'\
  'table { margin-left: auto;margin-right: auto;}'\
  'table, th, td {border: 1px solid black;border-collapse: collapse;}'\
  'th {padding: 3px;text-align: center;font-family: Helvetica, Arial, sans-serif;font-size: 85%;background-color:#ACD7E3}'\
  'td {padding: 3px;text-align: center;font-family: Helvetica, Arial, sans-serif;font-size: 80%;}'\
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

class Run():
    def __init__(self):

        # if keys=="":
        #     args = sys.argv[1:]
        #     keys = "Flour,G Sugar,Salt,SBC,Vitamin,Calcium,ABC,Lecithin,GMS,SMP,Milk,Syrup,Vannila,Flavour,FFM,Water,Biscuit Dust,Sugar,Cream,Palm Oil"
        
        self.collection = ""
        self.properties = ""
        self.reportKeys = []
        self.reportManager = {}
        self.recipeKeys = []
        self.recipeNames = {}
        self.log = getLogger()
        self.read_settings()

        self._date = "";
        self.all_dates = [];

        self.log.info('Reading Params....Mixing')
        self.log.info('File Ready to Use...Mixing')

    def read_settings(self, rec_key="1"):
        self.log.info("Reading Settings...Mixing")
        all_json = ""
        all_keys = ""
        keys = ""
        collection = ""
        reportKeys = ""
        reportManager = ""
        keys = ""
        recipeKeys = ""
        setdata = ""
        recipeNames = ""
        reader = csv.DictReader(open(CONFIG_PATH + 'stage_settings.txt'), delimiter="\t")
        for row in reader:
            if rec_key == "0":
                if row["Field"] == "RECIPE":
                    recipeKeys = ast.literal_eval(row["Value"])
                if row["Field"] == "RECIPENAME":
                    recipeNames = ast.literal_eval(row["Value"])
            else:
                if row["Field"] == "JSON_"+rec_key:
                    all_json = ast.literal_eval(elib.trim(row["Value"]))
                if row["Field"] == "KEYS_"+rec_key:
                    all_keys = ast.literal_eval(row["Value"])
                if row["Field"] == "COLLECTION":
                    collection = row["Value"]
                if row["Field"] == "REPORTKEYS_"+rec_key:
                    reportKeys = ast.literal_eval(row["Value"])
                if row["Field"] == "REPORTMNG_"+rec_key:
                    reportManager = ast.literal_eval(row["Value"])
                if row["Field"] == "SEQ_"+rec_key:
                    keys = row["Value"]
                if row["Field"] == "RECIPE":
                    recipeKeys = ast.literal_eval(row["Value"])
                if row["Field"] == "RECIPENAME":
                    recipeNames = ast.literal_eval(row["Value"])
                if row["Field"] == "SETDATA":
                    setdata = ast.literal_eval(row["Value"])
            
 
        self.readerconfig = ReaderBase()
        # self.properties = self.readerconfig.kpis(all_keys)
        self.config = self.readerconfig.toKeyJSON(all_json)
        self.collection = collection
        self.keys = keys
        self.properties = keys.split(",")
        self.reportManager = reportManager
        self.reportKeys = reportKeys
        self.setdata = setdata
        # self.recipeKeys = recipeKeys
        # self.recipeNames = recipeNames

    def get_today_records(self, dateparam = ""):
        self.log.info("Data Push Started...Mixing")
        self.read_settings()
        connection = MongoClient('127.0.0.1', username="admin", password="admin123", authSource='analyse_db', authMechanism='SCRAM-SHA-1')
        myDb = connection["analyse_db"]
        rec_key = "1"
        # for rec_key in self.recipeKeys:
        self.read_settings(rec_key)
        #print rec_key,"------", dateparam
        target_dict = self.read_from_db(dateparam, rec_key)
        self._date = dateparam
        self.log.info("Mixing self._date: %s", self._date)
        # mydb = client['analyse_db']
        dbData = []
        for prop in target_dict:
            # print prop
            times = []
            for key in target_dict[prop]:
                row = {}
                row = target_dict[prop][key]
                times.append(row["AvgDuration"])
            atimes = list(set(times))
            atimes_len = len(atimes) if len(atimes) else 1
            avg_duration = str(timedelta(seconds=sum(map(lambda f: int(f[0])*3600 + int(f[1])*60 + int(f[2]), map(lambda f: f.split(':'), atimes)))/atimes_len))
            for key in target_dict[prop]:
                if target_dict[prop][key] not in ["", None, []]:
                    row = {}
                    row = target_dict[prop][key]
                    row.setdefault("Prop", prop)
                    row.setdefault("AvgTimeDuration", avg_duration)
                    row.setdefault("asofdate", self._date)
                    dbData.append(row)
        if dbData != []:
            myDb["mixing_staging_lineA_"+rec_key].remove({'asofdate':self._date})
            #record_id = myDb["staging"].update(_to_push, { "$set" : _to_push}, upsert=True)
            record_id = myDb["mixing_staging_lineA_"+rec_key].insert_many(dbData)
        print 'Mixing %s records found', str(len(dbData))
        self.log.info('Mixing %s records found', str(len(dbData)))
        self.log.info("DB Push Completed...Mixing")

    def read_from_db(self, dateparam = "", recipeKey = "1"):
        self.log.info("Mixing dateparam: %s", dateparam)
        _dict = {}
        target_dict = {}
        
        connection = MongoClient('127.0.0.1', username="admin", password="admin123", authSource='analyse_db', authMechanism='SCRAM-SHA-1')
        myDb = connection["analyse_db"]
        db = myDb[self.collection]
        dbresult = []
        if dateparam == "":
            dbresult = db.find()
        else:
            yesterdayDate = datetime.datetime.strptime(dateparam, '%Y-%m-%d')
            _date2460 = yesterdayDate + timedelta(minutes = (24*60))
            todayDate = _date2460.strftime('%Y-%m-%d')
            selectedDate = yesterdayDate.strftime("%Y-%m-%d")

            to_find = dateparam #"$lt" : new ISODate("2019-01-27T23:59:00.000Z")
            ls_date = todayDate+" 06:29:00"
            gt_date = selectedDate+" 06:32:00"

            lt_tm = time.mktime(datetime.datetime.strptime(ls_date,'%Y-%m-%d %H:%M:%S').timetuple())
            gt_tm = time.mktime(datetime.datetime.strptime(gt_date,'%Y-%m-%d %H:%M:%S').timetuple())
            to_find = {"$gte": gt_tm, "$lte": lt_tm }
            dbresult = db.find({self.config["time_stamp"]:to_find}) #, self.config["recipe_no"]: elib.tonum(recipeKey,"int")})
            
        for prop in self.properties:
            _dict.setdefault(prop, {})
            target_dict.setdefault(prop, {})

        for row in dbresult:
            
            for prop in self.properties:  
                keyprop = prop.lower().replace(' ', '_')
                fbtime = row[self.config["time"]]
                # print fbtime
                #self._date = fbtime.strftime("%Y-%m-%d")

                fbcount_key = str(self.config[keyprop+'_batch_count'])
                fbset_key = str(self.config[keyprop+'_batch_set_weight'])
                fbactualweight_key = str(self.config[keyprop+'_actual_weight'])
                
                fbcount = row.get(fbcount_key, 0)
                fbset = elib.tonum(row.get(fbset_key, 0))
                fbactualweight = elib.tonum(row.get(fbactualweight_key, 0))
                
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
                    # print prop,'---',date2,'---',date1,'---',datetime.datetime.strptime(str(date1), datetimeFormat)
                    diff = datetime.datetime.strptime(str(date1), datetimeFormat) - datetime.datetime.strptime(str(date2), datetimeFormat)
                    avg_duration = str(diff)
                    
                    deviation = 0
                    total_set = max(_dict[prop][key]["Set"])
                    total_actual = max(_dict[prop][key]["ActualWeight"])
                    deviation = total_set - total_actual
                    if deviation < 0:
                        deviation = deviation * -1
                    
                    avg_deviation = deviation / total_batches

                    percent_deviation = deviation
                    if total_set > 0:
                        percent_deviation = (deviation / total_set) * 100

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
                    target_dict[prop][str(key)].setdefault("PercentDeviation", percent_deviation)
                    target_dict[prop][str(key)].setdefault("AvgDeviation", elib.rnd(avg_deviation, 2))
                    target_dict[prop][str(key)].setdefault("TargetAchieved", target_achieved)
                    target_dict[prop][str(key)].setdefault("TargetMissed", target_missed)
                    target_dict[prop][str(key)].setdefault("MaxTime", date1.strftime('%Y-%m-%d %H:%M:%S'))
                    target_dict[prop][str(key)].setdefault("MinTime", date2.strftime('%Y-%m-%d %H:%M:%S'))
                    # print prop, '---', str(key), '---', target_dict[prop][str(key)]
                except Exception as e:
                    print e
        
        return target_dict

    def read_and_download_report(self, _date):
        self.read_settings()
        filepaths = []
        rec_key = "1"
        # for rec_key in self.recipeKeys:
        self.read_settings(rec_key)
        out_list = self.get_report_list(_date, rec_key)
        filename = self.download_stage_report(out_list, _date, rec_key)
        path = FILE_PATH
        uuidstr = str(uuid.uuid4())
        filepaths.append(filename)

        return filepaths
    
    def read_and_download_home(self, _date):
        filepaths = []
        self.read_settings()
        rec_key = "1"
        # for rec_key in self.recipeKeys:
        self.read_settings(rec_key)
        filename = self.get_home(_date, rec_key)
        path = FILE_PATH
        uuidstr = str(uuid.uuid4())
        filepaths.append(filename)

        return filepaths
        
    def createHeaders(self, _list, prop):
        resultHeader = []
        results = ""

        for key in _list:
            s = ""
            s = key + prop
            resultHeader.append(s)
        results = elib.list2string("\t",resultHeader)

        return results

    def to_html_pretty(self, df, filename='out.html', title='', subtitle='', htmlToAdd='', reportTitle = '', selectedDate=''):
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
        if subtitle != '':
            ht += '<h3> %s </h3>\n' % subtitle
        ht += df

        with open(filename, 'a') as f:
             f.write(HTML_TEMPLATE1 + ht + HTML_TEMPLATE2)

    def download_stage_report(self, out_list, _date, rec_key):
        selectedDate = _date
        reportTitle = "Mixing - Report" #+self.recipeNames[rec_key]

        reportHeader = ["Time", "BatchCount", "SetPoint", "ActualQty", "Deviation", "AvgDuration", "% Deviation", "SetDeviation", "SetDuration"]
        fileCompleted = []
        all_rows = []
        data_list = []
        txtfilename = FILE_PATH + "reports_all.txt"
        for node in out_list:
            headers = ["Time", "BatchCount", "TotalSetPoint", "TotalActualQty", "Deviation", "AvgDuration", "PercentDeviation", "SetDeviation", "SetDuration"]
            title = node["name"]
            txtfilename = FILE_PATH + node["name"].lower().replace(" ", "_") + ".txt"
            fileAttr = {"txt": txtfilename, "name":node["name"], "subtitle": "", "html": ""}
            first_row = []
            data_list = []
            all_rows = []
            for subnode in node["attr"]:
                s = subnode["prop"].replace(" ", "")
                first_row.append(s)
                datalist = []
                for row in subnode["data"]:
                    attr = {}
                    for hd in headers:
                        if hd == 'Time':
                            tm = row["MaxTime"].replace(" ", "&nbsp;")
                            attr.setdefault(hd, tm)
                        else:
                            attr.setdefault(hd, row[hd])
                    datalist.append(attr)
                all_rows.append(datalist)

            all_length = len(all_rows)
            if all_length == 2:
                first_list = all_rows[0]
                second_list = all_rows[1]
                big_list = second_list
                small_list = first_list

                first_len = len(first_list)
                second_len = len(second_list)

                if first_len > second_len:
                    big_list = first_list
                    small_list = second_list
                    s = "<span style='margin-right:180px;'>" + first_row[1] + "</span><span style='margin-left:220px;'>" +  first_row[0] +"</span>"
                    fileAttr["subtitle"] = s
                    data_list.append(self.createHeaders(reportHeader, "") + "\t" + self.createHeaders(reportHeader, "."))
                else:
                    s = "<span style='margin-right:180px;'>" + first_row[0] + "</span><span style='margin-left:220px;'>" +  first_row[1] +"</span>"
                    fileAttr["subtitle"] = s
                    data_list.append(self.createHeaders(reportHeader, "") + "\t" + self.createHeaders(reportHeader, "."))

                for big_row in big_list:
                    index = big_list.index(big_row)
                    s = ""
                    if index < len(small_list):
                        small_row = small_list[index]
                        for key in headers:
                            s += str(small_row[key])
                            s += "\t"
                        s += "\t" 
                    else:
                        for key in headers:
                            s += str("-")
                            s += "\t"
                        s += "\t" 
                    for key in headers:
                        s += str(big_row[key])
                        s += "\t"
                    data_list.append(s)
            else:
                fileAttr["subtitle"] = s
                data_list.append(elib.list2string("\t", reportHeader))
                for row in all_rows:
                    for subrow in row:
                        s = ""
                        for key in headers:
                            s += str(subrow[key])
                            s += "\t"
                        data_list.append(s)
            
            ht = ''
            ht += '<table><thead><tr><th style=""></th>'

            rowcnt = 0
            hdList = []
            hdList.extend(self.createHeaders(reportHeader, '').split("\t"))
            if all_length == 2:
                hdList.append("")
                hdList.extend(self.createHeaders(reportHeader, '.').split("\t"))

            for hd in hdList:
                if hd not in ["SetDeviation", "SetDeviation.", "SetDuration", "SetDuration."]:
                    ht += '<th>'+hd+'</th>'
            ht += '</tr>'
            ht += '</thead><tbody>' 
            for line in data_list:
                lineList = []
                linkedData = {}
                if rowcnt != 0: #content
                    lineList = line.split("\t")
                    for i in range(0, len(hdList)):
                        linkedData.setdefault(hdList[i], lineList[i])

                    ht += '<tr style="text-align: right;">'
                    ht += '<td style="background-color:#ddeff3">'+str(rowcnt)+'</td>'
                    for link in hdList:
                        if link not in ["SetDeviation", "SetDeviation.", "SetDuration", "SetDuration."]:
                            if link == "Deviation":
                                if linkedData["SetDeviation"] in [True, 'True']:
                                    ht += '<td style="background-color:#ffd457;">'+str(linkedData[link])+'</td>'
                                else:
                                    ht += '<td style="background-color:#ddeff3">'+str(linkedData[link])+'</td>'
                            elif link == "Deviation.":
                                if linkedData["SetDeviation."] in [True, 'True']:
                                    ht += '<td style="background-color:#ffd457;">'+str(linkedData[link])+'</td>'
                                else:
                                    ht += '<td style="background-color:#ddeff3">'+str(linkedData[link])+'</td>'
                            elif link == "AvgDuration":
                                if linkedData["SetDuration"] in [True, 'True']:
                                    ht += '<td style="background-color:#ffd457;">'+str(linkedData[link])+'</td>'
                                else:
                                    ht += '<td style="background-color:#ddeff3"">'+str(linkedData[link])+'</td>'
                            elif link == "AvgDuration.":
                                if linkedData["SetDuration."] in [True, 'True']:
                                    ht += '<td style="background-color:#ffd457;">'+str(linkedData[link])+'</td>'
                                    print 'Here...'
                                else:
                                    ht += '<td style="background-color:#ddeff3">'+str(linkedData[link])+'</td>'
                            else:
                                ht += '<td style="background-color:#ddeff3">'+str(linkedData[link])+'</td>'
                    ht += '</tr>'
                rowcnt += 1
            ht += '</tbody></table>' 

            fileAttr["html"] = ht    
            fileCompleted.append(fileAttr) 
    

        out_pdf= FILE_PATH + 'Mixing_Report'+'_'+_date+'.pdf'
        intermediate_html = FILE_PATH + 'intermediate.html'

        htmlToAdd = '<div style="margin-left:10px;margin-top:20px;text-align:center;border:1px solid white;">'\
                        '<div style="text-center:left;margin-left:1rem;margin-right:1rem;margin-top:300px;">'\
                            '<img src="' + CONFIG_PATH + 'abz2_big.png" style=""/>'\
                            '<div style="text-align:center;color:#323232;font-size:35px;margin-top:5px;">'\
                                '<span style="color:#323232;font-size:35px;margin-right:2rem;">'+reportTitle+'</span>'\
                            '</div>'\
                            '<div style="text-align:center;color:#323232;font-size:35rem;margin-top:5px;">'\
                                '<span style="color:#323232;font-size:30px;"> Generation Date ('+selectedDate+') </span>'\
                            '</div>'\
                        '</div>'\
                    '</div>'
        if os.path.exists(intermediate_html):
            os.remove(intermediate_html)
        for key in self.reportKeys:
            for fattr in fileCompleted:
                if fattr["name"] == key:
                    intermediate_html = FILE_PATH + 'intermediate.html'
                    self.to_html_pretty(fattr["html"], intermediate_html,fattr["name"], fattr["subtitle"], htmlToAdd, reportTitle, selectedDate)
                    htmlToAdd = ""
        options = {
            "orientation": "Landscape"
        }
        # pdfkit.from_file(intermediate_html, out_pdf, configuration=config, options=options)
        pdfkit.from_file(intermediate_html, out_pdf, options=options)
        return out_pdf

    def get_report_list(self, _date, rec_key):
        connection = MongoClient('127.0.0.1', username="admin", password="admin123", authSource='analyse_db', authMechanism='SCRAM-SHA-1')
        myDb = connection["analyse_db"]
        
        db = myDb["mixing_staging_lineA_"+str(rec_key)]
        find_dict = {"asofdate":_date}
        dbresult = db.find(find_dict)        

        _dict = {}
        out_list = []
        item_count = db.count_documents(find_dict)
        if item_count == 0:
            #print "Data not available in staging... Getting From Mains..."
            self.get_today_records(_date)
            find_dict = {"asofdate":_date}
            item_count = db.count_documents(find_dict)
            #print item_count

        
        if item_count > 0:
            out_list = []
            for dt in dbresult:
                if str(dt["Prop"]) not in _dict.keys():
                    _dict.setdefault(str(dt["Prop"]), [])
                _dict[str(dt["Prop"])].append(dt)

        target_dict = {}
        for prop in _dict:
            target_dict.setdefault(prop, {})
            for node in _dict[prop]:
                node["TotalActualQty"] = node["TotalActualQty"] if elib.rnd(node["TotalActualQty"], 2) < 10 and elib.rnd(node["TotalActualQty"], 2) >= 0 else node["TotalActualQty"]
                node["TotalActualQty"] = str(Decimal(str(node["TotalActualQty"])).quantize(TWOPLACES))
                node["TotalSetPoint"] = node["TotalSetPoint"] if elib.rnd(node["TotalSetPoint"], 2) < 10 and elib.rnd(node["TotalSetPoint"], 2) >= 0 else node["TotalSetPoint"]
                node["TotalSetPoint"] = str(Decimal(str(node["TotalSetPoint"])).quantize(TWOPLACES))
                node["Deviation"] = str(elib.rnd(node["Deviation"], 2)) if elib.rnd(node["Deviation"], 2) < 10 and elib.rnd(node["Deviation"], 2) >= 0 else str(elib.rnd(node["Deviation"], 2))
                node["PercentDeviation"] = str(elib.rnd(node["PercentDeviation"], 2))

                setPoint = elib.tonum(node["TotalSetPoint"])
                setPointLess = setPoint - ((setPoint * 10)/100)
                setPointMore = setPoint + ((setPoint * 10)/100)
                actual = elib.tonum(node["TotalActualQty"])
                deviation = elib.tonum(node["Deviation"])

                node["SetDuration"] = False # if datetime.strptime(str(self.setdata[prop]['duration']), "%H:%M:%S") > datetime.strptime(str(node['AvgDuration']), "%H:%M:%S") else False
                node["SetDeviation"] = False #if elib.tonum(self.setdata[prop]['deviation']) > elib.tonum(node["Deviation"]) else False
                if actual >= setPointLess and actual <= setPointMore:
                    node["SetDeviation"] = True

                batchCount = elib.tonum(node["BatchCount"], 'int')
                target_dict[prop].setdefault(batchCount, {})
                batchLabel = str(batchCount)
                if batchCount < 10:
                    batchLabel = str(batchCount)
                node["BatchCount"] = batchLabel
                target_dict[prop][batchCount] = node
                # target_dict[prop].setdefault(elib.tonum(node["BatchCount"],int), node)

        final_target = {}
        _list = []
        index = 0
        propKey = ""

        for key in self.reportKeys:
            final_target.setdefault(key, [])
            for node in self.reportManager[key]:
                prop = node["prop"]
                propid = prop.lower().replace(" ", "_")
                node["id"] = propid
                finalList = [] 

                for bt in sorted(target_dict.get(prop, {}).keys()):
                    finalList.append(target_dict[prop][bt])
                node["data"] = sorted(finalList, key = lambda i: i['MaxTime']) 
                final_target[key].append(node)

        out_list = []
        for key in self.reportKeys:
            out_list.append({
                "name": key,
                "attr" : final_target[key]
            })  

        return out_list
    
    def get_home(self, dateparam, rec_key):
        find_dict = {"asofdate":"2018-11-01"}
        result = False
        selectedDate = dateparam
        # todayDate = params.get('today', False)

        connection = MongoClient('127.0.0.1', username="admin", password="admin123", authSource='analyse_db', authMechanism='SCRAM-SHA-1')
        myDb = connection["analyse_db"]
        # myDb = connection["analyse_db"]
        db = myDb["mixing_staging_"+rec_key]

        out_result = []
        html_list = []
        _seqDict = {}

        find_dict = {"asofdate":selectedDate}
        dbresult = db.find(find_dict)
        _dict = {}
        for dt in dbresult:
            if str(dt["Prop"]) not in _dict.keys():
                _dict.setdefault(str(dt["Prop"]), [])
            _dict[str(dt["Prop"])].append(dt)

        target_dict = {}
        final_target = {}
        line_target = {}
        out_result = []
        line_cat = {}

        for prop in _dict:
            target_dict.setdefault(prop, {})
            final_target.setdefault(prop, {})
            target_dict[prop].setdefault("Batches", [])
            target_dict[prop].setdefault("Times", [])
            target_dict[prop].setdefault("LineBatch", [])
            for node in _dict[prop]:
                elib.dictIncrement(target_dict, prop, "TotalSetPoint", elib.tonum(node["TotalSetPoint"]))
                elib.dictIncrement(target_dict, prop, "TotalActualQty", elib.tonum(node["TotalActualQty"]))

                target_dict[prop]["Batches"].append(elib.tonum(node["BatchCount"],'int'))

                target_dict[prop]["LineBatch"].append({
                    "batch": elib.tonum(node["BatchCount"], 'int'),
                    "totalSetPoint": elib.tonum(node["TotalSetPoint"]),
                    "totalActualQty": elib.tonum(node["TotalActualQty"])
                })
                target_dict[prop]["Times"].append(node["AvgDuration"])

                elib.dictIncrement3D(line_target, prop, elib.tonum(node["BatchCount"], 'int'), "TotalSetPoint", elib.tonum(node["TotalSetPoint"]))
                elib.dictIncrement3D(line_target, prop, elib.tonum(node["BatchCount"], 'int'), "TotalActualQty", elib.tonum(node["TotalActualQty"]))

        for prop in target_dict:
            final_target[prop].setdefault("pie_chart", {})
            final_target[prop].setdefault("TotalActualQty", elib.rnd(target_dict[prop]["TotalActualQty"], 0))
            final_target[prop].setdefault("TotalSetPoint", elib.rnd(target_dict[prop]["TotalSetPoint"], 0))

            batches = sorted(list(set(target_dict[prop]["Batches"])))
            line_cat.setdefault(prop, batches)
            final_target[prop].setdefault("BatchCount", len(batches))

            times = list(set(target_dict[prop]["Times"]))
            avg_duration = str(timedelta(seconds=sum(map(lambda f: int(f[0])*3600 + int(f[1])*60 + int(f[2]), map(lambda f: f.split(':'), times)))/len(times)))
            final_target[prop].setdefault("AvgDuration", str(avg_duration))

            deviation = elib.tonum(target_dict[prop]["TotalSetPoint"]) - elib.tonum(target_dict[prop]["TotalActualQty"])
            if deviation < 0:
                deviation = deviation * -1
            avg_deviation = deviation / len(batches)
            final_target[prop].setdefault("Deviation", elib.rnd(deviation,0))
            final_target[prop].setdefault("AvgDeviation", elib.rnd(avg_deviation, 2))

            if elib.tonum(target_dict[prop]["TotalSetPoint"]) > 0:
                percent_deviation = (deviation / elib.tonum(target_dict[prop]["TotalSetPoint"])) * 100
            else:
                percent_deviation = deviation
            final_target[prop].setdefault("PercentDeviation", elib.rnd(percent_deviation, 2))

            if elib.tonum(target_dict[prop]["TotalSetPoint"]) > 0:
                target_acheived = elib.tonum(target_dict[prop]["TotalActualQty"]) / elib.tonum(target_dict[prop]["TotalSetPoint"])
            else:
                target_acheived = 0
            target_missed = 1 - target_acheived
            final_target[prop].setdefault("TargetAcheived", elib.rnd(target_acheived,2))
            final_target[prop].setdefault("TargetMissed", elib.rnd(target_missed,2))
        
        _seqDict = self.get_priority()      
        
        donut_color = [{
            'Target Acheived' : '#ff9933',
            'Target Missed': '#3399FF'
        }, {
            'Target Acheived' : '#7b074e',
            'Target Missed': '#077b34'
        }]


        line_color = [{
            'totalSetPoint': '#662441',
            'totalActualQty': '#e34566',
            'deviation': '#74d600'
        },{
            'totalSetPoint': '#8ABC4C',
            'totalActualQty': '#cc4680',
            'deviation': '#08c'
        }]

        donut_index = 0
        for seq in sorted(_seqDict.keys()):
            prop = _seqDict[seq]
            donut_series = []

            if donut_index == 1:
                donut_index = 0
            else:
                donut_index += 1

            donut_series.append({
                'color': donut_color[donut_index]["Target Acheived"],
                'name' : 'Target Acheived',
                'y': final_target.get(prop,{}).get("TargetAcheived",0) * 100
            })

            donut_series.append({
                'color': donut_color[donut_index]["Target Missed"],
                'name' : 'Target Missed',
                'y': final_target.get(prop,{}).get("TargetMissed",0) * 100
            })

            percentage = str(elib.rnd((final_target.get(prop,{}).get("TargetAcheived",0) * 100), 2))+ '%'
            donutChartObj = {}
            donutChartObj['id'] = 'pie_'+prop.lower().replace(' ', '_')
            donutChartObj["title"] = percentage
            donutChartObj['series'] = [{'data':donut_series, 'name':'Target '}]

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
            chart.add_data_set(donut_series, series_type='pie', name=donutChartObj["id"], size=220, innerSize=195)
            chart.save_file(FILE_PATH + donutChartObj["id"])
            html_list.append({"id": donutChartObj["id"], "type":"pie"})

            isData = False
            if len(donut_series) > 0:
                isData = True
            donutChartObj['isData'] = isData
            if prop not in final_target:
                final_target.setdefault(prop, {}).setdefault("pie_chart", {})
            final_target[prop]["pie_chart"] = donutChartObj

            legends_format = {
                'totalSetPoint':{
                    'name' : 'Total Set Point',
                    # 'color' : '#3eb308',
                    'color' : line_color[donut_index]['totalSetPoint'],
                    'dashStyle' : 'Solid',
                    'type' : 'line',
                    'y':0,
                    'visible' : True
                },
                'totalActualQty' : {
                    'name' : 'Total Actual Qty',
                    # 'color' : '#3eb308',
                    'color' : line_color[donut_index]['totalActualQty'],
                    'dashStyle' : 'Solid',
                    'type' : 'line',
                    'y':0,
                    'visible' : True
                },
                'deviation':{
                    'name': 'Deviation',
                    'color': line_color[donut_index]['deviation'],
                    'dashStyle':'Solid',
                    'type':'line',
                    'y':1,
                    'visible': True
                }
            }

            result = {}
            for leg in legends_format:
                result[leg] = {
                    'name': legends_format[leg]['name'],
                    'data': [],
                    'yAxis': legends_format[leg]['y'],
                    'type': legends_format[leg]['type'],
                    'color': legends_format[leg]['color'],
                    'visible': legends_format[leg]['visible']
                }

            xAxis = [] #sorted(list(set(target_dict[prop]["Batches"])))
            xAxis = [ x for x in line_cat.get(prop, [])]
            all_data = sorted(target_dict.get(prop,{}).get("LineBatch",[]), key=lambda k: k['batch'])
            
            for x in xAxis:
                for node in all_data:
                    if x == node["batch"]:
                        for key in legends_format:
                            if key == 'deviation':
                                deviation = elib.tonum(node["totalSetPoint"]) - elib.tonum(node["totalActualQty"])
                                if deviation < 0:
                                    deviation = deviation * -1
                                result[key]['data'].append({
                                    'category': x,
                                    'y': elib.rnd(deviation,2)
                                })
                            else:
                                result[key]['data'].append({
                                    'category': x,
                                    'y': elib.rnd(elib.tonum(node[key]),2)
                                })
                            # result[key]['data'].append([x, elib.rnd(elib.tonum(node[key]),2)])

            chartResult = []
            isData = False
            for leg in legends_format:
                if len(result[leg]['data']) > 0:
                    isData = True
                chartResult.append(result[leg])
            
            chartObj = {}
            chartObj["categories"] = xAxis
            chartObj['charttype'] = 'linechart'
            chartObj['id'] = 'line_'+prop.lower().replace(' ', '_')
            chartObj['series'] = chartResult
            chartObj['isData'] = isData

            final_target[prop]["line_chart"] = chartObj
            
            linechart = Highchart()
            lineoptions = {
                'chart': {
                    'type': 'line',
                    'height': 250,
                    'width': 850,
                    'spacingTop':10,
                    'spacingLeft':5,
                    'spacingBottom':10,
                    'spacingRight':5,
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

            out_result.append({"prop": prop, "data": final_target[prop]})

        for ht in html_list:
            self.htmltoImage(ht["id"], ht["type"])

        out_pdf= FILE_PATH + 'Mixing_Dashboard'+'_'+selectedDate+'.pdf'
        intermediate_html = FILE_PATH + 'intermediate.html'

        htmlToAdd = '<div style="margin-left:10px;margin-top:5px;text-align:center;border:1px solid white;">'\
                        '<div style="text-center:left;margin-left:1rem;margin-right:1rem;margin-top:500px;">'\
                            '<img src="' + CONFIG_PATH + 'abz2_big.png" style=""/>'\
                            '<div style="text-align:center;color:#323232;font-size:35px;margin-top:7px;">'\
                                '<span style="color:#323232;font-size:35px;margin-right:2rem;">Mixing Daily Report</span>'\
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
        for seq in sorted(_seqDict.keys()):
            prop = _seqDict[seq]
            propname = prop.lower().replace(" ", "_")
            piename = FILE_PATH + "pie_"+str(propname)+".png"
            linename = FILE_PATH + "line_"+str(propname)+".png"

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
                                        '<div class="flex flex__item flex--middle margin--left overview-header-border" style="">'\
                                            '<div class="flex__item text-left" style="margin-left:10px;">Total Set Point</div>'\
                                        '</div>'\
                                        '<div class="flex flex__item flex--middle margin--left overview-header-border">'\
                                            '<div class="flex__item text-left" style="margin-left:10px;">Total Actual Qty</div>'\
                                        '</div>'\
                                        '<div class="flex flex__item flex--middle margin--left overview-header-border">'\
                                            '<div class="flex__item text-left" style="margin-left:10px;">Deviation</div>'\
                                        '</div>'\
                                        '<div class="flex flex__item flex--middle margin--left overview-header-border">'\
                                            '<div class="flex__item text-left" style="margin-left:10px;">Avg Deviation</div>'\
                                        '</div>'\
                                        '<div class="flex flex__item flex--middle margin--left overview-header-border">'\
                                            '<div class="flex__item text-left" style="margin-left:10px;">% Deviation</div>'\
                                        '</div>'\
                                        '<div class="flex flex__item flex--middle margin--left overview-header-border">'\
                                            '<div class="flex__item text-left" style="margin-left:10px;">Batches</div>'\
                                        '</div>'\
                                        '<div class="flex flex__item flex--middle margin--left overview-header-border" style="border-bottom:1px solid #e9e9e9;">' \
                                            '<div class="flex__item text-left" style="margin-left:10px;">Avg Duration</div>'\
                                        '</div>'\
                                    '</div>'\
                                    '<div class="flex flex--col flex__item" style="">'\
                                        '<div class="flex flex__item flex--middle flex--right text-large margin--right overview-value-border" style="">'\
                                            '<div class="flex__item text-right" style="margin-right:10px;">'+str(final_target.get(prop,{}).get("TotalSetPoint", '-'))+'</div>'\
                                        '</div>'\
                                        '<div class="flex flex__item flex--middle flex--right text-large margin--right overview-value-border">'\
                                            '<div class="flex__item text-right" style="margin-right:10px;">'+str(final_target.get(prop,{}).get("TotalActualQty",'-'))+'</div>'\
                                        '</div>'\
                                        '<div class="flex flex__item flex--middle flex--right text-large margin--right overview-value-border">'\
                                            '<div class="flex__item text-right" style="margin-right:10px;">'+str(final_target.get(prop,{}).get("Deviation",'-'))+'</div>'\
                                        '</div>'\
                                        '<div class="flex flex__item flex--middle flex--right text-large margin--right overview-value-border">'\
                                            '<div class="flex__item text-right" style="margin-right:10px;">'+str(final_target.get(prop,{}).get("AvgDeviation",'-'))+'</div>'\
                                        '</div>'\
                                        '<div class="flex flex__item flex--middle flex--right text-large margin--right overview-value-border">'\
                                            '<div class="flex__item text-right" style="margin-right:10px;">'+str(final_target.get(prop,{}).get("PercentDeviation",'-'))+'</div>'\
                                        '</div>'\
                                        '<div class="flex flex__item flex--middle flex--right text-large margin--right overview-value-border">'\
                                            '<div class="flex__item text-right" style="margin-right:10px;">'+str(final_target.get(prop,{}).get("BatchCount",'-'))+'</div>'\
                                        '</div>'\
                                        '<div class="flex flex__item flex--middle flex--right text-large margin--right overview-value-border" style="border-bottom:1px solid #e9e9e9;">'\
                                            '<div class="flex__item text-right" style="margin-right:10px;">'+str(final_target.get(prop,{}).get("AvgDuration",'-'))+'</div>'\
                                        '</div>'\
                                    '</div>'\
                                '</div>'\
                            '</div>'\
                            '<div class="flex flex--col flex__item custom-holder-2" style="width:20%;">'\
                                '<div class="flex flex--row flex--middle cnt-sub-2" style="height:25px; width:100%;">'\
                                    '<div class="hdr-txt3 pointer" style="margin-left:1rem;padding-left: 1rem;padding-right:1rem;">Target Achieved</div>'\
                                '</div>'\
                                '<div class="flex flex__item" style="margin-left:30px;">'\
                                    '<img src="'+piename+'" style=""/>'\
                                '</div>'\
                            '</div>'\
                            '<div class="flex flex--col flex__item__3 custom-holder-2" style="width:70%;">'\
                                '<div class="flex flex--row flex--middle cnt-sub-2" style="height:25px; width:100%;">'\
                                    '<div class="hdr-txt3 pointer" style="margin-left:1rem;padding-left: 1rem;padding-right:1rem;">Batch(Kg) Trend</div>'\
                                '</div>'\
                                '<div class="flex flex__item" style="margin:10px;width:100%;">'\
                                    '<img height="250" src="'+linename+'"/>'\
                                '</div>'\
                            '</div>'\
                        '</div>'\
                    '</div>'\
                  '</div>'

            index += 1
            imagesToDelete.append(piename)
            imagesToDelete.append(linename)
            if index == 0 or index % 2 == 0: 
                ht += '</div>'
                self.to_html_pretty_2(ht, intermediate_html, "Mixing", htmlToAdd, "Mixing Daily Report", selectedDate)
                htmlToAdd = ""
            elif index >= len(_seqDict.keys()):
                ht += '</div>'
                self.to_html_pretty_2(ht, intermediate_html, "Mixing", htmlToAdd, "Mixing Daily Report", selectedDate)
                htmlToAdd = ""
        # options = {'orientation': 'Landscape'}
        options = {
            # "page-size": "A4",
            "orientation": "Landscape",
            # 'dpi':400
        }
        # pdfkit.from_file(intermediate_html, out_pdf, configuration=config, options=options)
        pdfkit.from_file(intermediate_html, out_pdf, options=options)
        for img in imagesToDelete:
            os.remove(img)

        return out_pdf

    def to_html_pretty_2(self, ht, filename='out.html', title='', htmlToAdd="", reportTitle = '', selectedDate=''):
        htm = ''
        if htmlToAdd != "":
            htm += htmlToAdd
        if title != '':
            htm += '<h1><div class="flex flex--col flex__item flex--center">'
            htm += '<span style="text-align:left;width:20%;"> <img src="' + CONFIG_PATH + 'abz2_small.png" align:left/></span>'
            htm += '<span style="margin-left:33rem;width:60%; text-align:center;color:#323232;">'\
                        '<span style="color:#323232;font-size:22px;">'+reportTitle+'</span>'\
                    '</span>'\
                    '<span style="margin-left:24rem;width:20%;text-align:right;color:#323232;">'\
                        '<span style="color:#323232;font-size:22px;"> Generation Date ('+selectedDate+') </span>'\
                    '</span></div></h1>'
            # htm += '<h2> %s </h2>\n' % title
        htm += ht

        with open(filename, 'a') as f:
             f.write(HTML_TEMPLATE3 + htm + HTML_TEMPLATE2)

    def get_priority(self):
        seq = self.keys.split(",")
        _seqDict = {}

        index = 1
        for x in seq:
            _seqDict.setdefault(index, x)
            index += 1
        return _seqDict

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
    dbManager = Run()
    # dbManager.get_home("2019-03-25")
    dbManager.get_today_records("2019-03-25")
    dbManager.read_and_download_report("2019-03-25")
