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

# path_wkthmltopdf = r'C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe'
# config = pdfkit.configuration(wkhtmltopdf=path_wkthmltopdf)

CONFIG_PATH = str(os.path.realpath(__file__))
CONFIG_PATH = CONFIG_PATH.replace("stage_wet_weight_data.pyc", "")
CONFIG_PATH = CONFIG_PATH.replace("stage_wet_weight_data.pyo", "")
CONFIG_PATH = CONFIG_PATH.replace("stage_wet_weight_data.py", "")
CONFIG_PATH = CONFIG_PATH + "data/"

FILE_PATH = str(os.path.realpath(__file__))
FILE_PATH = FILE_PATH.replace("stage_wet_weight_data.pyc", "")
FILE_PATH = FILE_PATH.replace("stage_wet_weight_data.pyo", "")
FILE_PATH = FILE_PATH.replace("stage_wet_weight_data.py", "")
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

class WWRun():
    def __init__(self):
        
        self.collection = ""
        self.properties = ""
        self.reportKeys = []
        self.reportManager = {}
        self.read_settings()

        self._date = "";
        self.all_dates = [];

        #print 'Reading Params....'
        #print self._date
        #print 'File Ready to Use...'
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
        reader = csv.DictReader(open(CONFIG_PATH + 'stage_wet_weight_settings.txt'), delimiter="\t")
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
        #print "dateparam: ", dateparam
        
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
            ls_date = dateparam+" 23:59:00"
            gt_date = dateparam+" 00:00:00"
            lt_tm = time.mktime(datetime.strptime(ls_date,'%Y-%m-%d %H:%M:%S').timetuple())
            gt_tm = time.mktime(datetime.strptime(gt_date,'%Y-%m-%d %H:%M:%S').timetuple())
            to_find = {"$gte": gt_tm, "$lte": lt_tm }
            #print to_find
            dbresult = db.find({self.config["time_stamp"]:to_find}) 
            
        for prop in self.properties:
            _dict.setdefault(prop, {})
            target_dict.setdefault(prop, {})
        
        rpmCount = 0
        for row in dbresult:
            for prop in self.properties:
                
                fbtime = row[self.config["time"]]
                
                self._date = fbtime.strftime("%Y-%m-%d")
                _dict[prop].setdefault(fbtime, {})
                
                continuous_weight = row[self.config['wet_continuous_weight']]
                totaliser = elib.tonum(row[self.config['totaliser']])
                sample_weight = elib.tonum(row[self.config['sample_weight']])
                sample_bit = elib.tonum(row[self.config["sample_bit"]])

                _dict[prop][fbtime]["ContinuousWeight"] = elib.tonum(continuous_weight)
                _dict[prop][fbtime]["Totaliser"] = elib.tonum(totaliser)
                _dict[prop][fbtime]["SampleWeight"] = elib.tonum(sample_weight)
                _dict[prop][fbtime]["SampleBit"] = elib.tonum(sample_bit)
                _dict[prop][fbtime]["Time"] = fbtime                
                _dict[prop][fbtime]["Prop"] = prop
                
        return _dict

    def get_today_records(self, dateparam = ""):
        #print "Data Push Started..."
        # dateparam = "2018-11-01"
        target_dict = self.read_from_db(dateparam)
        # print target_dict
        connection = MongoClient('127.0.0.1', username="admin", password="admin123", authSource='analyse_db', authMechanism='SCRAM-SHA-1')
        myDb = connection["analyse_db"]
        print "self._date: ", self._date
        dbData = []
        for prop in target_dict:
            # #print prop
            for key in target_dict[prop]:
                if target_dict[prop][key] not in ["", None, []]:
                    row = {}
                    row = target_dict[prop][key]
                    row.setdefault("asofdate", self._date)
                    dbData.append(row)
        if dbData != []:
            myDb["wet_weight_staging"].remove({'asofdate':self._date})
            record_id = myDb["wet_weight_staging"].insert_many(dbData)
            #print len(dbData),' records found'
            #print "DB Push Completed...Wet Weight"
        else:
            print "No Data...Wet Weight"

    def get_ww_report(self, dateparam):
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
        out_result = {}

        find_dict = {"asofdate":selectedDate}

        connection = MongoClient('127.0.0.1', username="admin", password="admin123", authSource='analyse_db', authMechanism='SCRAM-SHA-1')
        myDb = connection["analyse_db"]
        # myDb = connection["analyse_db"]
        db = myDb["wet_weight_staging"]

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
        find_dict = {"asofdate":todayDate}
        item_count = db.count_documents(find_dict)
        
        if item_count == 0:
            #print "Data not available in staging... Getting From Mains..."
            self.get_today_records(todayDate)
            find_dict = {"asofdate":todayDate}
            item_count = db.count_documents(find_dict)
        #print item_count
        
        if item_count > 0:
            dbresult = db.find(find_dict)            
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
        else:
            out_result.setdefault("WetWeight", [])
            out_result.setdefault("SampleWeight", [])
        return out_result

    def downloadWWReport(self, out_report, dateparam):

        selectedDate = dateparam
        yesterdayDate = datetime.strptime(dateparam, '%Y-%m-%d')
        _date2460 = yesterdayDate + timedelta(minutes = (24*60))
        todayDate = _date2460.strftime('%Y-%m-%d')
        selectedDate = yesterdayDate.strftime("%Y-%m-%d")

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
                    s += str(node.get(key, "-"))
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
                                '<img src="' + CONFIG_PATH + 'abz2_big.png" style=""/>'\
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
        #print title
        if htmlToAdd != '':
            ht += htmlToAdd
        if title != '':
            ht += '<h1><img src="' + CONFIG_PATH + 'abz2_small.png" style="margin-right:100px;margin-top:5px;"/>'
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

    def save_ww_report(self, dateparam):
        #print "Saving Report..."
        out_list = self.get_ww_report(dateparam)
        filename = self.downloadWWReport(out_list, dateparam)
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

if __name__ == "__main__":
    MRun()