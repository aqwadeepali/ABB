with open("C:\mailer.log", "a") as fp:
    fp.write("Mailer script got executed.\n")

import schedule
import os, json
import elib
from datetime import timedelta, datetime
from time import strftime
# import datetime
import time
import os, json, csv
import re
import shutil
import zipfile
from stage_data import Run
from stage_moulder_data import MRun
from stage_cms_data import CMSRun
from stage_wet_weight_data import WWRun
from stage_packing_data import PRun
from stage_oven_data import ORun
from stage_bori_data import BRun
# import send_mail
from send_mail import EmailClient
import webbrowser
import ast

import logging
import logging.config
from logging import getLogger, INFO, ERROR, WARNING, CRITICAL, NOTSET, DEBUG
from concurrent_log_handler import ConcurrentRotatingFileHandler
import os

LOG_PATH = str(os.path.realpath(__file__))
LOG_PATH = LOG_PATH.replace("mail_schedular.pyc", "")
LOG_PATH = LOG_PATH.replace("mail_schedular.pyo", "")
LOG_PATH = LOG_PATH.replace("mail_schedular.py", "")
LOG_PATH = LOG_PATH + "../"
NEW_LOG_PATH = "D:\\ABBLogs\\"

log = logging.getLogger()
logfile = os.path.abspath(NEW_LOG_PATH + "mailschedularlogs.log")
log.setLevel(INFO)
# Rotate log after reaching 512K, keep 5 old copies.
rotateHandler = ConcurrentRotatingFileHandler(logfile, "a", 1024*1024, 5)
log.addHandler(rotateHandler)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
rotateHandler.setFormatter(formatter)


FILE_PATH = str(os.path.realpath(__file__))
FILE_PATH = FILE_PATH.replace("classes/mail_schedular.pyc", "")
FILE_PATH = FILE_PATH.replace("classes/mail_schedular.pyo", "")
FILE_PATH = FILE_PATH.replace("classes/mail_schedular.py", "")
FILE_PATH = FILE_PATH + "dbpush/data/"

SETTING_PATH = str(os.path.realpath(__file__))
SETTING_PATH = SETTING_PATH.replace("mail_schedular.pyc", "")
SETTING_PATH = SETTING_PATH.replace("mail_schedular.pyo", "")
SETTING_PATH = SETTING_PATH.replace("mail_schedular.py", "")
SETTING_PATH = SETTING_PATH + "data/"

def get_schedular_time_frame(tm):
    timerange = []
    nowDate = datetime.now()
    selectedDateTime = nowDate.strftime("%Y-%m-%d")
    selectedDateTime = selectedDateTime + " " + tm
    index = 0
    while index < 3:
        _date = datetime.strptime(selectedDateTime, '%Y-%m-%d %H:%M')
        _date_60 = _date + timedelta(minutes = 1)
        selectedDateTime = _date_60.strftime('%Y-%m-%d %H:%M')
        newtm = _date_60.strftime('%H:%M')
        timerange.append(newtm)
        index += 1
    print(timerange + "******************")
    return timerange

def set_settings(val):
    log.info("Setting Flag...%s", str(val))
    print("Setting Flag...." + str(val))
    time = ""
    tile = []
    EMAIL_LIST = []
    TIME_FLAG = False
    path = SETTING_PATH + 'ui_settings.txt'
    header = ["Field", "Value"]
    final_data = []
    reader = csv.DictReader(open(path), delimiter="\t")
    for row in reader:
        if row["Field"] == "UI_TIME":
            row["Value"] = row["Value"]
        if row["Field"] == "TILE":
            row["Value"] = ast.literal_eval(row["Value"])
        if row["Field"] == "EMAIL_LIST":
            row["Value"] = ast.literal_eval(row["Value"])
        if row["Field"] == "TIME_FLAG":
            row["Value"] = val
        final_data.append(row)
    
    with open(path, 'wb') as f:
        w = csv.DictWriter(f, final_data[0].keys(), dialect = "excel-tab")
        w.writeheader()
        w.writerows(final_data)

def read_settings():
    log.info("Reading Settings")
    time = ""
    tile = []
    EMAIL_LIST = []
    TIME_FLAG = False
    reader = csv.DictReader(open(SETTING_PATH + 'ui_settings.txt'), delimiter="\t")
    for row in reader:
        if row["Field"] == "UI_TIME":
            time = row["Value"]
        if row["Field"] == "TILE":
            tile = ast.literal_eval(row["Value"])
        if row["Field"] == "EMAIL_LIST":
            EMAIL_LIST = ast.literal_eval(row["Value"])
        if row["Field"] == "TIME_FLAG":
            TIME_FLAG = row["Value"]
    return {"time":time, "tile": tile, "email_list":EMAIL_LIST, "time_flag": TIME_FLAG}

def open_browser():
    url = 'http://localhost:4200/#/'

    # MacOS
    chrome_path = 'open -a /Applications/Google\ Chrome.app %s'

    # Windows
    # chrome_path = 'C:/Program Files (x86)/Google/Chrome/Application/chrome.exe %s'

    # Linux
    # chrome_path = '/usr/bin/google-chrome %s'

    webbrowser.get(chrome_path).open(url) # opens browser

def job():
    try:
        log.info("Job Started...")
        all_settings = read_settings()
        sch_time = all_settings["time"]

        sch_time_list = get_schedular_time_frame(sch_time)

        tile = all_settings["tile"]
        allTiles = {}
        for obj in tile:
            allTiles.setdefault(obj["name"], obj["value"])

        EMAIL_LIST = all_settings["email_list"]
        TIME_FLAG = all_settings["time_flag"]
        # dt = datetime.datetime.strptime("2018-11-02 06:02:00", '%Y-%m-%d %H:%M:%S')
        dt = datetime.now()
        _date2460 = dt - timedelta(minutes = (24*60))
        dtime = datetime.now().time()

        current_time = dtime.strftime("%H:%M")
        current_format_dt = dt.strftime('%Y-%m-%d')
        
        format_dttime = _date2460.strftime('%Y-%m-%d %H:%M:%S')
        format_dt = _date2460.strftime('%Y-%m-%d')
        log.info(current_time)

        #print current_time , "----" , sch_time_list

        if current_time in sch_time_list and TIME_FLAG in [False, "False"]:
            print("Schedular started...")
            # open_browser()
            set_settings(True)

            log.info("Dashboards Report Download.........................Started")
            
            if allTiles["Mixing"] == True:
                dbManager = Run()
                log.info("-------------------------")

            # #Moulder
            
            if allTiles["Moulder"] == True:
                dbMoulderManager = MRun()
                log.info("-------------------------")
                

            # #Oven
            if allTiles["Oven"] == True:
                dbOvenManager = ORun()
                log.info("-------------------------")

            # #Bori
            if allTiles["Bori"] == True:
                dbBoriManager = BRun()
                log.info("-------------------------")


            # #CMS
            if allTiles["CMS"] == True:
                dbCMSManager = CMSRun()
                log.info("-------------------------")

            #Wet Weight
            if allTiles["Wet Weight"] == True:
                dbWWManager = WWRun()
                log.info("-------------------------")

            #Packing
            if allTiles["Packing"] == True or allTiles["Losses"] == True:
                dbPManager = PRun()
                log.info("-------------------------")

            mixing_report = dbManager.read_and_download_report(format_dt) if allTiles["Mixing"] == True else ""
            log.info(mixing_report)
            moulder_report = dbMoulderManager.save_moulder_report(format_dt) if allTiles["Moulder"] == True else ""
            log.info(moulder_report)
            downtime_report = dbMoulderManager.save_moulder_downtime_report(format_dt) if allTiles["Moulder"] == True else ""
            log.info(downtime_report)
            oven_report = dbOvenManager.save_oven_report(format_dt) if allTiles["Oven"] == True else ""
            log.info(oven_report)
            bori_report = dbBoriManager.save_bori_report(format_dt) if allTiles["Bori"] == True else ""
            log.info(bori_report)
            cms_report = dbCMSManager.save_cms_report(format_dt) if allTiles["CMS"] == True else ""
            log.info(cms_report)
            ww_report = dbWWManager.save_ww_report(format_dt) if allTiles["Wet Weight"] == True else ""
            log.info(ww_report)
            packing_report = dbPManager.save_packing_report(format_dt) if allTiles["Packing"] == True else ""
            log.info(packing_report)
            losses_report = dbPManager.save_losses_report(format_dt) if allTiles["Losses"] == True else ""
            log.info(losses_report)
            folder_path = FILE_PATH + "Reports_"+format_dt
            if not os.path.exists(folder_path):
                os.makedirs(folder_path)
            else:
                shutil.rmtree(folder_path)
                os.makedirs(folder_path)

            if mixing_report not in ["", None]:
                for mr in mixing_report:
                    shutil.copy(mr, folder_path)
                    os.remove(mr)
            if moulder_report not in ["", None]:
                shutil.copy(moulder_report, folder_path)
                os.remove(moulder_report)
            if downtime_report not in ["", None]:
                shutil.copy(downtime_report, folder_path)
                os.remove(downtime_report)
            if oven_report not in ["", None]:
                shutil.copy(oven_report, folder_path)
                os.remove(oven_report)
            if bori_report not in ["", None]:
                shutil.copy(bori_report, folder_path)
                os.remove(bori_report)
            if cms_report not in ["", None]:
                shutil.copy(cms_report, folder_path)
                os.remove(cms_report)
            if ww_report not in ["", None]:
                shutil.copy(ww_report, folder_path)
                os.remove(ww_report)
            if packing_report not in ["", None]:
                shutil.copy(packing_report, folder_path)
                os.remove(packing_report)
            if losses_report not in ["", None]:
                shutil.copy(losses_report, folder_path)
                os.remove(losses_report)
            shutil.make_archive(FILE_PATH + 'All_Reports', 'zip', folder_path)

            attachement = {
                "Reports.zip": FILE_PATH + "All_Reports.zip",
            } 
            log.info("Sending Email Reports..............................")
            log.info(EMAIL_LIST)
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
                            '* This is an auto generated Mail from BIT, Pondicherry, Line A. Please do not reply.*</p></body></html>'
            email_client.sendMail('Britannia Report', email_message)
            log.info("Email Sent...")
            os.remove(FILE_PATH + 'All_Reports.zip')
            shutil.rmtree(folder_path)


            log.info("Dashboard Report Download.........................Started")
            mixing_report = dbManager.read_and_download_home(format_dt) if allTiles["Mixing"] == True else ""
            log.info(mixing_report)
            moulder_report = dbMoulderManager.save_moulder_home(format_dt) if allTiles["Moulder"] == True else ""
            log.info(moulder_report)
            oven_report = dbOvenManager.save_oven_home(format_dt) if allTiles["Oven"] == True else ""
            log.info(oven_report)
            packing_report = dbPManager.save_packing_home(format_dt) if allTiles["Packing"] == True else ""
            log.info(packing_report)
            folder_path = FILE_PATH + "Reports_"+format_dt
            if not os.path.exists(folder_path):
                os.makedirs(folder_path)
            else:
                shutil.rmtree(folder_path)
                os.makedirs(folder_path)

            if mixing_report not in ["", None]:
                for mr in mixing_report:
                    shutil.copy(mr, folder_path)
                    os.remove(mr)
            if moulder_report not in ["", None]:
                shutil.copy(moulder_report, folder_path)
                os.remove(moulder_report)
            if oven_report not in ["", None]:
                shutil.copy(oven_report, folder_path)
                os.remove(oven_report)
            if packing_report not in ["", None]:
                shutil.copy(packing_report, folder_path)
                os.remove(packing_report)
            shutil.make_archive(FILE_PATH + 'All_Dashboard_Reports', 'zip', folder_path)

            attachement = {
                "Dashboards.zip": FILE_PATH + "All_Dashboard_Reports.zip",
            } 
            log.info("Sending Email Dashboards..............................")
            log.info(EMAIL_LIST)
            email_client = EmailClient(EMAIL_LIST, attachement)
            email_message = '<html><body><p>Dear Sir/Madam,<br>'\
                            '<br>'\
                            '<br>'\
                            'Pls. find herewith the Dashboards for Britannia, Pondicherry Line A. <br>'\
                            '<br>'\
                            '<br>'\
                            'Regards, <br>'\
                            'Britannia Industries Limited. <br>'\
                            'Pondicherry, Line A.<br>'\
                            '<br>'\
                            '<br>'\
                            '* This is an auto generated Mail from BIT, Pondicherry, Line A. Please do not reply.*</p></body></html>'
            email_client.sendMail('Britannia Dashboards', email_message)
            log.info("Email Sent...")
            os.remove(FILE_PATH + 'All_Dashboard_Reports.zip')
            shutil.rmtree(folder_path)
            set_settings(False)
        else:
            log.info("No Report Sharing...")
            print("No Report")

        log.info("DB Push Sleeping...")
    except Exception as e:
        log.exception("Fatal error in main exception", exc_info=True)
        log.exception(str(e)) 
    finally:
        TIME_FLAG = False

schedule.every(1).minutes.do(job)

while True:
    schedule.run_pending()
    TIME_FLAG = False
    time.sleep(1)