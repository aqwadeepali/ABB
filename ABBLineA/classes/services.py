import os, json
import elib
from datetime import timedelta
from datetime import datetime
from datetime import date
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
from stage_data import Run
import ast
from send_mail import EmailClient
import shutil
from decimal import Decimal

import imgkit
from highcharts import Highchart
from openpyxl.workbook import Workbook

from logging import getLogger, INFO, ERROR, WARNING, CRITICAL, NOTSET, DEBUG

# path_wkthmltopdf = r'C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe'
# config = pdfkit.configuration(wkhtmltopdf=path_wkthmltopdf)

# path_wkthmltoimage = r'C:\Program Files\wkhtmltopdf\bin\wkhtmltoimage.exe'
# image_config = imgkit.config(wkhtmltoimage=path_wkthmltoimage)

SETTING_PATH = str(os.path.realpath(__file__))
SETTING_PATH = SETTING_PATH.replace("services.pyc", "")
SETTING_PATH = SETTING_PATH.replace("services.pyo", "")
SETTING_PATH = SETTING_PATH.replace("services.py", "")
SETTING_PATH = SETTING_PATH + "data/"

FILE_PATH = str(os.path.realpath(__file__))
FILE_PATH = FILE_PATH.replace("services.pyc", "")
FILE_PATH = FILE_PATH.replace("services.pyo", "")
FILE_PATH = FILE_PATH.replace("services.py", "")
FILE_PATH = FILE_PATH.replace("classes", "")
FILE_PATH = FILE_PATH + "dbpush/data/"

TWOPLACES = Decimal(10) ** -2
#EMAIL_LIST = ['deepali.bmahajan@gmail.com', 'rishikesh.jathar@gmail.com', 'pramodkonde@hotmail.com', 'shivabharathi64@gmail.com', 'greathary@gmail.com', 'surnisaa@gmail.com', 'ptoke01@gmail.com', 'waghanna.aaditya@gmail.com', 'itantaanalytics@gmail.com', 'rock.boyz92@gmail.com']

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

HTML_TEMPLATE3 = '<html><head><link rel="stylesheet" type="text/css" href="'+SETTING_PATH+'all_css.css"/><style>'\
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
    BaseServices(app, WSGI_PATH_PREFIX)

class BaseServices:
    print'                    Registered Services'
    print'-------------------------------------------------------------------'
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

        self.dbManager = Run()
        # self.get_settings()
        # self.show_chart()

        self.app.add_url_rule(API + '/services/sendfresponse', 'sendfresponse', self.sendfresponse, methods=['GET','POST'])

        # # Home API
        self.app.add_url_rule(API + '/services/readsettings', 'readsettings', self.read_settings, methods=['POST'])
        self.app.add_url_rule(API + '/services/getalldashboards', 'getalldashboards', self.get_all_dashboards, methods=['POST'])
        self.app.add_url_rule(API + '/services/gethome', 'gethome', self.get_home, methods=['POST'])
        self.app.add_url_rule(API + '/services/getreports', 'getreports', self.get_reports, methods=['POST'])
        self.app.add_url_rule(API + '/services/savereport', 'savereport', self.save_reports, methods=['POST'])
        self.app.add_url_rule(API + '/services/savedashboardreport', 'savedashboardreport', self.save_dashboard_report, methods=['POST'])
        self.app.add_url_rule(API + '/services/getmixingmenu', 'getmixingmenu', self.getmixingmenu, methods=['POST'])

    def get_settings(self, rec_key):
        try:
            print "Reading Settings", rec_key
            keys = ""
            reportKeys = ""
            reportManager = ""
            all_key_list = ""
            setdata = ""
            reader = csv.DictReader(open(SETTING_PATH + 'settings.txt'), delimiter="\t")
            for row in reader:

                if row["Field"] == "REPORTKEYS_"+rec_key:
                    reportKeys = ast.literal_eval(row["Value"])
                if row["Field"] == "REPORTMNG_"+rec_key:
                    reportManager = ast.literal_eval(row["Value"])
                if row["Field"] == "SEQ_"+rec_key:
                    keys = row["Value"]
                if row["Field"] == "KEYS_"+rec_key:
                    all_key_list = row["Value"]
                if row["Field"] == "RECIPE":
                    recipeKeys = ast.literal_eval(row["Value"])
                if row["Field"] == "RECIPENAME":
                    recipeNames = ast.literal_eval(row["Value"])
                if row["Field"] == "SETDATA":
                    setdata = ast.literal_eval(row["Value"])
     
            self.seqKeys = keys
            self.reportManager = reportManager
            self.reportKeys = reportKeys
            self.keyList = all_key_list
            self.setdata = setdata
            # self.recipeKeys = recipeKeys
            # self.recipeNames = recipeNames
        except Exception as e:
            self.log.exception("Read Settings Exception....")
            self.log.exception(e)
    
    def read_settings(self,mode = "ui"):
        try:
            print "Reading Settings"
            time = ""
            tile = []
            EMAIL_LIST = []
            reader = csv.DictReader(open(SETTING_PATH + 'ui_settings.txt'), delimiter="\t")
            for row in reader:
                if row["Field"] == "UI_TIME":
                    time = row["Value"]
                if row["Field"] == "TILE":
                    tile = ast.literal_eval(row["Value"])
                if row["Field"] == "EMAIL_LIST":
                    EMAIL_LIST = ast.literal_eval(row["Value"])
            if mode == "ui":
                return jsonify(Results={
                    "time": time,
                    "tile": tile
                })
            else:
                return {"time":time, "email_list":EMAIL_LIST}
        except Exception as e:
            self.log.exception("Read UI Settings Exception....")
            self.log.exception(e)

    def get_all_dashboards(self):
        try:
            params = self.get_params(request)
            all_files = params.get("files", [])
            all_settings = self.read_settings("email")
            EMAIL_LIST = all_settings["email_list"]
            download_folder = os.path.expanduser("~")+"/Downloads/"

            dtime = datetime.now()
            current_time = dtime.strftime("%H:%M")

            format_dttime = dtime.strftime('%Y-%m-%d %H:%M:%S')
            format_dt = dtime.strftime('%Y-%m-%d')

            newfolder = FILE_PATH + "Dashboards_"+format_dt
            if not os.path.exists(newfolder):
                os.makedirs(newfolder)
                for fl in all_files:
                    shutil.copy(download_folder + fl["file"], newfolder)
                    os.remove(download_folder + fl["file"])
                shutil.make_archive(FILE_PATH + 'All_Dashboards', 'zip', newfolder)
            else:
                shutil.rmtree(newfolder)
                os.makedirs(newfolder)
                for fl in all_files:
                    shutil.copy(download_folder + fl["file"], newfolder)
                    os.remove(download_folder + fl["file"])
                shutil.make_archive(FILE_PATH + 'All_Dashboards', 'zip', newfolder)

            attachement = {
                "Dashboards.zip": FILE_PATH + "All_Dashboards.zip",
            } 
            self.log.debug("Sending Email ..............................")
            email_client = EmailClient(EMAIL_LIST, attachement)
            email_message = '<html><body><p>Dear Sir/Madam,<br>'\
                            '<br>'\
                            '<br>'\
                            'Pls. find herewith the Reports for Britannia, Pondicherry Line A. <br>'\
                            '<br>'\
                            '<br>'\
                            'Regards, <br>'\
                            'Britannia Industries Limited. <br>'\
                            'Pondicherry, Line A.<br>'\
                            '<br>'\
                            '<br>'\
                            '*This is an auto generated Mail from BIT, Pondicherry, Line A. Please do not reply.*</p></body></html>'
            email_client.sendMail('Britannia Report', email_message)
            self.log.debug("Email Sent...")
            os.system('taskkill /f /im chrome.exe')
            os.remove(FILE_PATH + 'All_Dashboards.zip')
            return jsonify(Results=True)
        except:
            self.log.exception("Email All Dashboards Exception....")
            self.log.exception(e)


    def get_params(self, request):
        return request.json if (request.method == 'POST') else request.args

    def get_priority(self):
        try:
            seq = self.seqKeys.split(",")
            _seqDict = {}

            index = 1
            for x in seq:
                _seqDict.setdefault(index, x)
                index += 1
            return _seqDict
        except Exception as e:
            self.log.exception("get_priority Exception....")
            self.log.exception(e)

    def sendfresponse(self):
        try:
            params = self.get_params(request)
            if params != False:
                fname = params.get('name')

                fPath = FILE_PATH + fname

                file = open(fPath, 'rb').read()
                response = Response()
                response.data = file
                response.status_code = 200
                response.headers = Headers()
                response.headers['Pragma'] = 'public'
                response.headers['Expires'] = '0'
                response.headers['Cache-Control'] = 'public'
                response.headers['Content-Description'] = 'File Transfer'
                response.headers['Content-Type'] = 'application/octet-stream'#'text/plain' #'application/vnd.ms-excel' #'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
                response.headers['Content-Disposition'] = 'attachment; filename='+fname
                response.headers['Content-Transfer-Encoding'] = 'binary'
                # response.headers['X-Key'] = self.KEY

                os.remove(fPath)

                return response
            else:
                return False
        except Exception as e:
            self.log.exception("sendfresponse Exception....")
            self.log.exception(e)

    def getmixingmenu(self):

        params = self.get_params(request)
        recKey = "1" #params.get('recipeValue', False)

        self.get_settings(recKey)

        splitKeys = self.seqKeys.split(",")
        mixingMenu = []
        for key in splitKeys:
            menu = {
                "label": key,
                "value": key,
                "display": True
            }
            mixingMenu.append(menu)

        return jsonify(Results = {"items": mixingMenu, "selected": splitKeys})


    def get_home(self):
        try:
            params = self.get_params(request)
            
            find_dict = {"asofdate":"2018-11-01"}
            out_result = []
            result = False
            selectedDate = params.get('selectedDate', False)

            selectedFromDate = params.get('selectedFromDate', False)
            selectedToDate = params.get('selectedToDate', False)
            start = datetime.strptime(selectedFromDate, "%Y-%m-%d")
            end = datetime.strptime(selectedToDate, "%Y-%m-%d")
            date_generated = [start + timedelta(days=x) for x in range(0, (end-start).days + 1)]

            for date in date_generated:
                self.dbManager.get_today_records(date.strftime("%Y-%m-%d"))

            todayDate = params.get('today', False)
            recipeValue = "1" #params.get('recipeValue', False)
            selectedMixingMenu = params.get('selectedItems', [])

            self.get_settings(recipeValue)
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

            myDb = self.mongo["mixing_staging_lineA_"+recipeValue]
            item_count = myDb.count_documents(find_dict)
            if item_count == 0:
                self.log.debug("Data not available in staging... Getting From Mains...")
                # self.dbManager.get_today_records(selectedDate)
                #find_dict = {"asofdate":selectedDate}
                item_count = myDb.count_documents(find_dict)
                print item_count
                self.log.debug(item_count)
            if item_count > 0 and len(selectedMixingMenu) > 0:
                dbresult = myDb.find(find_dict)
                _dict = {}
                for dt in dbresult:
                    if str(dt["Prop"]) in selectedMixingMenu:
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

                        batch = node["asofdate"] + "_" + str(elib.tonum(node["BatchCount"],'int'))
                        if selectedFromDate == selectedToDate:
                            batch = elib.tonum(node["BatchCount"],'int')
                        target_dict[prop]["Batches"].append(batch)

                        target_dict[prop]["LineBatch"].append({
                            "batch": batch,
                            "totalSetPoint": elib.tonum(node["TotalSetPoint"]),
                            "totalActualQty": elib.tonum(node["TotalActualQty"])
                        })
                        target_dict[prop]["Times"].append(node["AvgDuration"])

                        elib.dictIncrement3D(line_target, prop, batch, "TotalSetPoint", elib.tonum(node["TotalSetPoint"]))
                        elib.dictIncrement3D(line_target, prop, batch, "TotalActualQty", elib.tonum(node["TotalActualQty"]))


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
                    # 'Target Acheived' : '#979797',
                    # 'Target Missed': '#FAA524'
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
                    if prop in selectedMixingMenu:
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
                        isData = False
                        if len(donut_series) > 0:
                            isData = True
                        donutChartObj['isData'] = isData
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
                        xAxis = [ x for x in line_cat[prop] ]
                        all_data = sorted(target_dict[prop]["LineBatch"], key=lambda k: k['batch'])
                        
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
                        
                        out_result.append({"prop": prop, "data": final_target[prop]})


            return jsonify(Results= out_result)
        except Exception as e:
            self.log.exception("get_home Exception....")
            self.log.exception(e)

    def createHeaders(self, _list, prop):
        try:
            resultHeader = []
            results = ""

            for key in _list:
                s = ""
                s = key + prop
                resultHeader.append(s)
            results = elib.list2string("\t",resultHeader)

            return results
        except Exception as e:
            self.log.exception("createHeaders Exception....")
            self.log.exception(e)

    def downloadReport(self,out_list):
        try:
            params = self.get_params(request)

            selectedDate = params.get('selectedDate', False)
            todayDate = params.get('today', False)
            reportTitle = params.get("title", False)

            todayDate = datetime.now();
            dts_time = time.mktime(todayDate.timetuple()) * 1000

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
            
            out_pdf= FILE_PATH + 'Report_Demo_'+selectedDate+'.pdf'
            intermediate_html = FILE_PATH + 'intermediate.html'

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
            for key in self.reportKeys:
                for fattr in fileCompleted:
                    if fattr["name"] == key:
                        intermediate_html = FILE_PATH + 'intermediate.html'
                        self.to_html_pretty(fattr["html"], intermediate_html,fattr["name"], fattr["subtitle"], htmlToAdd, newhtmlToAdd, reportTitle, selectedDate)
                        htmlToAdd = ""
                        newhtmlToAdd = '<div style="margin-left:5px;margin-top:2px;border:1px solid white;">'\
                            '<div style="text-align:left;margin-left:1rem;margin-right:1rem;">'\
                                '<img src="' + SETTING_PATH + 'abz2_small.png" style="margin-right:100px;"/>'\
                                '<span style="margin-left:120px;text-align:center;color:#323232;font-size:22px;">'\
                                    '<span style="color:#323232;font-size:22px;margin-right:2rem;">'+reportTitle+'</span>'\
                                '</span>'\
                                '<span style="text-align:right;color:#323232;font-size:22px;margin-left:130px;">'\
                                    '<span style="color:#323232;font-size:22px;"> Generation Date ('+selectedDate+') </span>'\
                                '</span>'\
                            '</div>'\
                        '</div>'
                        # os.remove(fattr["txt"])
            options = {
                "orientation": "Landscape"
                }
            pdfkit.from_file(intermediate_html, out_pdf, options=options)
            return out_pdf
        except Exception as e:
            self.log.exception("downloadReport Exception....")
            self.log.exception(e)


    # original one
    # def downloadReport(self,out_list):
    #     try:
    #         params = self.get_params(request)

    #         selectedDate = params.get('selectedDate', False)
    #         todayDate = params.get('today', False)
    #         reportTitle = params.get("title", False)

    #         todayDate = datetime.now();
    #         dts_time = time.mktime(todayDate.timetuple()) * 1000

    #         reportHeader = ["Time", "BatchCount", "SetPoint", "ActualQty", "Deviation", "AvgDuration", "%&nbsp;Deviation", "SetDeviation", "SetDuration"]
    #         fileCompleted = []
    #         all_rows = []
    #         data_list = []
    #         txtfilename = FILE_PATH + "reports_all.txt"
    #         for node in out_list:
    #             headers = ["Time", "BatchCount", "TotalSetPoint", "TotalActualQty", "Deviation", "AvgDuration", "PercentDeviation", "SetDeviation", "SetDuration"]
    #             title = node["name"]
    #             txtfilename = FILE_PATH + node["name"].lower().replace(" ", "_") + ".txt"
    #             fileAttr = {"txt": txtfilename, "name":node["name"], "subtitle": "", "excel_name": FILE_PATH + node["name"].lower().replace(" ", "_")}
    #             first_row = []
    #             data_list = []
    #             all_rows = []
    #             for subnode in node["attr"]:
    #                 s = subnode["prop"].replace(" ", "")
    #                 first_row.append(s)
    #                 datalist = []
    #                 for row in subnode["data"]:
    #                     attr = {}
    #                     for hd in headers:
    #                         if hd == 'Time':
    #                             tm = row["MaxTime"].replace(" ", "&nbsp;")
    #                             attr.setdefault(hd, tm)
    #                         else:
    #                             attr.setdefault(hd, row[hd])
    #                     datalist.append(attr)
    #                 all_rows.append(datalist)

    #             all_length = len(all_rows)
    #             if all_length == 2:
    #                 first_list = all_rows[0]
    #                 second_list = all_rows[1]
    #                 big_list = second_list
    #                 small_list = first_list

    #                 first_len = len(first_list)
    #                 second_len = len(second_list)

    #                 if first_len > second_len:
    #                     big_list = first_list
    #                     small_list = second_list
    #                     s = "<span style='margin-right:180px;'>" + first_row[1] + "</span><span style='margin-left:220px;'>" +  first_row[0] +"</span>"
    #                     fileAttr["subtitle"] = s
    #                     data_list.append(self.createHeaders(reportHeader, "") + "\t" + self.createHeaders(reportHeader, "."))
    #                 else:
    #                     s = "<span style='margin-right:180px;'>" + first_row[0] + "</span><span style='margin-left:220px;'>" +  first_row[1] +"</span>"
    #                     fileAttr["subtitle"] = s
    #                     data_list.append(self.createHeaders(reportHeader, "") + "\t" + self.createHeaders(reportHeader, "."))

    #                 for big_row in big_list:
    #                     index = big_list.index(big_row)
    #                     s = ""
    #                     if index < len(small_list):
    #                         small_row = small_list[index]
    #                         for key in headers:
    #                             s += str(small_row[key])
    #                             s += "\t"
    #                         s += "\t" 
    #                     else:
    #                         for key in headers:
    #                             s += str("-")
    #                             s += "\t"
    #                         s += "\t" 
    #                     for key in headers:
    #                         s += str(big_row[key])
    #                         s += "\t"
    #                     data_list.append(s)
    #             else:
    #                 fileAttr["subtitle"] = s
    #                 data_list.append(elib.list2string("\t", reportHeader))
    #                 for row in all_rows:
    #                     for subrow in row:
    #                         s = ""
    #                         for key in headers:
    #                             s += str(subrow[key])
    #                             s += "\t"
    #                         data_list.append(s)
    #             fileCompleted.append(fileAttr)
    #             outF = open(txtfilename, "w")

    #             for line in data_list:
    #                 outF.write(line)
    #                 outF.write("\n")
    #                 rowcnt += 1
    #             outF.close()
            
    #         out_pdf= FILE_PATH + 'Report_Demo_'+selectedDate+'.pdf'
    #         intermediate_html = FILE_PATH + 'intermediate.html'

    #         htmlToAdd = '<div style="margin-left:10px;margin-top:20px;text-align:center;border:1px solid white;">'\
    #                         '<div style="text-center:left;margin-left:1rem;margin-right:1rem;margin-top:500px;">'\
    #                             '<img src="' + SETTING_PATH + 'abz2_big.png" style=""/>'\
    #                             '<div style="text-align:center;color:#323232;font-size:35px;margin-top:5px;">'\
    #                                 '<span style="color:#323232;font-size:35px;margin-right:2rem;">'+reportTitle+'</span>'\
    #                             '</div>'\
    #                             '<div style="text-align:center;color:#323232;font-size:35rem;margin-top:5px;">'\
    #                                 '<span style="color:#323232;font-size:30px;"> Generation Date ('+selectedDate+') </span>'\
    #                             '</div>'\
    #                         '</div>'\
    #                     '</div>'
    #         newhtmlToAdd = ''
    #         if os.path.exists(intermediate_html):
    #             os.remove(intermediate_html)
    #         for key in self.reportKeys:
    #             for fattr in fileCompleted:
    #                 if fattr["name"] == key:
    #                     df = pd.read_csv(fattr["txt"], delim_whitespace=True)
                        
    #                     intermediate_html = FILE_PATH + 'intermediate.html'
    #                     self.to_html_pretty(df, intermediate_html,fattr["name"], fattr["subtitle"], htmlToAdd, newhtmlToAdd, reportTitle, selectedDate)
    #                     htmlToAdd = ""
    #                     newhtmlToAdd = '<div style="margin-left:5px;margin-top:2px;border:1px solid white;">'\
    #                         '<div style="text-align:left;margin-left:1rem;margin-right:1rem;">'\
    #                             '<img src="' + SETTING_PATH + 'abz2_small.png" style="margin-right:100px;"/>'\
    #                             '<span style="margin-left:120px;text-align:center;color:#323232;font-size:22px;">'\
    #                                 '<span style="color:#323232;font-size:22px;margin-right:2rem;">'+reportTitle+'</span>'\
    #                             '</span>'\
    #                             '<span style="text-align:right;color:#323232;font-size:22px;margin-left:130px;">'\
    #                                 '<span style="color:#323232;font-size:22px;"> Generation Date ('+selectedDate+') </span>'\
    #                             '</span>'\
    #                         '</div>'\
    #                     '</div>'
    #                     # os.remove(fattr["txt"])
    #         options = {
    #             "orientation": "Landscape"
    #             }
    #         pdfkit.from_file(intermediate_html, out_pdf, options=options)
    #         return out_pdf
    #     except Exception as e:
    #         self.log.exception("downloadReport Exception....")
    #         self.log.exception(e)
    
    def to_html_pretty(self, df, filename='out.html', title='', subtitle='', htmlToAdd='', newhtmlToAdd='', reportTitle='', selectedDate=''):
        try:
            ht = ''
            if htmlToAdd != '':
                ht += htmlToAdd
            if title != '':
                ht += '<h1><img src="' + SETTING_PATH + 'abz2_small.png" style="margin-right:100px;margin-top:5px;"/>'
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
        except Exception as e:
            self.log.exception("to_html_pretty Exception....")
            self.log.exception(e)

    def get_reports(self,mode="view"):
        try:
            params = self.get_params(request)
            result = False
            
            find_dict = {"asofdate":"2018-11-01"}
            result = False
            selectedDate = params.get('selectedDate', False)

            selectedFromDate = params.get('selectedFromDate', False)
            selectedToDate = params.get('selectedToDate', False)
            start = datetime.strptime(selectedFromDate, "%Y-%m-%d")
            end = datetime.strptime(selectedToDate, "%Y-%m-%d")
            date_generated = [start + timedelta(days=x) for x in range(0, (end-start).days + 1)]

            for date in date_generated:
                self.dbManager.get_today_records(date.strftime("%Y-%m-%d"))

            todayDate = params.get('today', False)
            recipeValue = "1" #params.get('recipeValue', False)
            selectedMixingMenu = params.get('selectedItems', [])
            self.get_settings(recipeValue)
            if selectedFromDate == selectedToDate:
                find_dict = {"asofdate":selectedFromDate}
            else:
                find_dict = {
                            "asofdate": {
                                "$gte": selectedFromDate,
                                "$lte": selectedToDate
                            }
                        }

            myDb = self.mongo["mixing_staging_lineA_"+recipeValue]
            item_count = myDb.count_documents(find_dict)
            if item_count == 0:
                self.log.debug("Data not available in staging... Getting From Mains...")
                # self.dbManager.get_today_records(selectedDate)
                #find_dict = {"asofdate":selectedDate}
                item_count = myDb.count_documents(find_dict)
                self.log.debug(item_count)

            out_list = []

            if item_count > 0:
                dbresult = myDb.find(find_dict)
                _dict = {}
                # _seqDict = self.get_priority()

                for dt in dbresult:
                    if str(dt["Prop"]) in selectedMixingMenu:
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

                        batchCount = node["asofdate"] + "_" + str(elib.tonum(node["BatchCount"], 'int'))
                        target_dict[prop].setdefault(batchCount, {})
                        batchLabel = str(elib.tonum(node["BatchCount"], 'int'))
                        node["BatchCount"] = batchLabel
                        if '_id' in node:
                            del node['_id']
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
                        if prop in selectedMixingMenu:
                            propid = prop.lower().replace(" ", "_")
                            node["id"] = propid
                            finalList = [] 
                            for bt in sorted(target_dict.get(prop, {}).keys()):
                                finalList.append(target_dict[prop][bt])
                            node["data"] = sorted(finalList, key = lambda i: i['MaxTime']) 
                            final_target[key].append(node)

                out_list = []
                for key in self.reportKeys:
                    if len(final_target[key]) > 0:
                        out_list.append({
                            "name": key,
                            "attr" : final_target[key]
                        })

            if mode == "view":
                return jsonify(Results = out_list)
            else:
                return out_list
        except Exception as e:
            self.log.exception("get_reports Exception....")
            self.log.exception(e)

    def save_reports(self):
        try:
            out_list = self.get_reports(mode="download")
            filename = self.downloadReport(out_list)
            path = FILE_PATH
            uuidstr = str(uuid.uuid4())
            filepath = filename

            zip_name = "Reports_"+uuidstr+".zip"
            zip_file = path + zip_name
            self.log.debug('Creating archive ' + zip_name)
            zf = zipfile.ZipFile(zip_file, mode='w')
            compression = zipfile.ZIP_DEFLATED

            zf.write(filepath, os.path.basename(filepath), compress_type=compression)
            os.remove(filepath)

            return jsonify(Results = zip_name)
        except Exception as e:
            self.log.exception("save_reports Exception....")
            self.log.exception(e)
    
    def save_dashboard_report(self):
        try:
            filename = self.get_dashboard_home()
            path = FILE_PATH
            uuidstr = str(uuid.uuid4())
            filepath = filename

            zip_name = "Mixing_Dashboard_"+uuidstr+".zip"
            zip_file = path + zip_name
            print 'Creating archive ' + zip_name
            zf = zipfile.ZipFile(zip_file, mode='w')
            compression = zipfile.ZIP_DEFLATED

            zf.write(filepath, os.path.basename(filepath), compress_type=compression)
            os.remove(filepath)
            return jsonify(Results = zip_name)
        except Exception as e:
            self.log.exception("save_dashboard_reports Exception....")
            self.log.exception(e)
    
    def get_dashboard_home(self):
        try:
            params = self.get_params(request)
            
            find_dict = {"asofdate":"2018-11-01"}
            out_result = []
            result = False
            selectedDate = params.get('selectedDate', False)

            selectedFromDate = params.get('selectedFromDate', False)
            selectedToDate = params.get('selectedToDate', False)
            start = datetime.strptime(selectedFromDate, "%Y-%m-%d")
            end = datetime.strptime(selectedToDate, "%Y-%m-%d")
            date_generated = [start + timedelta(days=x) for x in range(0, (end-start).days + 1)]

            for date in date_generated:
                self.dbManager.get_today_records(date.strftime("%Y-%m-%d"))

            todayDate = params.get('today', False)
            recipeValue = "1" #params.get('recipeValue', False)
            selectedMixingMenu = params.get('selectedItems', [])

            self.get_settings(recipeValue)
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

            myDb = self.mongo["mixing_staging_lineA_"+recipeValue]
            item_count = myDb.count_documents(find_dict)
            if item_count == 0:
                self.log.debug("Data not available in staging... Getting From Mains...")
                # self.dbManager.get_today_records(selectedDate)
                #find_dict = {"asofdate":selectedDate}
                item_count = myDb.count_documents(find_dict)
                print item_count
                self.log.debug(item_count)
            if item_count > 0 and len(selectedMixingMenu) > 0:
                dbresult = myDb.find(find_dict)
                _dict = {}
                for dt in dbresult:
                    if str(dt["Prop"]) in selectedMixingMenu:
                        if str(dt["Prop"]) not in _dict.keys():
                            _dict.setdefault(str(dt["Prop"]), [])
                        _dict[str(dt["Prop"])].append(dt)

            target_dict = {}
            final_target = {}
            line_target = {}
            out_result = []
            line_cat = {}
            _seqDict = {}
            html_list = []

            if _dict != {}:

                for prop in _dict:
                    target_dict.setdefault(prop, {})
                    final_target.setdefault(prop, {})
                    target_dict[prop].setdefault("Batches", [])
                    target_dict[prop].setdefault("Times", [])
                    target_dict[prop].setdefault("LineBatch", [])
                    for node in _dict[prop]:
                        elib.dictIncrement(target_dict, prop, "TotalSetPoint", elib.tonum(node["TotalSetPoint"]))
                        elib.dictIncrement(target_dict, prop, "TotalActualQty", elib.tonum(node["TotalActualQty"]))

                        batch = node["asofdate"] + "_" + str(elib.tonum(node["BatchCount"],'int'))
                        if selectedFromDate == selectedToDate:
                            batch = elib.tonum(node["BatchCount"],'int')
                        target_dict[prop]["Batches"].append(batch)

                        target_dict[prop]["LineBatch"].append({
                            "batch": batch,
                            "totalSetPoint": elib.tonum(node["TotalSetPoint"]),
                            "totalActualQty": elib.tonum(node["TotalActualQty"])
                        })
                        target_dict[prop]["Times"].append(node["AvgDuration"])

                        elib.dictIncrement3D(line_target, prop, batch, "TotalSetPoint", elib.tonum(node["TotalSetPoint"]))
                        elib.dictIncrement3D(line_target, prop, batch, "TotalActualQty", elib.tonum(node["TotalActualQty"]))

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
                    if prop in selectedMixingMenu:
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

                        if selectedFromDate == selectedToDate:

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
                                '<img src="' + SETTING_PATH + 'abz2_big.png" style=""/>'\
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
                if prop in selectedMixingMenu:
                    propname = prop.lower().replace(" ", "_")
                    piename = FILE_PATH + "pie_"+str(propname)+".png"
                    linename = FILE_PATH + "line_"+str(propname)+".png"
                    if selectedFromDate != selectedToDate:
                        linename = ""

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
                                    '</div>'

                    if selectedFromDate == selectedToDate:
                        ht += '<div class="flex flex--col flex__item__3 custom-holder-2" style="width:70%;">'\
                            '<div class="flex flex--row flex--middle cnt-sub-2" style="height:25px; width:100%;">'\
                                '<div class="hdr-txt3 pointer" style="margin-left:1rem;padding-left: 1rem;padding-right:1rem;">Batch(Kg) Trend</div>'\
                            '</div>'\
                            '<div class="flex flex__item" style="margin:10px;width:100%;">'\
                                '<img height="250" src="'+linename+'"/>'\
                            '</div>'\
                        '</div>'

                    ht += '</div>'\
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
            self.log.debug(intermediate_html)
            self.log.debug(out_pdf)
            pdfkit.from_file(intermediate_html, out_pdf, options=options)

            for img in imagesToDelete:
                if(os.path.exists(img)):
                    os.remove(img)

            return out_pdf
        except Exception as e:
            self.log.exception("Save_reports Exception....")
            self.log.exception(e)
    
    def htmltoImage(self, ht, chartType):
        print ht+".html",'---to---', ht+'.png'
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

        imgkit.from_file(FILE_PATH + htmlname, FILE_PATH + pngname, options=options)
        if(os.path.exists(FILE_PATH + htmlname)):
            os.remove(FILE_PATH + htmlname)

    def to_html_pretty_2(self, ht, filename='out.html', title='', htmlToAdd="", reportTitle = '', selectedDate=''):
        htm = ''
        if htmlToAdd != "":
            htm += htmlToAdd
        if title != '':
            htm += '<h1><div class="flex flex--col flex__item flex--center">'
            htm += '<span style="text-align:left;width:20%;"> <img src="' + SETTING_PATH + 'abz2_small.png" align:left/></span>'
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
        
# while True:
#     schedule.run_pending()
    # time.sleep(1)
