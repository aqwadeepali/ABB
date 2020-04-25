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
from stage_bori_data import BRun
import ast
import operator
import copy

from logging import getLogger, INFO, ERROR, WARNING, CRITICAL, NOTSET, DEBUG

# path_wkthmltopdf = r'C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe'
# config = pdfkit.configuration(wkhtmltopdf=path_wkthmltopdf)

SETTING_PATH = str(os.path.realpath(__file__))
SETTING_PATH = SETTING_PATH.replace("bori_services.pyc", "")
SETTING_PATH = SETTING_PATH.replace("bori_services.pyo", "")
SETTING_PATH = SETTING_PATH.replace("bori_services.py", "")
SETTING_PATH = SETTING_PATH + "data/"

FILE_PATH = str(os.path.realpath(__file__))
FILE_PATH = FILE_PATH.replace("bori_services.pyc", "")
FILE_PATH = FILE_PATH.replace("bori_services.pyo", "")
FILE_PATH = FILE_PATH.replace("bori_services.py", "")
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

def register_services(app, WSGI_PATH_PREFIX):
    BoriServices(app, WSGI_PATH_PREFIX)

class BoriServices:

    def __init__(self, app, API):
        self.app = app
        self.API = API
        self.dManagers = self.app.config["Managers"]["DataManager"]
        self.mongoManger = self.dManagers.get_connection()

        self.mongo = self.mongoManger["analyse_db"]
        # schedule.every().day.at("20:50").do(job)
        # schedule.every(2).minutes.do(job)

        # print self.mongo.collection_names()
        # print '--------------------------------------------------------------'

        self.dbManager = BRun()
        self.log = getLogger()
        # self.get_settings()

        # self.app.add_url_rule(API + '/services/sendfresponse', 'sendfresponse', self.sendfresponse, methods=['GET','POST'])

        # # Home API
        self.app.add_url_rule(API + '/services/getborireport', 'getborireport', self.get_bori_report, methods=['POST'])
        self.app.add_url_rule(API + '/services/saveborireport', 'saveborireport', self.save_bori_report, methods=['POST'])

    def get_settings(self):
        try:
            print "Reading Settings"
            keys = ""
            reportKeys = ""
            reader = csv.DictReader(open(SETTING_PATH + 'bori_settings.txt'), delimiter="\t")
            for row in reader:
                if row["Field"] == "REPORTKEYS":
                    reportKeys = ast.literal_eval(row["Value"])
                if row["Field"] == "SEQ":
                    keys = row["Value"]
     
            self.seqKeys = keys
            self.reportKeys = reportKeys
        except Exception as e:
            print "Exception in reading settings"
            self.log.exception("Read Settings Exception....")
            self.log.exception(e)
        finally:
            print "Exception Finally in reading settings"
            self.log.exception("Read Settings Exception....")


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

    def get_bori_report(self, mode="view"):
        try:
            params = self.get_params(request)
            self.get_settings()
            timerange = []
            result = False
            selectedFromDate = params.get('selectedFromDate', False)
            selectedToDate = params.get('selectedToDate', False)
            start = datetime.strptime(selectedFromDate, "%Y-%m-%d")
            end = datetime.strptime(selectedToDate, "%Y-%m-%d")
            date_generated = [start + timedelta(days=x) for x in range(0, (end-start).days + 1)]

            if selectedFromDate == selectedToDate:
                if date_generated == []:
                    date_generated = [start]   

            for dateparam in date_generated:
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
            # print timerange
            out_result = []
            footer_data = {}
            all_footer = {}
            columns = []
            _dict = {}

            myDb = self.mongo["bori_staging"]

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
                            propname = prop.replace("8", "eight")
                            row.setdefault(propname+"_Set", elib.tonum(all_result[tm][bt].get(prop+"_Set", 0),'int'))
                            row.setdefault(propname+"_Initial", elib.tonum(all_result[tm][bt].get(prop+"_Initial", 0),'int'))
                            row.setdefault(propname+"_Actual", elib.tonum(all_result[tm][bt].get(prop+"_Actual", 0),'int'))
                            row.setdefault(propname+"_Final", elib.tonum(all_result[tm][bt].get(prop+"_Final", 0),'int'))
                        out_result.append(row)

                all_footer = {}
                for prop in self.reportKeys:
                    propname = prop.replace("8", "eight")
                    all_footer.setdefault(propname+"_Total",footer_data.get(prop+"_Total", 0))
                all_footer.setdefault("AllTotal", allTotalFinal)

                columns = [{
                    "field": "Batch",
                    "header": "Batch",
                    "colspan": 1
                }]
                for key in self.reportKeys:
                    propname = key.replace("8", "eight")
                    columns.append({
                        "field" : key,
                        "header": propname+"_Total",
                        "colspan": 3
                    })


            if mode == "view":  
                return jsonify(Results= {"data": out_result, "footer_data": all_footer, "columns": columns})
            else:
                return {"data": out_result, "footer_data": footer_data, 'allFinal': allTotalFinal}
        except Exception as e:
            self.log.exception("get_bori_report Exception....")
            self.log.exception(e)
        finally:
            self.log.exception("get_bori_report Exception....")

    def find2ndMax(self, _list, lastMax):
        maxNum = _list[0]
        secondMax = ""
        for item in _list:
            if item != lastMax:
                if maxNum < item:
                    secondMax = copy.deepcopy(maxNum)
                    maxNum = item
        return maxNum

    def downloadBoriReport(self, out_data):
        try:
            params = self.get_params(request)

            dateparam = params.get('selectedDate', False)
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
                newmode = mode.replace("8", "eight")
                for node in subheaders:
                    headers.append(node)
                    keyheaders.append(newmode.lower().replace(" ", "_") + "_" + headkeys[subheaders.index(node)])

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
            ht += '<td colspan="2" style="">Total All: '+str(elib.tonum(out_data["allFinal"],'int'))+'</td>'
            for prop in self.reportKeys:
                ht += '<td colspan="3" style="">Total: '+str(footer_data.get(prop+"_Total",0))+'</td>'

            ht += '</tbody></table>'

            out_pdf= FILE_PATH + 'Bori_Report_'+selectedDate+'.pdf'
            intermediate_html = FILE_PATH + 'intermediate.html'
            reportTitle = "Bori Daily Report"

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
            self.to_html_pretty_report(ht, intermediate_html, "Bori Daily Report", htmlToAdd, reportTitle, selectedDate)
            htmlToAdd = ""
            # options = {'orientation': 'Landscape'}
            # pdfkit.from_file(intermediate_html, out_pdf, configuration=config)
            pdfkit.from_file(intermediate_html, out_pdf)
            return out_pdf
        except Exception as e:
            self.log.exception("downloadBoriReport Exception....")
            self.log.exception(e)
        finally:
            self.log.exception("downloadBoriReport Exception....")

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
        finally:
            self.log.exception("to_html_pretty_report Exception....")

    def save_bori_report(self):
        try:
            self.log.debug("Saving Report...")
            out_list = self.get_bori_report("download")
            filename = self.downloadBoriReport(out_list)
            path = FILE_PATH
            uuidstr = str(uuid.uuid4())
            filepath = filename

            zip_name = "Bori_Reports_"+uuidstr+".zip"
            zip_file = path + zip_name
            self.log.debug('Creating archive ' + zip_name)
            zf = zipfile.ZipFile(zip_file, mode='w')
            compression = zipfile.ZIP_DEFLATED

            zf.write(filepath, os.path.basename(filepath), compress_type=compression)
            os.remove(filepath)

            return jsonify(Results = zip_name)
        except Exception as e:
            self.log.exception("save_bori_report Exception....")
            self.log.exception(e)
        finally:
            self.log.exception("save_bori_report Exception....")
