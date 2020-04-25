import emailLib
import os
import time

import logging
import logging.config
from logging import getLogger, INFO, ERROR, WARNING, CRITICAL, NOTSET, DEBUG, Formatter
from concurrent_log_handler import ConcurrentRotatingFileHandler

SETTING_PATH = str(os.path.realpath(__file__))
SETTING_PATH = SETTING_PATH.replace("send_mail.pyc", "")
SETTING_PATH = SETTING_PATH.replace("send_mail.pyo", "")
SETTING_PATH = SETTING_PATH.replace("send_mail.py", "")

FILE_PATH = str(os.path.realpath(__file__))
FILE_PATH = FILE_PATH.replace("classes/send_mail.pyc", "")
FILE_PATH = FILE_PATH.replace("classes/send_mail.pyo", "")
FILE_PATH = FILE_PATH.replace("classes/send_mail.py", "")
FILE_PATH = FILE_PATH + "dbpush/data/"

class EmailClient:
    def __init__(self, addr_list, attachment):

        self.to_addr_list =  addr_list #['deepali.bmahajan@gmail.com']
        self.attachment = attachment
        self.log = getLogger()

    def sendMail(self,subject,message):
        # conn = {'hostname': 'smtp.gmail.com', 'port': 587, 'uname': 'itantaanalytics@gmail.com',
        #         'password': 'Itanta@123'}
        conn = {'hostname': 'smtp.gmail.com', 'port': 465, 'uname': 'britannialine.a@gmail.com', 'password': 'brit123#'}
        mailSentFlag = False

        while mailSentFlag == False:
            self.log.info("mailSentFlag--- %s", mailSentFlag)
            try:
                srvr = emailLib.getSMTPServer(conn)
                msgObj = emailLib.sendemail(
                    srv=srvr,
                    from_addr=conn['uname'],
                    from_name='Britannia Line-A',
                    to_addr_list=self.to_addr_list,
                    cc_addr_list=[],
                    bcc_addr_list=[],
                    reply_to='',
                    readreceipt_to='',
                    subject=subject,
                    message=message,
                    attachmentPaths=self.attachment,
                    # attachmentPaths={
                    #     "pdfreport": SETTING_PATH + "All_charts_2018-11-01.pdf"
                    # },
                    askReadReceipt=False,
                    charSet='',
                    htmlImages=[],
                    mailId=''
                )
                mailSentFlag = True
                self.log.info("mailSentFlag --- %s", mailSentFlag)
            except Exception as e:
                self.log.exception(e)
                self.log.info("Exception Occurs")
                self.log.info("Sleeping... Retrying after 1 minute")
                time.sleep(60)
                continue
            break


# if __name__ == '__main__':
#     attachement = {
#         "Reports": FILE_PATH + "Moulder_DownTime.zip",
#     } 
#     email_client = EmailClient(['deepali.bmahajan@gmail.com','rishikesh.jathar@gmail.com'], attachement)
#     email_message = '<html><body><p>Dear Sir/Madam,<br>'\
#                         '<br>'\
#                         '<br>'\
#                         'Pls. find herewith the Reports for Britannia, Pondicherry Line A. <br>'\
#                         '<br>'\
#                         '<br>'\
#                         'Regards, <br>'\
#                         'Britannia Industries Limited. <br>'\
#                         'Pondicherry, Line A.<br>'\
#                         '<br>'\
#                         '<br>'\
#                         '* This is an auto generated Mail from BIT, Pondicherry, Line A. Please do not reply.*</p></body></html>'
#     email_client.sendMail('subject', email_message)
