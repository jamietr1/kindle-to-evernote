#!/usr/bin/env python
# encoding: utf-8
"""
kindle2en.py

Created by Jamie Todd Rubin on 2014-03-08.
Copyright (c) 2014 __MyCompanyName__. All rights reserved.
"""

from __future__ import print_function
import sys
import os.path
import dateutil.parser as parser
import re

GMAIL_USERNAME = 'jamietoddrubin@gmail.com'
GMAIL_PASS = 'fqozdqcvhrxrzhqr'
GMAIL_SERVER = 'smtp.gmail.com'
EN_ADDRESS = 'jamietr.b9650@m.evernote.com'
CLIPPINGS_FILE = '/cygdrive/c/Users/rubin/Documents/GitHub/kindle-to-evernote/My Clippings.txt'
SEMAPHORE = '/cygdrive/c/Users/rubin/Documents/GitHub/kindle-to-evernote/.kindle2en_sem'

if (os.path.isfile(CLIPPINGS_FILE) == False):
	# ASSERT: error! Can't find the clippings file; exit cleanly
	sys.exit(0)

# Process semaphore file for last_date value
if (os.path.isfile(SEMAPHORE) == False):
	f = open(SEMAPHORE, 'w')
	last_date = parser.parse('1/1/2000')
	print(last_date, file=f)
	f.close()
	
lines = [line.strip() for line in open(SEMAPHORE)]
for line in lines:
	last_date = parser.parse(line)

line_count = 0

lines = [line.strip() for line in open(CLIPPINGS_FILE)]
for line in lines:
	line_count = line_count + 1
	if (line_count == 1):
		# ASSERT: this is a title line
		title = line
		prev_title = 1
		continue
	else:
		# ASSERT: not the first line
		if (prev_title == 1):
			# ASSERT: this is the date line
			result = re.search( r'.*Added on (.*)', line, re.M|re.I)
			note_date = parser.parse(result.group(1))
			if (note_date >= last_date):
				# ASSERT: We haven't collected this note yet, so do it now.
				prev_title = 0
				collect = 1
			continue
		elif (line == "========"):
			# ASSERT: end of record
			pass
		else:
		


	
	
	
#if (os.path.isfile(CLIPPINGS_FILE)):
#	lines = [line.strip() for line in open(CLIPPINGS_FILE)]
#	for line in lines:
#		print line
#		
#	print parser.parse('Thursday, March 6, 2014 3:50:33 AM')
#else:
#	print "Does not exist"




 
#from email.mime.text import MIMEText
#msg = MIMEText('This is the body of the message.')
#msg['Subject'] = 'Blank subject lines look like spam.'
#msg['From'] = GMAIL_USERNAME
#msg['To'] = EN_ADDRESS
#msg = msg.as_string()
 
#import smtplib
#session = smtplib.SMTP(GMAIL_SERVER, 587)
#session.ehlo()
#session.starttls()
#session.login(GMAIL_USERNAME, GMAIL_PASS)
#session.sendmail(GMAIL_USERNAME, recipients, msg)
#session.quit()
