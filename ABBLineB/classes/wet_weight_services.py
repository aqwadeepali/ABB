import os, json
import elib
import datetime
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
from stage_wet_weight_data import WWRun
import ast
import operator

# path_wkthmltopdf = r'C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe'
# config = pdfkit.configuration(wkhtmltopdf=path_wkthmltopdf)

SETTING_PATH = str(os.path.realpath(__file__))
SETTING_PATH = SETTING_PATH.replace("wet_weight_services.pyc", "")
SETTING_PATH = SETTING_PATH.replace("wet_weight_services.pyo", "")
SETTING_PATH = SETTING_PATH.replace("wet_weight_services.py", "")
SETTING_PATH = SETTING_PATH + "data/"

FILE_PATH = str(os.path.realpath(__file__))
FILE_PATH = FILE_PATH.replace("wet_weight_services.pyc", "")
FILE_PATH = FILE_PATH.replace("wet_weight_services.pyo", "")
FILE_PATH = FILE_PATH.replace("wet_weight_services.py", "")
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

        self.dbManager = WWRun()
        # self.get_settings()

        # self.app.add_url_rule(API + '/services/sendfresponse', 'sendfresponse', self.sendfresponse, methods=['GET','POST'])

        # # Home API
        self.app.add_url_rule(API + '/services/getwwhome', 'getwwhome', self.get_ww_home, methods=['POST'])
        self.app.add_url_rule(API + '/services/getwwreport', 'getwwreport', self.get_ww_report, methods=['POST'])
        self.app.add_url_rule(API + '/services/savewwreport', 'savewwreport', self.save_ww_report, methods=['POST'])

    def get_settings(self):
        print "Reading Settings"
        keys = ""
        reportKeys = ""
        reportManager = ""
        reader = csv.DictReader(open(SETTING_PATH + 'wet_weight_settings.txt'), delimiter="\t")
        for row in reader:
            if row["Field"] == "REPORTKEYS":
                reportKeys = ast.literal_eval(row["Value"])
            if row["Field"] == "SEQ":
                keys = row["Value"]
 
        self.seqKeys = keys
        self.reportKeys = reportKeys


    def get_params(self, request):
        return request.json if (request.method == 'POST') else request.args

    def get_ww_home(self):
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

        out_result = []

        find_dict = {"asofdate":selectedDate}

        myDb = self.mongo["wet_weight_staging"]
        item_count = myDb.count_documents(find_dict)
        if item_count == 0:
            print "Data not available in staging... Getting From Mains..."
            self.dbManager.get_today_records(selectedDate)
            find_dict = {"asofdate":selectedDate}
            item_count = myDb.count_documents(find_dict)
        print item_count
        line_color = {
            'ContinuousWeight': '#662441',
            'Totaliser': '#e34566',
            'SampleWeight': '#74d600'
            # 'CreamRatioActual': '#08c'
        }
        _legend1 = {
            'ContinuousWeight':{
                'name' : 'Continuous WT',
                # 'color' : '#3eb308',
                'color' : line_color['ContinuousWeight'],
                'dashStyle' : 'Solid',
                'type' : 'line',
                'y':0,
                'visible' : True
            },
            'Totaliser' : {
                'name' : 'Totalizer',
                # 'color' : '#3eb308',
                'color' : line_color['Totaliser'],
                'dashStyle' : 'Solid',
                'type' : 'line',
                'y':0,
                'visible' : True
            }
        }
        _legend2 = {
            'SampleWeight':{
                'name' : 'Sample Weight',
                # 'color' : '#3eb308',
                'color' : line_color['SampleWeight'],
                'dashStyle' : 'Solid',
                'type' : 'column',
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
        myDb = self.mongo["wet_weight_staging"]
        item_count = myDb.count_documents(find_dict)
        print item_count,'---',find_dict
        if item_count == 0:
            print "Data not available in staging... Getting From Mains..."
            self.dbManager.get_today_records(todayDate)
            find_dict = {"asofdate":todayDate}
            item_count = myDb.count_documents(find_dict)
        print item_count
        if item_count > 0:
            dbresult = myDb.find(find_dict)            
            for dt in dbresult:
                if dt != []:        
                    if str(dt["Prop"]) not in _dict.keys():
                        _dict.setdefault(str(dt["Prop"]), [])
                    _dict[str(dt["Prop"])].append(dt)

        if _dict != {}:

            target_dict = {}
            totaliser = {}
            final_dict = {}
            minNum = 10000
            maxNum = -1
            maxTime = ""
            minTime = ""
            sminNum = 10000
            smaxNum = -1
            smaxTime = ""
            sminTime = ""
            result = {}
            wt_data = {}
            sample_data = {}
            wt_result = {}
            sample_result = {}
            wt_series = {}
            sample_series = {}
            sample_bit_data = {}
            for leg in _legend1:
                wt_result[leg] = {
                    'name': _legend1[leg]['name'],
                    'data': [],
                    'yAxis': _legend1[leg]['y'],
                    'type': _legend1[leg]['type'],
                    'color': _legend1[leg]['color'],
                    'visible': _legend1[leg]['visible']
                }
            for leg in _legend2:
                sample_result[leg] = {
                    'name': _legend2[leg]['name'],
                    'data': [],
                    'yAxis': _legend2[leg]['y'],
                    'type': _legend2[leg]['type'],
                    'color': _legend2[leg]['color'],
                    'visible': _legend2[leg]['visible']
                }
            # for prop in self.reportKeys:
            stage_data = _dict["Wet Weight"]
            all_time = []
            for node in stage_data:
                xTime = node["Time"]
                xDateTime =  xTime.strftime("%Y-%m-%d %H:%M")
                cont_weight = elib.tonum(node["ContinuousWeight"])
                totalizer = elib.tonum(node["Totaliser"],'float', 0)

                sample_weight = elib.tonum(node["SampleWeight"])
                sample_bit = elib.tonum(node["SampleBit"], 'int')

                if xTime not in totaliser:
                    totaliser.setdefault(xTime, totalizer)
                else:
                    totaliser[xTime] = totalizer

                if(cont_weight > 0):
                    elib.dictIncrement1D(target_dict, "ContinuousWeight", [cont_weight])
                else:
                    if "ContinuousWeight" not in target_dict:
                        target_dict.setdefault("ContinuousWeight", [0])

                
                all_time.append(xTime)
                elib.dictIncrement(sample_bit_data, xTime, str(sample_bit), sample_weight)
                if sample_bit == 1:
                    if(sample_weight > 0):
                        elib.dictIncrement1D(target_dict, "SampleWeight", [sample_weight])

                    else:
                        if "SampleWeight" not in target_dict:
                            target_dict.setdefault("SampleWeight", [0])

                    
                
                    if sample_weight > 0:
                        elib.dictIncrement(sample_data, xDateTime, "SampleWeight", [sample_weight])
                    else:
                        if xDateTime not in sample_data.keys():
                            sample_data.setdefault(xDateTime, {}).setdefault("SampleWeight", [0])
                        elif "SampleWeight" not in sample_data[xDateTime].keys():
                            sample_data[xDateTime].setdefault("SampleWeight", [0])
                else:
                    if "SampleWeight" not in target_dict:
                        target_dict.setdefault("SampleWeight", [0])


                if xDateTime in timerange:
                    if cont_weight > 0:
                        elib.dictIncrement(wt_data, xDateTime, "ContinuousWeight", [cont_weight])
                    else:
                        if xDateTime not in wt_data.keys():
                            wt_data.setdefault(xDateTime, {}).setdefault("ContinuousWeight", [0])
                        elif "ContinuousWeight" not in wt_data[xDateTime].keys():
                            wt_data[xDateTime].setdefault("ContinuousWeight", [0])
                    if totalizer > 0:
                        elib.dictIncrement(wt_data, xDateTime, "Totaliser", [totalizer])
                    else:
                        if xDateTime not in wt_data.keys():
                            wt_data.setdefault(xDateTime, {}).setdefault("Totaliser", [0])
                        elif "Totaliser" not in wt_data[xDateTime].keys():
                            wt_data[xDateTime].setdefault("Totaliser", [0])

            for xtime in wt_data.keys():
                wt_series.setdefault(xtime,{})
                for key in wt_data[xtime]:
                    avg = sum(wt_data[xtime][key]) / len(wt_data[xtime][key])
                    wt_series[xtime].setdefault(key, avg)
                    if key == "ContinuousWeight":
                        if maxNum < avg:
                            maxNum = avg
                            maxTime = xtime
                        if minNum >= avg:
                            minNum = avg
                            minTime = xtime
                    if key == "SampleWeight":
                        if smaxNum < avg:
                            smaxNum = avg
                            smaxTime = xtime
                        if sminNum >= avg:
                            sminNum = avg
                            sminTime = xtime
            cnt = 0
            zeroCnt = 1
            totalW = 0
            bit_data = {}
            for xtime in sorted(all_time):
                for key in sample_bit_data[xtime]:
                    if key == "1":
                        if zeroCnt != 0:
                            cnt += 1
                            zeroCnt = 0
                            totalW = sample_bit_data[xtime][key]
                        if str(cnt) not in bit_data:
                            bit_data.setdefault(str(cnt), totalW)
                        else:
                            bit_data[str(cnt)] = totalW
                    else:
                        totalW = 0
                        zeroCnt = 1
                        
            for xtime in wt_series:
                for leg in _legend1:
                    wt_result[leg]["data"].append({
                        "category": xtime,
                        "y": elib.rnd(wt_series[xtime][leg],2)
                    })
            all_bits = [ int(x) for x in bit_data.keys() ]
            for bit in sorted(all_bits):
                sample_result["SampleWeight"]["data"].append({
                    "category": str(bit),
                    "y": elib.rnd(bit_data[str(bit)],2)
                })

            chartQtyResult = []
            isData = False
            for leg in _legend1:
                if len(wt_result[leg]['data']) > 0:
                    isData = True
                chartQtyResult.append(wt_result[leg])

            chartObjQty = {}
            chartObjQty["categories"] = sorted(wt_series.keys())
            chartObjQty['charttype'] = 'linechart'
            chartObjQty['id'] = 'wet_weight'
            chartObjQty['series'] = chartQtyResult
            chartObjQty['isData'] = isData

            chartResult = []
            isData = False
            for leg in _legend2:
                if len(sample_result[leg]['data']) > 0:
                    isData = True
                chartResult.append(sample_result[leg])

            chartObjRatio = {}
            chartObjRatio["categories"] = sorted(all_bits)
            chartObjRatio['charttype'] = 'linechart'
            chartObjRatio['id'] = 'sample_weight'
            chartObjRatio['series'] = chartResult
            chartObjRatio['isData'] = isData

            average_wt = sum(target_dict["ContinuousWeight"])/ len(target_dict["ContinuousWeight"])
            average_sample = sum(target_dict["SampleWeight"])/ len(target_dict["SampleWeight"])
            total_sample = sum(target_dict["SampleWeight"])
            totalTotaliser = 0
            for x in sorted(totaliser.keys()):
                totalTotaliser = totaliser[x]

            final_dict = {}
            final_dict["line_chart_wt_weight"] = chartObjQty
            final_dict["line_chart_sample_weight"] = chartObjRatio

            final_dict.setdefault("AverageWt", elib.rnd(elib.tonum(average_wt,"float"),2))
            final_dict.setdefault("AverageSample", elib.rnd(elib.tonum(average_sample,"float"),2))
            final_dict.setdefault("TotalSample", total_sample)
            final_dict.setdefault("TotalTotaliser", totalTotaliser)
            final_dict.setdefault("Max", elib.rnd(maxNum, 2))
            final_dict.setdefault("Min", elib.rnd(minNum, 2))
            final_dict.setdefault("MaxTime", maxTime)
            final_dict.setdefault("MinTime", minTime)
            final_dict.setdefault("SMax", elib.rnd(smaxNum, 2))
            final_dict.setdefault("SMin", elib.rnd(sminNum, 2))
            final_dict.setdefault("SMaxTime", smaxTime)
            final_dict.setdefault("SMinTime", sminTime)

            out_result.append({"prop": "Wet Weight", "data": final_dict})
        return jsonify(Results=out_result)

    def get_ww_report(self, mode="view"):
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
            
        out_result = {}

        find_dict = {"asofdate":selectedDate}

        myDb = self.mongo["wet_weight_staging"]
        item_count = myDb.count_documents(find_dict)
        if item_count == 0:
            print "Data not available in staging... Getting From Mains..."
            self.dbManager.get_today_records(selectedDate)
            find_dict = {"asofdate":selectedDate}
            item_count = myDb.count_documents(find_dict)
        print item_count

        _dict = {}
        if item_count > 0:
            dbresult = myDb.find(find_dict)
            for dt in dbresult:
                if dt != []:        
                    if str(dt["Prop"]) not in _dict.keys():
                        _dict.setdefault(str(dt["Prop"]), [])
                    _dict[str(dt["Prop"])].append(dt)
        find_dict = {"asofdate":todayDate}
        myDb = self.mongo["wet_weight_staging"]
        item_count = myDb.count_documents(find_dict)
        
        if item_count == 0:
            print "Data not available in staging... Getting From Mains..."
            self.dbManager.get_today_records(todayDate)
            find_dict = {"asofdate":todayDate}
            item_count = myDb.count_documents(find_dict)
        print item_count
        if item_count > 0:
            dbresult = myDb.find(find_dict)            
            for dt in dbresult:
                if dt != []:        
                    if str(dt["Prop"]) not in _dict.keys():
                        _dict.setdefault(str(dt["Prop"]), [])
                    _dict[str(dt["Prop"])].append(dt)

        if _dict != {}:
            stage_data = _dict["Wet Weight"]
            wt_data = {}
            wt_result = []
            sample_data = {}
            sample_result = []
            all_time = []
            sample_bit_data = {}
            for node in stage_data:
                xTime = node["Time"]
                xDateTime =  xTime.strftime("%Y-%m-%d %H:%M")
                cont_weight = elib.tonum(node["ContinuousWeight"])
                totalizer = elib.tonum(node["Totaliser"],'float', 0)
                sample_weight = elib.tonum(node["SampleWeight"])
                sample_bit = elib.tonum(node["SampleBit"], 'int')
                
                all_time.append(xTime)
                elib.dictIncrement(sample_bit_data, xTime, str(sample_bit), sample_weight)
                
                if xDateTime in timerange:
                    if cont_weight > 0:
                        elib.dictIncrement(wt_data, xDateTime, "ContinuousWeight", [cont_weight])
                    else:
                        if xDateTime not in wt_data.keys():
                            wt_data.setdefault(xDateTime, {}).setdefault("ContinuousWeight", [0])
                        elif "ContinuousWeight" not in wt_data[xDateTime].keys():
                            wt_data[xDateTime].setdefault("ContinuousWeight", [0])
                    if totalizer > 0:
                        elib.dictIncrement(wt_data, xDateTime, "Totaliser", [totalizer])
                    else:
                        if xDateTime not in wt_data.keys():
                            wt_data.setdefault(xDateTime, {}).setdefault("Totaliser", [0])
                        elif "Totaliser" not in wt_data[xDateTime].keys():
                            wt_data[xDateTime].setdefault("Totaliser", [0])
            cnt = 0
            zeroCnt = 1
            totalW = 0
            bit_data = {}
            sample_result = []
            for xtime in sorted(all_time):
                for key in sample_bit_data[xtime]:
                    if key == "1":
                        if zeroCnt != 0:
                            row = {}
                            xDateTime =  xtime.strftime("%Y-%m-%d %H:%M")
                            row.setdefault("Time", xDateTime)
                            row.setdefault("SampleBit", 1)
                            row.setdefault("SampleWeight", sample_bit_data[xtime][key])
                            sample_result.append(row)
                            cnt += 1
                            zeroCnt = 0
                            totalW = sample_bit_data[xtime][key]
                        if str(cnt) not in bit_data:
                            bit_data.setdefault(str(cnt), totalW)
                        else:
                            bit_data[str(cnt)] = totalW
                    else:
                        totalW = 0
                        zeroCnt = 1

            for xtime in timerange:
                row = {}
                row.setdefault("Time", xtime)
                for key in wt_data.get(xtime,{}):
                    avg = sum(wt_data[xtime][key]) / len(wt_data[xtime][key])
                    row.setdefault(key, avg)
                wt_result.append(row)

            out_result.setdefault("WetWeight", wt_result)
            out_result.setdefault("SampleWeight", sample_result)

        if mode == "view":
            return jsonify(Results=out_result)
        else:
            return out_result

    def downloadWWReport(self, out_report):
        params = self.get_params(request)
        selectedDate = params.get('selectedDate', False)
        todayDate = params.get('today', False)
        reportTitle = params.get("title", False)

        todayDate = datetime.now();
        dts_time = time.mktime(todayDate.timetuple()) * 1000
        txtfilename = "wet_weight_report.txt"
        title = "Wet Weight"
        headers =  ["Time", "Continuous Weight", "Totaliser"]
        keyheaders = ["Time", "ContinuousWeight", "Totaliser"]
        out_pdf= FILE_PATH + 'Wet_Weight_Report_'+selectedDate+'.pdf'
        out_files = []
        for report in out_report:
            out_data = out_report[report]
            if report == "WetWeight":
                title = "Wet Weight"
                txtfilename = "wet_weight_report.txt"
                headers =  ["Time", "Continuous Weight", "Totaliser"]
                keyheaders = ["Time", "ContinuousWeight", "Totaliser"]
            elif report == "SampleWeight":
                title = "Sample Weight"
                txtfilename = "sampling_report.txt"
                headers =  ["Time", "Sample Weight", "Sample Bit"]
                keyheaders = ["Time", "SampleWeight", "SampleBit"]

            data_list = []
            s = ""

            for hd in headers:
                s += str(hd)
                index = headers.index(hd)
                if index < len(headers) - 1:
                    s += "\t"
            data_list.append(s)

            for node in out_data:
                s = ""      
                for key in keyheaders:
                    s += str(node.get(key,"-"))
                    index = keyheaders.index(key)
                    if index < len(keyheaders) - 1:
                        s += "\t"
                data_list.append(s)
            out_files.append({"txt": txtfilename, "name": title})
            outF = open(txtfilename, "w")
            for line in data_list:
                outF.write(line)
                outF.write("\n")
            outF.close()
        
        intermediate_html = 'intermediate.html'
        htmlToAdd = '<div style="margin-left:10px;margin-top:20px;text-align:center;border:1px solid white;">'\
                            '<div style="text-center:left;margin-left:1rem;margin-right:1rem;margin-top:500px;">'\
                                '<img src="' + SETTING_PATH + 'abz2_big.png" style=""/>'\
                                '<div style="text-align:center;color:#323232;font-size:35px;margin-top:5px;">'\
                                    '<span style="color:#323232;font-size:35px;margin-right:2rem;">Wet Weight Report</span>'\
                                '</div>'\
                                '<div style="text-align:center;color:#323232;font-size:35rem;margin-top:5px;">'\
                                    '<span style="color:#323232;font-size:30px;"> Generation Date ('+selectedDate+') </span>'\
                                '</div>'\
                            '</div>'\
                        '</div>'
        newhtmlToAdd = ''
        if os.path.exists(intermediate_html):
            os.remove(intermediate_html)
        for _file in out_files:
            title = _file["name"] + " Daily Report"
            df = pd.read_csv(_file["txt"], delimiter="\t", delim_whitespace=False)
            intermediate_html = 'intermediate.html'
            self.to_html_pretty(df, intermediate_html, title, htmlToAdd, "Wet Weight Report", selectedDate)
            htmlToAdd = ""
            os.remove(_file["txt"])
        # pdfkit.from_file(intermediate_html, out_pdf, configuration=config)
        pdfkit.from_file(intermediate_html, out_pdf)
        return out_pdf

    def to_html_pretty(self, df, filename='out.html', title='', htmlToAdd='',reportTitle='', selectedDate=''):
        ht = ''
        print title
        if htmlToAdd != '':
            ht += htmlToAdd
        if title != '':
            ht += '<h1><img src="' + SETTING_PATH + 'abz2_small.png" style="margin-right:100px;margin-top:5px;"/>'
            ht += '<span style="margin-left:70px;text-align:center;color:#323232;font-size:22px;">'\
                                '<span style="color:#323232;font-size:18px;margin-right:2rem;">'+reportTitle+'</span>'\
                            '</span>'\
                            '<span style="text-align:right;color:#323232;font-size:22px;margin-left:110px;">'\
                                '<span style="color:#323232;font-size:18px;"> Generation Date ('+selectedDate+') </span>'\
                            '</span></h1>'
            ht += '<h2> %s </h2>\n' % title
        ht += df.to_html(classes='wide', escape=False)

        with open(filename, 'a') as f:
             f.write(HTML_TEMPLATE1 + ht + HTML_TEMPLATE2)

    def save_ww_report(self):
        print "Saving Report..."
        out_list = self.get_ww_report(mode="download")
        filename = self.downloadWWReport(out_list)
        path = FILE_PATH
        uuidstr = str(uuid.uuid4())
        filepath = filename

        zip_name = "Wet_Weight_Reports_"+uuidstr+".zip"
        zip_file = path + zip_name
        print 'Creating archive ' + zip_name
        zf = zipfile.ZipFile(zip_file, mode='w')
        compression = zipfile.ZIP_DEFLATED

        zf.write(filepath, os.path.basename(filepath), compress_type=compression)
        os.remove(filepath)

        return jsonify(Results = zip_name)
