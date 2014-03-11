#!/usr/bin/env python
# encoding: utf-8
"""
kindle2en.py

Created by Jamie Todd Rubin on 2014-03-08.
Copyright (c) 2014 __MyCompanyName__. All rights reserved.
"""

from __future__ import print_function
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from os.path import expanduser
from datetime import *
import sys
import os.path
import dateutil.parser as parser
import re
import codecs
import smtplib

# Functions
def read_configuration():
	config_settings = {}
	if (os.path.isfile(CONFIG_FILE) == False):
		#ASSERT: no configuration file
		#TODO: create a file
		sys.exit(0)
	
	lines = [line.strip() for line in open(CONFIG_FILE)]
	for line in lines:
		if (line == "" or line[0] == '#'):
			continue
			
		tokens = line.split('=')
		config_settings[tokens[0]] = tokens[1];
		
	return config_settings

# Get run time for semaphore update at the end
update_time = datetime.now()

# File locations
HOME_DIR = expanduser("~")
CONFIG_FILE = HOME_DIR + '/.kindle2en.cfg'

# Read configuration file
config = read_configuration()

# Other settings
SEMAPHORE = HOME_DIR + '.kindle2en_sem'
RECORD_DELIM = '=========='

if (os.path.isfile(config['CLIPPINGS_FILE']) == False):
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
title_notes = {}
is_title = prev_date = notenote = highlight = 0

# Parse the clippings.txt file
lines = [line.strip() for line in codecs.open(config['CLIPPINGS_FILE'], 'r', 'utf-8-sig')]
for line in lines:
	line_count = line_count + 1
	if (line_count == 1 or is_title == 1):
		# ASSERT: this is a title line
		title = line.encode('ascii', 'ignore')
		prev_title = 1
		is_title = 0
		note_type_result = note_type = l = l_result = location = ""
		continue
	else:
		# ASSERT: not the first line
		if (prev_title == 1):
			# ASSERT: this is the date line
			#print(line)
			result = re.search( r'(.*)Added on (.*)', line, re.M|re.I)
			if (result is not None):
				note_type_result = result.group(1)
				#print(note_type_result)
				if (note_type_result.find("Highlight")>0):
					note_type = "Highlight"
				else:
					note_type = "Note"
				
				l = note_type_result
				l_result = re.search(r'(\d+)', l, re.M|re.I)
				location = l_result.group(1)
				
				note_date = parser.parse(result.group(2))
				
			if (note_date >= last_date):
				# ASSERT: We haven't collected this note yet, so do it now.
				str_date = note_date.strftime("%Y-%m-%d %H:%M:%S")
				if (title_notes.has_key(title)):
					title_notes[title] += 'On ' + str_date + ', a ' + note_type + ' starting at location ' + location + '\n'
				else:
					title_notes[title] = 'On ' + str_date + ', a ' + note_type + ' starting at location ' + location + '\n'
					
				prev_title = 0
				collect = 1
			continue
		elif (line == RECORD_DELIM):
			# ASSERT: end of record
			if (note_type == "Highlight" and highlight == 1):
				title_notes[title] += '</i></div></blockquote><i><br/></i>\n'
				
			if (note_type == "Note" and notenote == 1):
				title_notes[title] += '</div></blockquote><br/>\n';
				
			collect = 0
			is_title = 1
			highlight = 0
			notenote = 0
			continue
		else:
			# ASSERT: collecting lines for the current title/date
			if (collect == 1):
				if (note_type == "Highlight" and highlight == 0):
					title_notes[title] += '<div><br/></div><blockquote style="margin: 0 0 0 40px; border: none; padding: 0px;"><div><i style="background-color:rgb(255, 250, 165);-evernote-highlight:true;">' + line + '\n'
					highlight = 1
				elif (note_type == "Note" and notenote == 0):
					title_notes[title] += '<div><br/></div><blockquote style="margin: 0 0 0 40px; border: none; padding: 0px;"><div>' + line + '\n'
					notenote = 1
				else:
					title_notes[title] += line + '\n'

			
# Email to Evernote

msg_count = 0
for title, note in title_notes.iteritems():
	# INV: Do this for each title update we have

	
	# Package as an HTML email message so that we get the formatting in the note
	msg = MIMEMultipart('alternative')
	part1 = MIMEText(note.encode('ascii', 'ignore'), 'html')
	msg.attach(part1)
	
	# The space-+ at the end of the subject tells Evernote to append this to the most
	# recent note with the same title, or create a new note if the title does not exist
	subject = title.encode('ascii', 'ignore') + ' +'
	msg['Subject'] = subject
	
	# Address the message
	msg['From'] = config['GMAIL_USERNAME']
	msg['To'] = config['EN_ADDRESS']
	msg = msg.as_string()
	
	# Send the message
	try:
		session = smtplib.SMTP(config['GMAIL_SERVER'], 587)
		session.ehlo()
		session.starttls()
		session.login(config['GMAIL_USERNAME'], config['GMAIL_PASS'])
		session.sendmail(config['GMAIL_USERNAME'], config['EN_ADDRESS'], msg)
	except:
		pass
	else:
		print('Notes updated for ' + title)
		msg_count = msg_count + 1
		session.quit()
	
	

# Update semaphore file
f = open(SEMAPHORE, 'w')
print(update_time.strftime("%Y-%m-%d %H:%M:%S"), file=f)
f.close()

print(msg_count)




