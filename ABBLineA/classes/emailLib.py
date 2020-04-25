# -*- coding: utf-8 -*-
import smtplib,os
import re,sys
import email
from email import encoders
from email.message import Message
from email.mime.audio import MIMEAudio
from email.mime.base import MIMEBase
from email.mime.image import MIMEImage
from email.MIMEMultipart import MIMEMultipart
from email.MIMEText import MIMEText
from email.header import Header
# For guessing MIME type based on file name extension
import mimetypes
import imaplib
from datetime import datetime

idPrefix = 'Prefix_'
idSuffix = '_Suffix'

base_path = os.path.dirname( __file__ )
log_path = os.path.join( base_path, "../log" )

def getSMTPServer(conn):	
	try:
		# srv = smtplib.SMTP(conn['hostname'] + ':' + str(conn['port']) , timeout = 3600)
		# srv.starttls() # required for port 587
		srv = smtplib.SMTP_SSL(conn['hostname'], conn["port"], timeout = 3600)
		srv.login(conn['uname'], conn['password'])
		#emailLib.logErrorMsg("SMTP login successful.")
	except Exception as inst:
		srv = None
		print "Unable to connect to SMTP server."
		raise Exception(str(sys.exc_info()[0]) + ' ' + str(sys.exc_info()[1]))				
	return srv

def smtpServerStop(srv):
	srv.quit()


def logErrorMsg(msg, fileName=''):
	log = open( log_path + '/error.txt', 'a+' )
	if len(fileName) > 0:
		print >> log, datetime.now().strftime("%Y-%m-%d %H:%M:%S") + " : " + msg + " in " + fileName
	else:
		print >> log, datetime.now().strftime("%Y-%m-%d %H:%M:%S") + " : " + msg 
	log.close()

def sendemail(srv,from_addr,from_name, to_addr_list, cc_addr_list,bcc_addr_list, reply_to, readreceipt_to, subject, message, attachmentPaths, askReadReceipt, htmlImages, charSet = 'utf-8',mailId = ''):
	mailType = 'html'
	allAddrs = to_addr_list + cc_addr_list + bcc_addr_list
	for mail in allAddrs:
		if not re.match(r"[^@]+@[^@]+\.[^@]+", mail):
			print "Invalid email id -", mail
	
	mailIdStr = idPrefix + mailId + idSuffix
	if len(reply_to.strip()) == 0:
		reply_to = from_addr
		
	print from_addr
	msg = MIMEMultipart()
	msg['From'] = from_addr
	#msg['From'] = from_name
	msg.set_charset('utf-8')
	msg['To'] = ','.join(to_addr_list)
	msg['Cc'] = ','.join(cc_addr_list)
	msg['Bcc'] = ','.join(bcc_addr_list)
	#msg['Subject'] = subject
	msg['Subject'] = Header(subject, 'utf-8')
	msg['Reply-to'] = reply_to
	msg['Thread-Topic'] = mailIdStr
	msg['App-Message-ID']= mailIdStr
	msg['Message-ID']= mailIdStr
	msg['Original-Message-ID']= mailIdStr
	msg['Content-Type']='text/html'
	
	if askReadReceipt == True:
		msg['Disposition-Notification-To'] = readreceipt_to
	
	#chienese chartset = 'GB18030'
	msg.attach(MIMEText(message, mailType, charSet))
	
	if len(attachmentPaths.keys()) > 0:
		for name in attachmentPaths:			
			path = attachmentPaths[name]
			if not os.path.isfile(path):
				print path, ' not found'
	        
	        if os.path.isfile(path):
		        ctype, encoding = mimetypes.guess_type(path)		        
		        #if ctype is None or encoding is not None:
		        if ctype is None and encoding is not None:	            
		            ctype = 'application/octet-stream'
		        maintype, subtype = ctype.split('/', 1)
		        if maintype == 'text':
		            fp = open(path)
		            attachment = MIMEText(fp.read(), _subtype=subtype)
		            fp.close()
		        elif maintype == 'image':
		            fp = open(path, 'rb')
		            attachment = MIMEImage(fp.read(), _subtype=subtype)
		            fp.close()
		        elif maintype == 'audio':
		            fp = open(path, 'rb')
		            attachment = MIMEAudio(fp.read(), _subtype=subtype)
		            fp.close()
		        else:
		            fp = open(path, 'rb')		           
		            attachment = MIMEBase(maintype, subtype)
		            attachment.set_payload(fp.read())
		            fp.close()
		            # Encode the payload using Base64
		            encoders.encode_base64(attachment)
		        # Set the filename parameter
		        
		        attachment.add_header('Content-Disposition', 'attachment', filename=name)
		        msg.attach(attachment)
	
	if len(htmlImages) > 0:
		for img in htmlImages:
			msg.attach(img)
			
	text = msg.as_string()	
	sm = srv.sendmail(from_addr, allAddrs , text)
	
	for name in attachmentPaths:
		path = attachmentPaths[name]		
		if '.vcf' in path:
			os.remove(path)		
	#server.quit()
	return msg

def getMailsFromMailBox():
	M = imaplib.IMAP4_SSL("pod51019.outlook.com", 993)
	M.login('tam@entercoms.com', 'Pass@word190814')
	M.select("inbox")
	#typ, data = M.search(None, 'FROM', 'Nikhil')
	return M
	
def getBouncedMail(mailBox):
	typ, data = mailBox.search(None, 'SUBJECT', 'Undeliverable:')
	#typ, data = mailBox.search(None, 'ALL')
	
	bouncedMailIds = []
	bouncedMailDict = {}
	
	for num in data[0].split():
		typ, data = mailBox.fetch(num, '(RFC822)')
		for response_part in data:
			if isinstance(response_part, tuple):
				msg = email.message_from_string(response_part[1])
				br_mailId = ''
				om_mailId = ''
				ss_mailId = ''
				mailUId = ''
				if (msg.is_multipart() and len(msg.get_payload()) > 1 and msg.get_payload(1).get_content_type() == 'message/delivery-status'):			
					if msg.has_key('Thread-Topic'):
						br_mailId = msg['Thread-Topic']
					
					if idPrefix not in br_mailId and idSuffix not in br_mailId:
						br_mailId = ''
						for k in msg.get_payload():
							if 'App-Message-ID' in str(k):
								arr = str(k).split('App-Message-ID')
								if len(arr) > 1 and idPrefix in arr[1] and idSuffix in arr[1]:
									index1 = arr[1].index(idPrefix) + len(idPrefix)
									index2 = arr[1].index(idSuffix)
									om_mailId = arr[1][index1:index2]
									if len(om_mailId) > 0:
										break
						
					br_mailId = br_mailId.replace(idPrefix , '')
					br_mailId = br_mailId.replace(idSuffix , '')
										
					#if len(br_mailId) == 0 and len(om_mailId) == 0 :
				 	if len(msg.get_payload()) > 0:
				 		searchArr = str(msg.get_payload(0)).split('To:')
			 			if len(searchArr) > 1:			 				
			 				searchArr[1] = searchArr[1].replace('&lt;', '<')
			 				searchArr[1] = searchArr[1].replace('&gt;', '>')
			 							 				
			 				try:
				 				index1 = searchArr[1].index('<') + 1
				 				index2 = searchArr[1].index('>')
				 				ss_mailId = searchArr[1][index1:index2]
			 				except Exception as inst:
			 					print str(inst)
				        						        		
							if len(br_mailId) > 0:
								if bouncedMailDict.has_key(br_mailId) == False:
									bouncedMailDict[br_mailId] = []	
								bouncedMailDict[br_mailId].append(ss_mailId)
							elif len(om_mailId) > 0:
								if bouncedMailDict.has_key(om_mailId) == False:
									bouncedMailDict[om_mailId] = []
								bouncedMailDict[om_mailId].append(ss_mailId)
							else:
								if bouncedMailDict.has_key('orphan') == False:
									bouncedMailDict['orphan'] = []
								bouncedMailDict['orphan'].append(ss_mailId)
							
					if len(br_mailId) > 0:
						bouncedMailIds.append(br_mailId)
					if len(om_mailId) > 0:
						bouncedMailIds.append(om_mailId)
					if len(ss_mailId) > 0:
						bouncedMailIds.append(ss_mailId)
					
					folderName = 'bouncereceipt'	          	  		          	  	
	          	  	try:
		          	  	mailBox.copy(num, 'bouncereceipt')
				        r = mailBox.store(num, '+FLAGS', '\\Deleted')
	          	  	except Exception as inst:
				        print str(inst)
					'''
					for k in msg.get_payload():
						print k
					
					if len(msg.get_payload()) > 2:
						print msg.get_payload(0)
						print "--------------------------------------"
					
					for k in msg.items():
						print k
						print >> outf, k[0] + " : " + k[1]
										
					for header in [ 'subject', 'to', 'from', 'References', 'In-Reply-To']:
						print header + " : " + msg[header]
					'''
		
	return bouncedMailDict

def getReadrecipt(mailBox):
	#typ, data = mailBox.search(None, 'ALL')	
	typ, data = mailBox.search(None, 'SUBJECT', 'Read:')
	msg_headers = [ 'to', 'from', 'Thread-Topic', 'subject']
	mailUUIds = []
	notread_mailUUIds = []
	orphanMails = []
	maildata = {}
	for num in data[0].split():
	    typ, data = mailBox.fetch(num, '(RFC822)')
	    for response_part in data:            
	        if isinstance(response_part, tuple):                
	            msg = email.message_from_string(response_part[1])	            
	            om_mailId = ''	            
	            if type(msg.get_payload()) == list and len(msg.get_payload()) > 1 and msg.get_payload(1).get_content_type() == 'message/disposition-notification':
	          	  	mailRead = True	            
	          	  	if "not read" in msg['subject'].lower():
	          	  		mailRead = False
          	  		for k in msg.walk():
						if 'Original-Message-ID' in str(k) or 'In-Reply-To' in str(k):		                    	                    
						    arr = str(k).split('Original-Message-ID')		                              
						    if len(arr) < 2:		                    	
						    	arr = str(k).split('In-Reply-To')
						    if len(arr) > 1 and idPrefix in arr[1] and idSuffix in arr[1]:
						        index1 = arr[1].index(idPrefix) + len(idPrefix)
						        index2 = arr[1].index(idSuffix)
						        om_mailId = arr[1][index1:index2]
						        if len(om_mailId) > 0:
						        	if mailRead:
						        		mailUUIds.append(om_mailId)
						        	else:
						        		notread_mailUUIds.append(om_mailId)
						        	break
	            		
	          	  	if len(om_mailId) == 0:
	          	  		maildata = {'date' : datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
		            	for header in msg_headers:   		
		            		maildata[header] = msg[header]
		                orphanMails.append(maildata)
		            	          	  	
	          	  	folderName = 'readreceipt'	          	  		          	  	
	          	  	try:
		          	  	mailBox.copy(num, 'readreceipt')
				        r = mailBox.store(num, '+FLAGS', '\\Deleted')
	          	  	except Exception as inst:
				        print str(inst)
			        
	return mailUUIds, notread_mailUUIds, orphanMails
				
	            
def get_language_charset(language):
	return 
