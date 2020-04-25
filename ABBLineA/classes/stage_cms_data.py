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


HTML_TEMPLATE2 = '</body></html>'

class CMSRun():
    def __init__(self):
        
        self.collection = ""
        self.properties = ""
        self.reportKeys = []
        self.reportManager = {}
        self.read_settings()

        self._date = "";
        self.all_dates = [];

        #print 'Reading Params....CMS'
        #print self._date
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
            _dict[prop].setdefault("CreamerRatioSP", [])
            _dict[prop].setdefault("CreamerRatioActual", [])
            _dict[prop].setdefault("MaidaActual", [])
            _dict[prop].setdefault("CreamActual", [])
            _dict[prop].setdefault("Time", [])
            target_dict.setdefault(prop, {})
        
        for row in dbresult:
            for prop in self.properties:                 
                keyprop = prop.lower().replace(' ', '_')
                fbtime = row[self.config["time"]]
                
                self._date = fbtime.strftime("%Y-%m-%d")
                _dict[prop].setdefault(fbtime, {})
                creamRatioSP = row[self.config['cream_ratio_sp']]
                creamRatioActual = elib.tonum(row[self.config['cream_ratio_actual']])
                maidaActual = elib.tonum(row[self.config['maida_actual']])
                creamActual = elib.tonum(row[self.config["cream_actual"]])

                _dict[prop][fbtime]["CreamerRatioSP"] = elib.tonum(creamRatioSP)
                _dict[prop][fbtime]["CreamerRatioActual"] = elib.tonum(creamRatioActual)
                _dict[prop][fbtime]["MaidaActual"] = elib.tonum(maidaActual)
                _dict[prop][fbtime]["CreamActual"] = creamActual
                _dict[prop][fbtime]["Time"] = fbtime
                _dict[prop][fbtime]["Prop"] = prop
                
        return _dict

    def get_today_records(self, dateparam = ""):
        #print "Data Push Started..."
        # dateparam = "2018-11-01"
        target_dict = self.read_from_db(dateparam)
        # print target_dict
        # client = MongoClient('127.0.0.1', username="admin", password="admin123", authSource='analyse_db', authMechanism='SCRAM-SHA-1')
        connection = MongoClient('127.0.0.1', username="admin", password="admin123", authSource='analyse_db', authMechanism='SCRAM-SHA-1')
        myDb = connection["analyse_db"]
        #print "self._date: ", self._date
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
            myDb["cms_staging"].remove({'asofdate':self._date})
            record_id = myDb["cms_staging"].insert_many(dbData)
            #print len(dbData),' records found'
            #print "DB Push Completed...CMS"
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
        db = myDb["cms_staging"]
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

if __name__ == "__main__":
    MRun()