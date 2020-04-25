import os, json
import elib
from datetime import timedelta
from datetime import datetime
import time
from flask import jsonify, request, Response, json
from werkzeug.datastructures import Headers
import pandas as pd
import uuid
import csv
import os, json
import zipfile
import re
import pdfkit
from stage_moulder_data import MRun
import ast
import operator

import imgkit
from highcharts import Highchart

from logging import getLogger, INFO, ERROR, WARNING, CRITICAL, NOTSET, DEBUG

# path_wkthmltopdf = r'C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe'
# config = pdfkit.configuration(wkhtmltopdf=path_wkthmltopdf)

# path_wkthmltoimage = r'C:\Program Files\wkhtmltopdf\bin\wkhtmltoimage.exe'
# image_config = imgkit.config(wkhtmltoimage=path_wkthmltoimage)

SETTING_PATH = str(os.path.realpath(__file__))
SETTING_PATH = SETTING_PATH.replace("moulder_services.pyc", "")
SETTING_PATH = SETTING_PATH.replace("moulder_services.pyo", "")
SETTING_PATH = SETTING_PATH.replace("moulder_services.py", "")
SETTING_PATH = SETTING_PATH + "data/"

FILE_PATH = str(os.path.realpath(__file__))
FILE_PATH = FILE_PATH.replace("moulder_services.pyc", "")
FILE_PATH = FILE_PATH.replace("moulder_services.pyo", "")
FILE_PATH = FILE_PATH.replace("moulder_services.py", "")
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

HTML_TEMPLATE3 = '<html><head><link rel="stylesheet" type="text/css"  href="'+SETTING_PATH+'all_css.css"/><style>'\
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

def register_services(app, WSGI_PATH_PREFIX):
    MoulderServices(app, WSGI_PATH_PREFIX)

class MoulderServices:

    def __init__(self, app, API):
        self.app = app
        self.API = API
        self.dManagers = self.app.config["Managers"]["DataManager"]
        self.mongoManger = self.dManagers.get_connection()

        self.mongo = self.mongoManger["analyse_db"]
        self.log = getLogger()
        # schedule.every().day.at("20:50").do(job)
        # schedule.every(2).minutes.do(job)

        #print self.mongo.collection_names()
        #print '--------------------------------------------------------------'

        self.dbManager = MRun()
        # self.get_settings()

        # self.app.add_url_rule(API + '/services/sendfresponse', 'sendfresponse', self.sendfresponse, methods=['GET','POST'])

        # # Home API
        self.app.add_url_rule(API + '/services/getmoulderhome', 'getmoulderhome', self.get_moulder_home, methods=['POST'])
        self.app.add_url_rule(API + '/services/getmoulderreport', 'getmoulderreport', self.get_moulder_report, methods=['POST'])
        self.app.add_url_rule(API + '/services/getmoulderdowntimereport', 'getmoulderdowntimereport', self.get_moulder_downtime_report, methods=['POST'])
        self.app.add_url_rule(API + '/services/savemoulderreport', 'savemoulderreport', self.save_moulder_report, methods=['POST'])
        self.app.add_url_rule(API + '/services/savemoulderhome', 'savemoulderhome', self.save_moulder_home, methods=['POST'])
        self.app.add_url_rule(API + '/services/savemoulderdowntimereport', 'savemoulderdowntimereport', self.save_moulder_downtime_report, methods=['POST'])

    def get_settings(self):
        try:
            print "Reading Settings"
            keys = ""
            reportKeys = ""
            reportManager = ""
            reader = csv.DictReader(open(SETTING_PATH + 'moulder_settings.txt'), delimiter="\t")
            for row in reader:
                if row["Field"] == "REPORTKEYS":
                    reportKeys = ast.literal_eval(row["Value"])
                if row["Field"] == "REPORTMNG":
                    reportManager = ast.literal_eval(row["Value"])
                if row["Field"] == "SEQ":
                    keys = row["Value"]
     
            self.seqKeys = keys
            self.reportManager = reportManager
            self.reportKeys = reportKeys
        except Exception as e:
            self.log.exception("Read Settings Exception....")
            self.log.exception(e)


    def get_params(self, request):
        return request.json if (request.method == 'POST') else request.args

    # def sendfresponse(self):
    #     params = self.get_params(request)
    #     if params != False:
    #         fname = params.get('name')
    #         print FILE_PATH
    #         print fname

    #         fPath = FILE_PATH + fname

    #         file = open(fPath, 'rb').read()
    #         response = Response()
    #         response.data = file
    #         response.status_code = 200
    #         response.headers = Headers()
    #         response.headers['Pragma'] = 'public'
    #         response.headers['Expires'] = '0'
    #         response.headers['Cache-Control'] = 'public'
    #         response.headers['Content-Description'] = 'File Transfer'
    #         response.headers['Content-Type'] = 'application/octet-stream'#'text/plain' #'application/vnd.ms-excel' #'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    #         response.headers['Content-Disposition'] = 'attachment; filename='+fname
    #         response.headers['Content-Transfer-Encoding'] = 'binary'
    #         # response.headers['X-Key'] = self.KEY

    #         os.remove(fPath)

    #         return response
    #     else:
    #         return False

    def get_moulder_downtime_report(self, mode="view"):
        try:
            params = self.get_params(request)
            self.get_settings()
            result = False
            _dict = {}


            timerange = []
            _dict = {}
            out_result = []
            selectedFromDate = params.get('selectedFromDate', False)
            selectedToDate = params.get('selectedToDate', False)
            start = datetime.strptime(selectedFromDate, "%Y-%m-%d")
            end = datetime.strptime(selectedToDate, "%Y-%m-%d")
            date_generated = [start + timedelta(days=x) for x in range(0, (end-start).days + 1)]

            if selectedFromDate == selectedToDate:
                if date_generated == []:
                    date_generated = [start]

            for dateparam in date_generated:
                # dateparam = params.get('selectedDate', False)
                yesterdayDate = dateparam
                _date2460 = yesterdayDate + timedelta(minutes = (24*60))
                todayDate = _date2460.strftime('%Y-%m-%d')
                selectedDate = yesterdayDate.strftime("%Y-%m-%d")
                self.dbManager.get_today_records(selectedDate)

                selectedDateTime = selectedDate + " 06:30"
                todayDateTime = todayDate + " 05:30"
                timerange.append(selectedDateTime)
                while selectedDateTime != todayDateTime:
                    _date = datetime.strptime(selectedDateTime, '%Y-%m-%d %H:%M')
                    _date_60 = _date + timedelta(minutes = 60)
                    selectedDateTime = _date_60.strftime('%Y-%m-%d %H:%M')
                    timerange.append(selectedDateTime)
            timerange = sorted(timerange)
            out_result = []
            out_downtime = []
            high_index = {}
            newDownTime = {}
            if selectedFromDate == selectedToDate:
                find_dict = {"asofdate":selectedFromDate}
            else:
                find_dict = {
                            "asofdate": {
                                "$gte": selectedFromDate,
                                "$lte": selectedToDate
                            }
                        }

            myDb = self.mongo["moulder_staging"]
            item_count = myDb.count_documents(find_dict)
            # if item_count == 0:
            #     print "Data not available in staging... Getting From Mains..."
            #     self.dbManager.get_today_records(selectedDate)
            #     find_dict = {"asofdate":selectedDate}
            #     item_count = myDb.count_documents(find_dict)
            # print item_count
            if item_count > 0:
                dbresult = myDb.find(find_dict)
                _dict = {}
                for dt in dbresult:
                    #print dt
                    if dt != []:        
                        if str(dt["Prop"]) not in _dict.keys():
                            _dict.setdefault(str(dt["Prop"]), [])
                        _dict[str(dt["Prop"])].append(dt)
            line_result = {}
            downTime = {}
            downTimeC = {}
            if _dict != {}:
                for prop in self.reportKeys:
                    stage_data = _dict[prop]
                    cnt = 1
                    line_data = {}
                    all_downs = {}
                    line_result.setdefault(prop, {})
                    for node in stage_data:
                        actual_num = elib.tonum(node["Actual"])

                        xTime = node["Time"]
                        xDateTime = xTime.strftime("%Y-%m-%d %H:%M:%S")
                        #if xDateTime in timerange:
                        elib.dictIncrement1D(all_downs, xDateTime,actual_num)

                    for xtime in sorted(all_downs.keys()):
                        minnum = all_downs[xtime]
                        if minnum == 0:
                            if cnt != 0:
                                elib.dictIncrement1D(downTime, prop, [xtime])
                                cnt = 0
                        else:
                            if cnt == 0:
                                elib.dictIncrement1D(downTimeC, prop, [xtime])
                            cnt = 1

                out_downtime = []
                high_index = {}
                high_duration = {}
                newDownTime = {}
                newDownTimeClose = {}
                for prop in self.reportKeys:
                    duration = []
                    newDownTime.setdefault(prop, downTime.get(prop, []))
                    for xt in downTime.get(prop, []):
                        close = {}
                        close.setdefault("Start", xt)
                        xt_index = downTime[prop].index(xt)
                        if xt_index < len(downTimeC.get(prop, [])):
                            new_xt = downTimeC[prop][xt_index]
                            close.setdefault("End", new_xt)
                            startdate = datetime.strptime(xt, '%Y-%m-%d %H:%M:%S')
                            enddate = datetime.strptime(new_xt, '%Y-%m-%d %H:%M:%S')
                            diff = enddate - startdate
                            duration.append(str(diff))
                            # diff_format = diff.strftime("%H:%M:%S")
                            close.setdefault("Duration", str(diff))
                        else:
                            close.setdefault("End", "-")
                            close.setdefault("Duration", "-")
                        elib.dictIncrement1D(newDownTimeClose, prop, [close])
                    count = len(list(set(downTime.get(prop, []))))
                    total_duration = self.getTotalDuration(duration)
                    high_duration.setdefault(prop, total_duration)
                    high_index.setdefault(prop, count)
                max_value = max(high_index.iteritems(), key=operator.itemgetter(1))
                
                keys = ["Start", "End", "Duration"]

                for x in range(0, max_value[1] + 1):
                    row = {}
                    row.setdefault("index", x)
                    for prop in self.reportKeys:
                        propname = prop.lower().replace(" ", "_")
                        _data = newDownTimeClose.get(prop, [])
                        if len(_data) > x:
                            nowData = _data[x]
                            for key in keys:
                                row.setdefault(propname+"_"+key, nowData[key])
                        else:
                            for key in keys:
                                row.setdefault(propname+"_"+key, "-")
                    out_downtime.append(row)

            columns = []
            for key in self.reportKeys:
                columns.append({
                    "field" : key,
                    "header": key + " RPM"
                })

            if mode == "view":  
                return jsonify(Results={"all_rows":out_downtime, "footer": high_index, "footer_duration":high_duration, "columns": columns})
            else:
                return {"all_rows":out_downtime, "footer": high_index, "footer_duration":high_duration}
        except Exception as e:
            self.log.exception("get_moulder_downtime_report Exception....")
            self.log.exception(e)

    def get_moulder_report(self, mode="view"):
        try:
            params = self.get_params(request)
            self.get_settings()
            result = False
            timerange = []
            _dict = {}
            out_result = []
            selectedFromDate = params.get('selectedFromDate', False)
            selectedToDate = params.get('selectedToDate', False)
            start = datetime.strptime(selectedFromDate, "%Y-%m-%d")
            end = datetime.strptime(selectedToDate, "%Y-%m-%d")
            date_generated = [start + timedelta(days=x) for x in range(0, (end-start).days + 1)]

            if selectedFromDate == selectedToDate:
                if date_generated == []:
                    date_generated = [start]

            for dateparam in date_generated:
                # dateparam = params.get('selectedDate', False)
                yesterdayDate = dateparam
                _date2460 = yesterdayDate + timedelta(minutes = (24*60))
                todayDate = _date2460.strftime('%Y-%m-%d')
                selectedDate = yesterdayDate.strftime("%Y-%m-%d")
                self.dbManager.get_today_records(selectedDate)

                selectedDateTime = selectedDate + " 06:30"
                todayDateTime = todayDate + " 05:30"
                timerange.append(selectedDateTime)
                while selectedDateTime != todayDateTime:
                    _date = datetime.strptime(selectedDateTime, '%Y-%m-%d %H:%M')
                    _date_60 = _date + timedelta(minutes = 60)
                    selectedDateTime = _date_60.strftime('%Y-%m-%d %H:%M')
                    timerange.append(selectedDateTime)
            timerange = sorted(timerange)
            print timerange

            if selectedFromDate == selectedToDate:
                find_dict = {"asofdate":selectedFromDate}
            else:
                find_dict = {
                            "asofdate": {
                                "$gte": selectedFromDate,
                                "$lte": selectedToDate
                            }
                        }

            myDb = self.mongo["moulder_staging"]
            item_count = myDb.count_documents(find_dict)
            # if item_count == 0:
            #     self.log.debug("Data not available in staging... Getting From Mains...")
            #     self.dbManager.get_today_records(selectedDate)
            #     find_dict = {"asofdate":selectedDate}
            #     item_count = myDb.count_documents(find_dict)
            self.log.debug(item_count)
            print item_count
            if item_count > 0:
                dbresult = myDb.find(find_dict)
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
                        current_num = elib.tonum(node["Frequency"])
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
                                elib.dictIncrement(line_data, xDateTime, "SetPoint", [setpoint])
                            else:
                                if xDateTime not in line_data.keys():
                                    line_data.setdefault(xDateTime, {}).setdefault("Actual", [0])
                                    line_data.setdefault(xDateTime, {}).setdefault("SetPoint", [0])
                                elif "Actual" not in line_data[xDateTime]:
                                    line_data[xDateTime].setdefault("Actual", [0])
                                    line_data[xDateTime].setdefault("SetPoint", [0])
                            if current_num > 0:
                                elib.dictIncrement(line_data, xDateTime, "CurrentActual", [current_num])
                            else:
                                if xDateTime not in line_data.keys():
                                    line_data.setdefault(xDateTime, {}).setdefault("CurrentActual", [0])
                                elif "CurrentActual" not in line_data[xDateTime].keys():
                                    line_data[xDateTime].setdefault("CurrentActual", [0])
                    for xTime in line_data:
                        avg_baking = sum(line_data[xTime]["BakingTime"])/len(line_data[xTime]["BakingTime"])
                        avg_actual = sum(line_data[xTime]["Actual"])/len(line_data[xTime]["Actual"])
                        avg_setpoint = sum(line_data[xTime]["SetPoint"])/len(line_data[xTime]["SetPoint"])
                        avg_current_actual = sum(line_data[xTime]["CurrentActual"])/len(line_data[xTime]["CurrentActual"])

                        line_result[prop].setdefault(xTime, {}).setdefault("BakingTime", elib.rnd(avg_baking, 0))
                        line_result[prop].setdefault(xTime, {}).setdefault("Actual", elib.rnd(avg_actual, 0))
                        line_result[prop].setdefault(xTime, {}).setdefault("SetPoint", elib.rnd(avg_setpoint, 0))
                        line_result[prop].setdefault(xTime, {}).setdefault("Current", elib.rnd(avg_current_actual, 2))

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
                            row.setdefault(newProp+"_Current", line_result[prop][xTime]["Current"])
                    if row != {}:
                        out_result.append(row)
                        
            if mode == "view":  
                return jsonify(Results= out_result)
            else:
                return out_result
        except Exception as e:
            self.log.exception("get_moulder_report Exception....")
            self.log.exception(e)
                

    def get_moulder_home(self):
        try:
            params = self.get_params(request)
            self.get_settings()
            result = False
            timerange = []
            selectedFromDate = params.get('selectedFromDate', False)
            selectedToDate = params.get('selectedToDate', False)
            start = datetime.strptime(selectedFromDate, "%Y-%m-%d")
            end = datetime.strptime(selectedToDate, "%Y-%m-%d")
            date_generated = [start + timedelta(days=x) for x in range(0, (end-start).days + 1)]

            if selectedFromDate == selectedToDate:
                if date_generated == []:
                    date_generated = [start]

            for dateparam in date_generated:
                # dateparam = params.get('selectedDate', False)
                yesterdayDate = dateparam
                _date2460 = yesterdayDate + timedelta(minutes = (24*60))
                todayDate = _date2460.strftime('%Y-%m-%d')
                selectedDate = yesterdayDate.strftime("%Y-%m-%d")
                self.dbManager.get_today_records(selectedDate)

                selectedDateTime = selectedDate + " 06:30"
                todayDateTime = todayDate + " 05:30"
                timerange.append(selectedDateTime)
                while selectedDateTime != todayDateTime:
                    _date = datetime.strptime(selectedDateTime, '%Y-%m-%d %H:%M')
                    _date_60 = _date + timedelta(minutes = 60)
                    selectedDateTime = _date_60.strftime('%Y-%m-%d %H:%M')
                    timerange.append(selectedDateTime)
            timerange = sorted(timerange)

            out_result = []

            if selectedFromDate == selectedToDate:
                find_dict = {"asofdate":selectedFromDate}
            else:
                find_dict = {
                            "asofdate": {
                                "$gte": selectedFromDate,
                                "$lte": selectedToDate
                            }
                        }

            myDb = self.mongo["moulder_staging"]
            item_count = myDb.count_documents(find_dict)
            
            self.log.debug(item_count)
            line_color = {
                'SetPoint': '#662441',
                'Actual': '#e34566',
                'CurrentSetPoint': '#74d600',
                'CurrentActual': '#08c'
            }
            legends_format = {
                'SetPoint':{
                    'name' : 'Set Point',
                    # 'color' : '#3eb308',
                    'color' : line_color['SetPoint'],
                    'dashStyle' : 'Solid',
                    'type' : 'line',
                    'y':0,
                    'visible' : True
                },
                'Actual' : {
                    'name' : 'Actual',
                    # 'color' : '#3eb308',
                    'color' : line_color['Actual'],
                    'dashStyle' : 'Solid',
                    'type' : 'line',
                    'y':0,
                    'visible' : True
                },
                'CurrentActual' : {
                    'name' : 'Current Actual',
                    # 'color' : '#3eb308',
                    'color' : line_color['CurrentActual'],
                    'dashStyle' : 'Solid',
                    'type' : 'line',
                    'y':1,
                    'visible' : True
                }
            }
            _dict = {}
            if item_count > 0:
                dbresult = myDb.find(find_dict)
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
                cminNum = 10000
                cmaxNum = -1
                cmaxTime = ""
                cminTime = ""
                result = {}
                line_data = {}
                line_result = {}
                line_series = []

                for prop in self.reportKeys:
                    # if prop == "Moulder":
                    minNum = 10000
                    maxNum = -1
                    maxTime = ""
                    minTime = ""
                    cminNum = 10000
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
                        current_num = elib.tonum(node["Frequency"])

                        xTime = node["Time"]
                        xDateTime =  xTime.strftime("%Y-%m-%d %H:%M")
                        
                        if actual_num > 0:
                            elib.dictIncrement1D(target_dict, "Actual", elib.tonum(node["Actual"]))
                            elib.dictIncrement1D(target_dict, "MinMax", [elib.tonum(node["Actual"])])
                        else:
                            elib.dictIncrement1D(target_dict, "Actual", 0)
                            elib.dictIncrement1D(target_dict, "MinMax", [0])
                        if current_num > 0:
                            elib.dictIncrement1D(target_dict, "CurrentActual", current_num)
                            elib.dictIncrement1D(target_dict, "CurrentMinMax", [current_num])
                        elif "CurrentMinMax" not in target_dict:
                            target_dict.setdefault("CurrentMinMax", [0])
                            target_dict.setdefault("CurrentActual", 0)

                        
                        # print xDateTime,'---', actual_num
                        if xDateTime in timerange:
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
                            if current_num > 0:
                                elib.dictIncrement(line_data, xDateTime, "CurrentActual", [current_num])
                            else:
                                if xDateTime not in line_data.keys():
                                    line_data.setdefault(xDateTime, {}).setdefault("CurrentActual", [0])
                                elif "CurrentActual" not in line_data[xDateTime].keys():
                                    line_data[xDateTime].setdefault("CurrentActual", [0])
                    for xtime in line_data.keys():
                        line_series.setdefault(xtime,{})
                        for key in line_data[xtime]:
                            avg = sum(line_data[xtime][key]) / len(line_data[xtime][key])
                            line_series[xtime].setdefault(key, avg)
                            if key == "Actual":
                                if maxNum < avg:
                                    maxNum = avg
                                    maxTime = xtime
                                elif minNum >= avg:
                                    minNum = avg
                                    minTime = xtime

                            if key == "CurrentActual":
                                if cmaxNum < avg:
                                    cmaxNum = avg
                                    cmaxTime = xtime
                                elif cminNum >= avg:
                                    cminNum = avg
                                    cminTime = xtime


                    for xtime in sorted(line_series.keys()):
                        for leg in legends_format:
                            line_result[leg]["data"].append({
                                "category": xtime,
                                "y": elib.rnd(line_series[xtime][leg],2)
                            })

                    non_zero = [x for x in target_dict.get("MinMax", [0]) if x != 0]
                    non_zero_current = [x for x in target_dict.get("CurrentMinMax", [0]) if x != 0]

                    if len(non_zero) == 0:
                        non_zero = [0]
                    if len(non_zero_current) == 0:
                        non_zero_current = [0]

                    average = target_dict.get("Actual",0) / len(non_zero)
                    average_current = target_dict.get("CurrentActual",0) / len(non_zero_current)

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
                    
                    final_dict = {}
                    final_dict["line_chart"] = chartObj

                    final_dict.setdefault("Average", elib.rnd(elib.tonum(average,"float"),0))
                    final_dict.setdefault("CurrentAverage", elib.rnd(elib.tonum(average_current,"float"),2))
                    final_dict.setdefault("Max", elib.rnd(maxNum, 0))
                    final_dict.setdefault("Min", elib.rnd(minNum, 0))
                    final_dict.setdefault("MaxTime", maxTime)
                    final_dict.setdefault("MinTime", minTime)
                    final_dict.setdefault("CurrentMax", elib.rnd(cmaxNum, 2))
                    final_dict.setdefault("CurrentMin", elib.rnd(cminNum, 2))
                    final_dict.setdefault("CurrentMaxTime", cmaxTime)
                    final_dict.setdefault("CurrentMinTime", cminTime)

                    out_result.append({"prop": prop, "data": final_dict})

            return jsonify(Results= out_result) 
        except Exception as e:
            self.log.exception("get_moulder_home Exception....")
            self.log.exception(e)

    def downloadMoulderDowntimeReport(self, out_report):
        try:
            params = self.get_params(request)

            selectedDate = params.get('selectedDate', False)
            todayDate = params.get('today', False)
            reportTitle = params.get("title", False)

            todayDate = datetime.now();
            dts_time = time.mktime(todayDate.timetuple()) * 1000

            fileCompleted = []
            all_rows = []
            data_list = []
            txtfilename = FILE_PATH + "reports_moulder.txt"
            subheaders = ["Start Time", "End Time", "Duration"]
            headkeys = ["Start", "End", "Duration"]
            headers =  []
            keyheaders = []

            for mode in self.reportKeys:
                for node in subheaders:
                    headers.append(node)
                    keyheaders.append(mode.lower().replace(" ", "_") + "_" + headkeys[subheaders.index(node)])
            data_list = []
            s = ""
            
            hpstack = []
            for prop in self.reportKeys:
                hpstack.append({"rowspan":1, "colspan":3, "name": prop })

            ht = ''
            ht += '<table><thead><tr><th style=""></th>'
            for hd in hpstack:
                ht += '<th rowspan="'+str(hd['rowspan'])+'" colspan="'+str(hd['colspan'])+'" style="">'+hd["name"]+'</th>'
            rowcnt = 0
            ht += '</tr></thead><tbody>'
            ht += '<tr style="text-align: right;">'
            ht += '<td style=""></td>'
            for node in headers:
                ht += '<td style="">'+node+'</td>'
            ht += '</tr>'

            for node in out_report["all_rows"]:
                rowcnt += 1
                ht += '<tr style="text-align: right;">'
                ht += '<td style="">'+str(rowcnt)+'</td>'
                for key in keyheaders:
                    ht += '<td style="">'+str(node.get(key,"-"))+'</td>'
            # for node in out_report["footer"]:
            rowcnt += 1
            ht += '<tr style="text-align: right;">'
            ht += '<td style="">'+str(rowcnt)+'</td>'
            for prop in self.reportKeys:
                ht += '<td colspan="3" style="">Down Time Count: '+str(out_report["footer"].get(prop,"-"))+'</td>'

            rowcnt += 1
            ht += '<tr style="text-align: right;">'
            ht += '<td style="">'+str(rowcnt)+'</td>'
            for prop in self.reportKeys:
                ht += '<td colspan="3" style="">Total Duration: '+str(out_report["footer_duration"].get(prop,"-"))+'</td>'

            out_pdf= FILE_PATH + 'Moulder_DownTime_Report_'+selectedDate+'.pdf'
            intermediate_html = FILE_PATH + 'intermediate.html'
            reportTitle = "Moulder Downtime Report"

            htmlToAdd = '<div style="margin-left:10px;margin-top:20px;text-align:center;border:1px solid white;">'\
                            '<div style="text-center:left;margin-left:1rem;margin-right:1rem;margin-top:500px;">'\
                                '<img src="' + SETTING_PATH + 'abz2_big.png" style=""/>'\
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
            self.to_html_pretty_report(ht, intermediate_html, "Moulder Downtime Report", htmlToAdd, reportTitle, selectedDate)
            htmlToAdd = ""
            options = {'orientation': 'Landscape'}
            # pdfkit.from_file(intermediate_html, out_pdf, options=options, configuration = config)
            pdfkit.from_file(intermediate_html, out_pdf, options=options)
            return out_pdf
        except Exception as e:
            self.log.exception("downloadMoulderDowntimeReport Exception....")
            self.log.exception(e)

    def downloadMoulderReport(self, out_report):
        try:
            params = self.get_params(request)

            selectedDate = params.get('selectedDate', False)
            todayDate = params.get('today', False)
            reportTitle = params.get("title", False)

            todayDate = datetime.now();
            dts_time = time.mktime(todayDate.timetuple()) * 1000

            fileCompleted = []
            all_rows = []
            subheaders = ["Set Point", "Actual", "Current"]
            headkeys = ["SetPoint", "Actual", "Current"]
            headers =  []
            keyheaders = ["xTime"]

            for mode in self.reportKeys:
                for node in subheaders:
                    if mode in ["Wet Check Weigher Conveyer"]:
                        if node != "Current":
                            headers.append(node)
                            keyheaders.append(mode.lower().replace(" ", "_") + "_" + headkeys[subheaders.index(node)])
                    else:
                        headers.append(node)
                        keyheaders.append(mode.lower().replace(" ", "_") + "_" + headkeys[subheaders.index(node)])
            keyheaders.append("bakingTime")
            
            hpstack = []
            hpstack.append({"rowspan":2, "colspan":1, "name": "Time"})
            for prop in self.reportKeys:
                if prop in ["Wet Check Weigher Conveyer"]:
                    hpstack.append({"rowspan":1, "colspan":2, "name": prop })
                else:
                    hpstack.append({"rowspan":1, "colspan":3, "name": prop })
            hpstack.append({"rowspan":2, "colspan":1, "name": "Baking Time"})

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

            out_pdf= FILE_PATH + 'Moulder_Report_'+selectedDate+'.pdf'
            intermediate_html = FILE_PATH + 'intermediate.html'
            reportTitle = "Moulder Daily Report"

            htmlToAdd = '<div style="margin-left:10px;margin-top:20px;text-align:center;border:1px solid white;">'\
                            '<div style="text-center:left;margin-left:1rem;margin-right:1rem;margin-top:500px;">'\
                                '<img src="' + SETTING_PATH + 'abz2_big.png" style=""/>'\
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
            self.to_html_pretty_report(ht, intermediate_html, "Moulder Daily Report", htmlToAdd, reportTitle, selectedDate)
            htmlToAdd = ""
            options = {'orientation': 'Landscape'}
            # pdfkit.from_file(intermediate_html, out_pdf, options=options, configuration = config)
            pdfkit.from_file(intermediate_html, out_pdf, options=options)
            return out_pdf
        except Exception as e:
            self.log.exception("downloadMoulderReport Exception....")
            self.log.exception(e)
        
    def getTotalDuration(self,timeList):
        try:
            result = ""
            totalSecs = 0
            for tm in timeList:
                timeParts = [int(s) for s in tm.split(':')]
                totalSecs += (timeParts[0] * 60 + timeParts[1]) * 60 + timeParts[2]
            totalSecs, sec = divmod(totalSecs, 60)
            hr, min = divmod(totalSecs, 60)
            result = "%d:%02d:%02d" % (hr, min, sec)
            return result
        except Exception as e:
            self.log.exception("getTotalDuration Exception....")
            self.log.exception(e)

    def to_html_pretty_report(self, df, filename='out.html', title='', htmlToAdd='',reportTitle='', selectedDate=''):
        try:
            htm = ''
            if htmlToAdd != '':
                htm += htmlToAdd
            if title != '':
                htm += '<h1><img src="' + SETTING_PATH + 'abz2_small.png" style="margin-right:100px;margin-top:5px;"/>'
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
        except Exception as e:
            self.log.exception("to_html_pretty_report Exception....")
            self.log.exception(e)

    def to_html_pretty(self, df, filename='out.html', title='', htmlToAdd='',reportTitle='', selectedDate=''):
        try:
            ht = ''
            if htmlToAdd != '':
                ht += htmlToAdd
            if title != '':
                ht += '<h1><img src="' + SETTING_PATH + 'abz2_small.png" style="margin-right:100px;margin-top:5px;"/>'
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
        except Exception as e:
            self.log.exception("to_html_pretty Exception....")
            self.log.exception(e)


    def save_moulder_report(self):
        try:
            self.log.debug("Saving Report...")
            out_list = self.get_moulder_report(mode="download")
            filename = self.downloadMoulderReport(out_list)
            path = FILE_PATH
            uuidstr = str(uuid.uuid4())
            filepath = filename

            zip_name = "Moulder_Reports_"+uuidstr+".zip"
            zip_file = path + zip_name
            self.log.debug('Creating archive ' + zip_name)
            zf = zipfile.ZipFile(zip_file, mode='w')
            compression = zipfile.ZIP_DEFLATED

            zf.write(filepath, os.path.basename(filepath), compress_type=compression)
            os.remove(filepath)

            return jsonify(Results = zip_name)
        except Exception as e:
            self.log.exception("save_moulder_report Exception....")
            self.log.exception(e)
    
    def get_moulder_dashboard_home(self):
        try:
            params = self.get_params(request)
            self.get_settings()
            result = False
            html_list = []
            timerange = []
            selectedFromDate = params.get('selectedFromDate', False)
            selectedToDate = params.get('selectedToDate', False)
            start = datetime.strptime(selectedFromDate, "%Y-%m-%d")
            end = datetime.strptime(selectedToDate, "%Y-%m-%d")
            date_generated = [start + timedelta(days=x) for x in range(0, (end-start).days + 1)]

            if selectedFromDate == selectedToDate:
                if date_generated == []:
                    date_generated = [start]

            for dateparam in date_generated:
                # dateparam = params.get('selectedDate', False)
                yesterdayDate = dateparam
                _date2460 = yesterdayDate + timedelta(minutes = (24*60))
                todayDate = _date2460.strftime('%Y-%m-%d')
                selectedDate = yesterdayDate.strftime("%Y-%m-%d")
                self.dbManager.get_today_records(selectedDate)

                selectedDateTime = selectedDate + " 06:30"
                todayDateTime = todayDate + " 05:30"
                timerange.append(selectedDateTime)
                while selectedDateTime != todayDateTime:
                    _date = datetime.strptime(selectedDateTime, '%Y-%m-%d %H:%M')
                    _date_60 = _date + timedelta(minutes = 60)
                    selectedDateTime = _date_60.strftime('%Y-%m-%d %H:%M')
                    timerange.append(selectedDateTime)
            timerange = sorted(timerange)

            out_result = []

            if selectedFromDate == selectedToDate:
                find_dict = {"asofdate":selectedFromDate}
            else:
                find_dict = {
                            "asofdate": {
                                "$gte": selectedFromDate,
                                "$lte": selectedToDate
                            }
                        }

            myDb = self.mongo["moulder_staging"]
            item_count = myDb.count_documents(find_dict)
            
            self.log.debug(item_count)
            line_color = {
                'SetPoint': '#662441',
                'Actual': '#e34566',
                'CurrentSetPoint': '#74d600',
                'CurrentActual': '#08c'
            }
            legends_format = {
                'SetPoint':{
                    'name' : 'Set Point',
                    # 'color' : '#3eb308',
                    'color' : line_color['SetPoint'],
                    'dashStyle' : 'Solid',
                    'type' : 'line',
                    'y':0,
                    'visible' : True
                },
                'Actual' : {
                    'name' : 'Actual',
                    # 'color' : '#3eb308',
                    'color' : line_color['Actual'],
                    'dashStyle' : 'Solid',
                    'type' : 'line',
                    'y':0,
                    'visible' : True
                },
                'CurrentActual' : {
                    'name' : 'Current Actual',
                    # 'color' : '#3eb308',
                    'color' : line_color['CurrentActual'],
                    'dashStyle' : 'Solid',
                    'type' : 'line',
                    'y':1,
                    'visible' : True
                }
            }
            _dict = {}
            if item_count > 0:
                dbresult = myDb.find(find_dict)
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
                cminNum = 10000
                cmaxNum = -1
                cmaxTime = ""
                cminTime = ""
                result = {}
                line_data = {}
                line_result = {}
                line_series = []

                for prop in self.reportKeys:
                    # if prop == "Moulder":
                    minNum = 10000
                    maxNum = -1
                    maxTime = ""
                    minTime = ""
                    cminNum = 10000
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
                        current_num = elib.tonum(node["Frequency"])

                        xTime = node["Time"]
                        xDateTime =  xTime.strftime("%Y-%m-%d %H:%M")
                        
                        if actual_num > 0:
                            elib.dictIncrement1D(target_dict, "Actual", elib.tonum(node["Actual"]))
                            elib.dictIncrement1D(target_dict, "MinMax", [elib.tonum(node["Actual"])])
                        else:
                            elib.dictIncrement1D(target_dict, "Actual", 0)
                            elib.dictIncrement1D(target_dict, "MinMax", [0])
                        if current_num > 0:
                            elib.dictIncrement1D(target_dict, "CurrentActual", current_num)
                            elib.dictIncrement1D(target_dict, "CurrentMinMax", [current_num])
                        elif "CurrentMinMax" not in target_dict:
                            target_dict.setdefault("CurrentMinMax", [0])
                            target_dict.setdefault("CurrentActual", 0)

                        
                        # print xDateTime,'---', actual_num
                        if xDateTime in timerange:
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
                            if current_num > 0:
                                elib.dictIncrement(line_data, xDateTime, "CurrentActual", [current_num])
                            else:
                                if xDateTime not in line_data.keys():
                                    line_data.setdefault(xDateTime, {}).setdefault("CurrentActual", [0])
                                elif "CurrentActual" not in line_data[xDateTime].keys():
                                    line_data[xDateTime].setdefault("CurrentActual", [0])
                    for xtime in line_data.keys():
                        line_series.setdefault(xtime,{})
                        for key in line_data[xtime]:
                            avg = sum(line_data[xtime][key]) / len(line_data[xtime][key])
                            line_series[xtime].setdefault(key, avg)
                            if key == "Actual":
                                if maxNum < avg:
                                    maxNum = avg
                                    maxTime = xtime
                                elif minNum >= avg:
                                    minNum = avg
                                    minTime = xtime

                            if key == "CurrentActual":
                                if cmaxNum < avg:
                                    cmaxNum = avg
                                    cmaxTime = xtime
                                elif cminNum >= avg:
                                    cminNum = avg
                                    cminTime = xtime


                    for xtime in sorted(line_series.keys()):
                        for leg in legends_format:
                            line_result[leg]["data"].append({
                                "category": xtime,
                                "y": elib.rnd(line_series[xtime][leg],2)
                            })

                    non_zero = [x for x in target_dict.get("MinMax", [0]) if x != 0]
                    non_zero_current = [x for x in target_dict.get("CurrentMinMax", [0]) if x != 0]

                    if len(non_zero) == 0:
                        non_zero = [0]
                    if len(non_zero_current) == 0:
                        non_zero_current = [0]

                    average = target_dict.get("Actual",0) / len(non_zero)
                    average_current = target_dict.get("CurrentActual",0) / len(non_zero_current)

                    chartResult = []
                    isData = False
                    for leg in legends_format:
                        if len(line_result[leg]['data']) > 0:
                            isData = True
                        chartResult.append(line_result[leg])
                    xAxis = []
                    for x in sorted(line_series.keys()):
                        xAxis.append(x[11:])
                    
                    chartObj = {}
                    chartObj["categories"] = sorted(line_series.keys())
                    chartObj['charttype'] = 'linechart'
                    chartObj['id'] = 'line_'+prop.lower().replace(' ', '_')
                    chartObj['series'] = chartResult
                    chartObj['isData'] = isData
                    
                    final_dict = {}
                    final_dict["line_chart"] = chartObj
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
                    for ln in chartResult:
                        linechart.add_data_set(ln["data"], series_type=ln["type"], name=ln["name"], color=ln["color"])
                    linechart.save_file(FILE_PATH + chartObj["id"])
                    html_list.append({"id": chartObj["id"], "type":"line"})

                    final_dict.setdefault("Average", elib.rnd(elib.tonum(average,"float"),0))
                    final_dict.setdefault("CurrentAverage", elib.rnd(elib.tonum(average_current,"float"),2))
                    final_dict.setdefault("Max", elib.rnd(maxNum, 0))
                    final_dict.setdefault("Min", elib.rnd(minNum, 0))
                    final_dict.setdefault("MaxTime", maxTime)
                    final_dict.setdefault("MinTime", minTime)
                    final_dict.setdefault("CurrentMax", elib.rnd(cmaxNum, 2))
                    final_dict.setdefault("CurrentMin", elib.rnd(cminNum, 2))
                    final_dict.setdefault("CurrentMaxTime", cmaxTime)
                    final_dict.setdefault("CurrentMinTime", cminTime)

                    out_result.append({"prop": prop, "data": final_dict})

            for ht in html_list:
                self.htmltoImage(ht["id"], ht["type"])

            out_pdf= FILE_PATH + 'Moulder_Dashboard_'+selectedDate+'.pdf'
            intermediate_html =  FILE_PATH + 'intermediate.html'

            htmlToAdd = '<div style="margin-left:10px;margin-top:5px;text-align:center;border:1px solid white;">'\
                            '<div style="text-center:left;margin-left:1rem;margin-right:1rem;margin-top:500px;">'\
                                '<img src="' + SETTING_PATH + 'abz2_big.png" style=""/>'\
                                '<div style="text-align:center;color:#323232;font-size:35px;margin-top:7px;">'\
                                    '<span style="color:#323232;font-size:35px;margin-right:2rem;">Moulder Daily Report</span>'\
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
                                                '<div class="flex__item text-left" style="margin-left:10px;">RPM</div>'\
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
                                            '<div class="flex flex__item flex--middle margin--left margin--top">'\
                                                '<div class="flex__item text-left" style="margin-left:10px;">Current</div>'\
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
                                                '<div class="flex__item text-left" style="margin-left:10px;color:white;">RPM</div>'\
                                            '</div>'\
                                            '<div class="flex flex__item flex--middle flex--right text-large overview-value-border" style="">'\
                                                '<div class="flex__item text-right" style="margin-right:2px;">'+str(propData["Average"])+' RPM</div>'\
                                            '</div>'\
                                            '<div class="flex flex__item flex--middle flex--right text-large overview-value-border">'\
                                                '<div class="flex__item text-right" style="margin-right:2px;">'+str(propData["Max"])+' RPM</div>'\
                                            '</div>'\
                                            '<div class="flex flex__item flex--middle flex--right text-large overview-value-border" style="border-bottom:1px solid #e9e9e9;">'\
                                                '<div class="flex__item text-right" style="margin-right:2px;">'+str(propData["Min"])+' RPM</div>'\
                                            '</div>'\
                                            '<div class="flex flex__item flex--middle margin--left margin--top">'\
                                                '<div class="flex__item text-left" style="margin-left:10px;color:white;">Current</div>'\
                                            '</div>'\
                                            '<div class="flex flex__item flex--middle flex--right text-large overview-value-border">'\
                                                '<div class="flex__item text-right" style="margin-right:2px;">'+str(propData["CurrentAverage"])+' A</div>'\
                                            '</div>'\
                                            '<div class="flex flex__item flex--middle flex--right text-large overview-value-border">'\
                                                '<div class="flex__item text-right" style="margin-right:2px;">'+str(propData["CurrentMax"])+' A</div>'\
                                            '</div>'\
                                            '<div class="flex flex__item flex--middle flex--right text-large overview-value-border" style="border-bottom:1px solid #e9e9e9;">'\
                                                '<div class="flex__item text-right" style="margin-right:2px;">'+str(propData["CurrentMin"])+' A</div>'\
                                            '</div>'\
                                        '</div>'\
                                        '<div class="flex flex--col flex__item" style="">'\
                                            '<div class="flex flex__item flex--middle margin--left">'\
                                                '<div class="flex__item text-left" style="margin-left:10px;color:white;">RPM</div>'\
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
                                            '<div class="flex flex__item flex--middle margin--left margin--top">'\
                                                '<div class="flex__item text-left" style="margin-left:10px;color:white;">Current</div>'\
                                            '</div>'\
                                            '<div class="flex flex__item flex--middle flex--right text-large margin--right overview-value-border">'\
                                                '<div class="flex__item text-right" style="margin-right:10px;color:white;">'+str(propData["CurrentMaxTime"])+'</div>'\
                                            '</div>'\
                                            '<div class="flex flex__item flex--middle flex--right text-large margin--right overview-value-border">'\
                                                '<div class="flex__item text-right" style="margin-right:10px;">'+str(propData["CurrentMaxTime"])+'</div>'\
                                            '</div>'\
                                            '<div class="flex flex__item flex--middle flex--right text-large margin--right overview-value-border" style="border-bottom:1px solid #e9e9e9;">'\
                                                '<div class="flex__item text-right" style="margin-right:10px;">'+str(propData["CurrentMinTime"])+'</div>'\
                                            '</div>'\
                                        '</div>'\
                                    '</div>'\
                                '</div>'\
                                '<div class="flex flex--col flex__item__3 custom-holder-2" style="width:70%;">'\
                                    '<div class="flex flex--row flex--middle cnt-sub-2" style="height:25px; width:100%;">'\
                                        '<div class="hdr-txt3 pointer" style="margin-left:1rem;padding-left: 1rem;padding-right:1rem;">Trend</div>'\
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
                    self.to_html_pretty_2(ht, intermediate_html, prop, htmlToAdd, "Moulder Daily Report", selectedDate)
                    htmlToAdd = ""
                elif index >= len(self.reportKeys) and index % 2 != 0:
                    ht += '</div>'
                    self.to_html_pretty_2(ht, intermediate_html, prop, htmlToAdd, "Moulder Daily Report", selectedDate)
                    htmlToAdd = ""

            options = {
                # "page-size": "A4",
                "orientation": "Landscape",
                # 'dpi':400
            }
            # pdfkit.from_file(intermediate_html, out_pdf, options=options, configuration=config)
            pdfkit.from_file(intermediate_html, out_pdf, options=options)

            for img in imagesToDelete:
                os.remove(img)

            return out_pdf 
        except Exception as e:
            self.log.exception("get_moulder_home Exception....")
            self.log.exception(e)
    
    def save_moulder_home(self):
        try:
            self.log.info("Saving Dashboard Report...")
            filename = self.get_moulder_dashboard_home()
            path = FILE_PATH
            uuidstr = str(uuid.uuid4())
            filepath = filename

            zip_name = "Moulder_Dashboard_Reports_"+uuidstr+".zip"
            zip_file = path + zip_name
            self.log.info('Creating archive %s', zip_name)
            zf = zipfile.ZipFile(zip_file, mode='w')
            compression = zipfile.ZIP_DEFLATED

            zf.write(filepath, os.path.basename(filepath), compress_type=compression)
            os.remove(filepath)

            return jsonify(Results = zip_name)
        except Exception as e:
            self.log.exception("save_moulder_home Exception....")
            self.log.exception(e)

    def save_moulder_downtime_report(self):
        try:
            self.log.debug("Saving Report...")
            out_list = self.get_moulder_downtime_report(mode="download")
            filename = self.downloadMoulderDowntimeReport(out_list)
            path = FILE_PATH
            uuidstr = str(uuid.uuid4())
            filepath = filename

            zip_name = "Downtime_Reports_"+uuidstr+".zip"
            zip_file = path + zip_name
            self.log.debug('Creating archive ' + zip_name)
            zf = zipfile.ZipFile(zip_file, mode='w')
            compression = zipfile.ZIP_DEFLATED

            zf.write(filepath, os.path.basename(filepath), compress_type=compression)
            os.remove(filepath)

            return jsonify(Results = zip_name)
        except Exception as e:
            self.log.exception("save_moulder_downtime_report Exception....")
            self.log.exception(e)
    
    def to_html_pretty_2(self, ht, filename='out.html', title='', htmlToAdd="", reportTitle = '', selectedDate=''):
        htm = ''
        if htmlToAdd != "":
            htm += htmlToAdd
        if title != '':
            htm += '<h1><div class="flex flex--col flex__item flex--center">'
            htm += '<span style="text-align:left;width:20%;"> <img src="' + SETTING_PATH + 'abz2_small.png" align:left/></span>'
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
        self.log.info(ht+".html ---to--- %s.png", ht)
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

        # imgfile = imgkit.from_file(FILE_PATH + htmlname, FILE_PATH + pngname, options=options, config=image_config)
        imgfile = imgkit.from_file(FILE_PATH + htmlname, FILE_PATH + pngname, options=options)
        os.remove(FILE_PATH + htmlname)
