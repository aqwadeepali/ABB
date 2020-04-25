import win32serviceutil
import win32service
import win32event
import servicemanager
import socket
import time
import subprocess
import logging
import sys
import os
import getpass

script_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "sms.py")
pythonw3_path = os.path.join(os.path.dirname(sys.executable), "pythonw3.exe")
userhome = os.path.expanduser('~')
username = os.path.split(userhome)[-1]

logging.basicConfig(
    filename = 'C:\\service.log',
    level = logging.INFO, 
    format = '[Itanta SMS Service] %(levelname)-7.7s %(message)s'
)

class ItantaSmsSvc (win32serviceutil.ServiceFramework):
    _svc_name_ = "Itanta Brit Mail Service"
    _svc_display_name_ = "Itanta Brit Mail Service"
    
    def __init__(self,args):
        win32serviceutil.ServiceFramework.__init__(self,args)
        self.stop_event = win32event.CreateEvent(None,0,0,None)
        socket.setdefaulttimeout(60)
        self.stop_requested = False

    def SvcStop(self):
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        win32event.SetEvent(self.stop_event)
        self.stop_requested = True

    def SvcDoRun(self):
        servicemanager.LogMsg(
            servicemanager.EVENTLOG_INFORMATION_TYPE,
            servicemanager.PYS_SERVICE_STARTED,
            (self._svc_name_,'')
        )
        self.main()

    def main(self):
        with open("C:\\maillog.log", "a") as fp:
            fp.write("Before executing sms\n")
        #cmd = "C:\\Users\\" + username + "\\AppData\\Local\\Programs\\Python\\Python37\\pythonw3.exe" + " " + script_path
        #ret = os.system(cmd)
        ret = os.system('C:\\Python27\\pythonw.exe "C:\\Program Files\\ItantaAnalytics\\ABB\\classes\\mail_schedular.py"')  
        with open("C:\\maillog.log", "a") as fp:
            fp.write("after executing sms " + str(ret) + "\n")

if __name__ == '__main__':
    win32serviceutil.HandleCommandLine(ItantaSmsSvc)