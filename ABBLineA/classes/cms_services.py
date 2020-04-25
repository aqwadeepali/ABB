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
from stage_cms_data import CMSRun
import ast
import operator

from logging import getLogger, INFO, ERROR, WARNING, CRITICAL, NOTSET, DEBUG

# path_wkthmltopdf = r'C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe'
# config = pdfkit.configuration(wkhtmltopdf=path_wkthmltopdf)

SETTING_PATH = str(os.path.realpath(__file__))
SETTING_PATH = SETTING_PATH.replace("cms_services.pyc", "")
SETTING_PATH = SETTING_PATH.replace("cms_services.pyo", "")
SETTING_PATH = SETTING_PATH.replace("cms_services.py", "")
SETTING_PATH = SETTING_PATH + "data/"

FILE_PATH = str(os.path.realpath(__file__))
FILE_PATH = FILE_PATH.replace("cms_services.pyc", "")
FILE_PATH = FILE_PATH.replace("cms_services.pyo", "")
FILE_PATH = FILE_PATH.replace("cms_services.py", "")
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


HTML_TEMPLATE2 = '</body></html>'

def register_services(app, WSGI_PATH_PREFIX):
    CMSServices(app, WSGI_PATH_PREFIX)

class CMSServices:

    def __init__(self, app, API):
        self.app = app
        self.API = API
        self.dManagers = self.app.config["Managers"]["DataManager"]
        self.mongoManger = self.dManagers.get_connection()

        self.mongo = self.mongoManger["analyse_db"]

        #print self.mongo.collection_names()
        #print '--------------------------------------------------------------'

        self.dbManager = CMSRun()
        self.log = getLogger()
        # self.get_settings()

        # self.app.add_url_rule(API + '/services/sendfresponse', 'sendfresponse', self.sendfresponse, methods=['GET','POST'])

        # # Home API
        self.app.add_url_rule(API + '/services/getcmshome', 'getcmshome', self.get_cms_home, methods=['POST'])
        self.app.add_url_rule(API + '/services/getcmsreport', 'getcmsreport', self.get_cms_report, methods=['POST'])
        self.app.add_url_rule(API + '/services/savecmsreport', 'savecmsreport', self.save_cms_report, methods=['POST'])

    def get_settings(self):
        try:
            print "Reading Settings"
            keys = ""
            reportKeys = ""
            reportManager = ""
            reader = csv.DictReader(open(SETTING_PATH + 'cms_settings.txt'), delimiter="\t")
            for row in reader:
                if row["Field"] == "REPORTKEYS":
                    reportKeys = ast.literal_eval(row["Value"])
                if row["Field"] == "SEQ":
                    keys = row["Value"]
     
            self.seqKeys = keys
            self.reportKeys = reportKeys
        except Exception as e:
            self.log.exception("Read Settings Exception....")
            self.log.exception(e)
        finally:
            self.log.exception("Read Settings Exception....")


    def get_params(self, request):
        return request.json if (request.method == 'POST') else request.args

    def get_cms_home(self):
        try:
            result = {}
            params = self.get_params(request)
            self.get_settings()
            dateparam = params.get('selectedDate', False)
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

            myDb = self.mongo["cms_staging"]
            item_count = myDb.count_documents(find_dict)
            if item_count == 0:
                self.log.debug("Data not available in staging... Getting From Mains...")
                self.dbManager.get_today_records(selectedDate)
                find_dict = {"asofdate":selectedDate}
                item_count = myDb.count_documents(find_dict)
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
            if item_count > 0:
                dbresult = myDb.find(find_dict)
                for dt in dbresult:
                    if dt != []:        
                        if str(dt["Prop"]) not in _dict.keys():
                            _dict.setdefault(str(dt["Prop"]), [])
                        _dict[str(dt["Prop"])].append(dt)
            find_dict = {"asofdate":todayDate}
            myDb = self.mongo["cms_staging"]
            item_count = myDb.count_documents(find_dict)

            if item_count == 0:
                self.log.debug("Data not available in staging... Getting From Mains...")
                self.dbManager.get_today_records(todayDate)
                find_dict = {"asofdate":todayDate}
                item_count = myDb.count_documents(find_dict)
            self.log.debug(item_count)
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

                    chartObjQty = {}
                    chartObjQty["categories"] = sorted(line_series_qty.keys())
                    chartObjQty['charttype'] = 'linechart'
                    chartObjQty['id'] = 'line_qty_'+prop.lower().replace(' ', '_')
                    chartObjQty['series'] = chartQtyResult
                    chartObjQty['isData'] = isData

                    chartRatioResult = []
                    isData = False
                    for leg in _legend2:
                        if len(line_result_ratio[leg]['data']) > 0:
                            isData = True
                        chartRatioResult.append(line_result_ratio[leg])

                    chartObjRatio = {}
                    chartObjRatio["categories"] = sorted(line_series_ratio.keys())
                    chartObjRatio['charttype'] = 'linechart'
                    chartObjRatio['id'] = 'line_ratio_'+prop.lower().replace(' ', '_')
                    chartObjRatio['series'] = chartRatioResult
                    chartObjRatio['isData'] = isData

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
            return jsonify(Results=out_result)
        except Exception as e:
            self.log.exception("get_cms_home Exception....")
            self.log.exception(e)
        finally:
            self.log.exception("get_cms_home Exception....")

    def get_cms_report(self, mode="view"):
        try:
            result = {}
            params = self.get_params(request)
            self.get_settings()
            dateparam = params.get('selectedDate', False)
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

            myDb = self.mongo["cms_staging"]
            item_count = myDb.count_documents(find_dict)
            if item_count == 0:
                self.log.debug("Data not available in staging... Getting From Mains...")
                self.dbManager.get_today_records(selectedDate)
                find_dict = {"asofdate":selectedDate}
                item_count = myDb.count_documents(find_dict)
            self.log.debug(item_count)

            _dict = {}
            if item_count > 0:
                dbresult = myDb.find(find_dict)
                for dt in dbresult:
                    if dt != []:        
                        if str(dt["Prop"]) not in _dict.keys():
                            _dict.setdefault(str(dt["Prop"]), [])
                        _dict[str(dt["Prop"])].append(dt)
            find_dict = {"asofdate":todayDate}
            myDb = self.mongo["cms_staging"]
            item_count = myDb.count_documents(find_dict)
            
            if item_count == 0:
                self.log.debug("Data not available in staging... Getting From Mains...")
                self.dbManager.get_today_records(todayDate)
                find_dict = {"asofdate":todayDate}
                item_count = myDb.count_documents(find_dict)
            self.log.debug(item_count)
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

            if mode == "view":
                return jsonify(Results=out_result)
            else:
                return out_result
        except Exception as e:
            self.log.exception("get_cms_report Exception....")
            self.log.exception(e)
        finally:
            self.log.exception("get_cms_report Exception....")

    def downloadCMSReport(self, out_report):
        try:
            params = self.get_params(request)
            selectedDate = params.get('selectedDate', False)
            todayDate = params.get('today', False)
            reportTitle = params.get("title", False)

            todayDate = datetime.now();
            dts_time = time.mktime(todayDate.timetuple()) * 1000
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
            
            df = pd.read_csv(txtfilename, delimiter="\t", delim_whitespace=False)
            intermediate_html = 'intermediate.html'
            self.to_html_pretty(df, intermediate_html, "CMS Daily Report", htmlToAdd, reportTitle, selectedDate)
            htmlToAdd = ""
            os.remove(txtfilename)
            # pdfkit.from_file(intermediate_html, out_pdf, configuration=config)
            pdfkit.from_file(intermediate_html, out_pdf)
            return out_pdf
        except Exception as e:
            self.log.exception("downloadCMSReport Exception....")
            self.log.exception(e)
        finally:
            self.log.exception("downloadCMSReport Exception....")

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
        finally:
            self.log.exception("to_html_pretty Exception....")

    def save_cms_report(self):
        try:
            self.log.debug("Saving Report...")
            out_list = self.get_cms_report(mode="download")
            filename = self.downloadCMSReport(out_list)
            path = FILE_PATH
            uuidstr = str(uuid.uuid4())
            filepath = filename

            zip_name = "CMS_Reports_"+uuidstr+".zip"
            zip_file = path + zip_name
            self.log.debug('Creating archive ' + zip_name)
            zf = zipfile.ZipFile(zip_file, mode='w')
            compression = zipfile.ZIP_DEFLATED

            zf.write(filepath, os.path.basename(filepath), compress_type=compression)
            os.remove(filepath)
            return jsonify(Results = zip_name)

        except Exception as e:
            self.log.exception("save_cms_report Exception....")
            self.log.exception(e)
        finally:
            self.log.exception("save_cms_report Exception....")
        
