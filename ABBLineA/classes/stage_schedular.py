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
LOG_PATH = LOG_PATH.replace("stage_schedular.pyc", "")
LOG_PATH = LOG_PATH.replace("stage_schedular.pyo", "")
LOG_PATH = LOG_PATH.replace("stage_schedular.py", "")
LOG_PATH = LOG_PATH + "../"

log = logging.getLogger()
logfile = os.path.abspath(LOG_PATH + "stageschedularlogs.log")
log.setLevel(INFO)
# Rotate log after reaching 512K, keep 5 old copies.
rotateHandler = ConcurrentRotatingFileHandler(logfile, "a", 1024*1024, 5)
log.addHandler(rotateHandler)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
rotateHandler.setFormatter(formatter)

FILE_PATH = str(os.path.realpath(__file__))
FILE_PATH = FILE_PATH.replace("classes/stage_schedular.pyc", "")
FILE_PATH = FILE_PATH.replace("classes/stage_schedular.pyo", "")
FILE_PATH = FILE_PATH.replace("classes/stage_schedular.py", "")
FILE_PATH = FILE_PATH + "dbpush/data/"

SETTING_PATH = str(os.path.realpath(__file__))
SETTING_PATH = SETTING_PATH.replace("stage_schedular.pyc", "")
SETTING_PATH = SETTING_PATH.replace("stage_schedular.pyo", "")
SETTING_PATH = SETTING_PATH.replace("stage_schedular.py", "")
SETTING_PATH = SETTING_PATH + "data/"

def read_settings():
    log.info("Reading Settings")
    time = ""
    tile = []
    EMAIL_LIST = []
    reader = csv.DictReader(open(SETTING_PATH + 'ui_settings.txt'), delimiter="\t")
    for row in reader:
        if row["Field"] == "STAGE_TIME":
            time = row["Value"]
        if row["Field"] == "TILE":
            tile = ast.literal_eval(row["Value"])
        if row["Field"] == "EMAIL_LIST":
            EMAIL_LIST = ast.literal_eval(row["Value"])
    return {"time":time, "tile": tile, "email_list":EMAIL_LIST}

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
        all_settings = read_settings()
        sch_time = all_settings["time"]

        # sch_time_list = get_schedular_time_frame(sch_time)

        tile = all_settings["tile"]
        allTiles = {}
        for obj in tile:
            allTiles.setdefault(obj["name"], obj["value"])

        log.info("DB Push Working...")
        # dt = datetime.datetime.strptime("2018-11-02 06:02:00", '%Y-%m-%d %H:%M:%S')
        dt = datetime.now()
        dtime = datetime.now().time()
        #print "dt: ", dt
        #print "dtime: ", dtime
        # dtimetuple = time.mktime(datetime.now().timetuple())

        current_time = dtime.strftime("%H:%M")
        current_format_dt = dt.strftime('%Y-%m-%d')

        current_format_dttime = current_format_dt + " " + current_time
        dtimetuple = time.mktime(datetime.strptime(current_format_dttime, '%Y-%m-%d %H:%M').timetuple())
        #print "current_format_dt: ", current_format_dt

        newDate = current_format_dt + " 00:00"
        todayDate = datetime.strptime(current_format_dt, '%Y-%m-%d')
        yesterDayDate = todayDate - timedelta(minutes = (24*60))
        
        # print todayDate, '=--', yesterDayDate
        timerange = []
        selectedTime = current_format_dt + " 06:30"
        timerange = []
        timerangeTuple = []
        timerange.append(newDate)
        #print newDate,'---', selectedTime
        while newDate != selectedTime:
            _date = datetime.strptime(newDate, '%Y-%m-%d %H:%M')
            _date_60 = _date + timedelta(minutes = 1)
            newDate = _date_60.strftime('%Y-%m-%d %H:%M')
            timerange.append(newDate)
            timerangeTuple.append(time.mktime(datetime.strptime(newDate, '%Y-%m-%d %H:%M').timetuple()))
        timerange = sorted(timerange)

        
        # tommDate = _date2460.strftime('%Y-%m-%d')
        
        # tommDate = tommDate + " 06:30"
        # tommDateTuple = time.mktime(datetime.strptime(tommDate, '%Y-%m-%d %H:%M').timetuple())
        # print "tommDate: ", tommDate

        if dtimetuple in timerangeTuple:
            current_format_dt = yesterDayDate.strftime("%Y-%m-%d")
            #print "Change in current_format_dt"
            #print "current_format_dt: ", current_format_dt
        
        # # Mixing
        dbManager = Run()
        if allTiles["Mixing"] == True:
            dbManager.get_today_records(current_format_dt)
            log.info("-------------------------")

        # #Moulder
        dbMoulderManager = MRun()
        if allTiles["Moulder"] == True:
            dbMoulderManager.get_today_records(current_format_dt)
            log.info("-------------------------")

        # #Oven
        dbOvenManager = ORun()
        if allTiles["Oven"] == True:
            dbOvenManager.get_today_records(current_format_dt)
            log.info("-------------------------")

        # #Bori
        dbBoriManager = BRun()
        if allTiles["Bori"] == True:
            dbBoriManager.get_today_records(current_format_dt)
            log.info("-------------------------")


        # #CMS
        dbCMSManager = CMSRun()
        if allTiles["CMS"] == True:
            dbCMSManager.get_today_records(current_format_dt)
            log.info("-------------------------")

        #Wet Weight
        dbWWManager = WWRun()
        if allTiles["Wet Weight"] == True:
            dbWWManager.get_today_records(current_format_dt)
            log.info("-------------------------")

        #Packing
        dbPManager = PRun()
        if allTiles["Packing"] == True or allTiles["Losses"] == True:
            dbPManager.get_today_records(current_format_dt)
            dbPManager.get_today_cbb_records(current_format_dt)
            log.info("-------------------------")

        log.info("DB Push Sleeping...")
    except Exception as e:
        log.exception("Fatal error in main exception", exc_info=True)
        log.exception(str(e)) 

schedule.every(1).minutes.do(job)

while True:
    schedule.run_pending()
    time.sleep(1)
