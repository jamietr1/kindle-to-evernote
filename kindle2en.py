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
import getopt
import os.path
import dateutil.parser as parser
import re
import codecs
import smtplib

# Functions
def read_configuration(f):
	config_settings = {}
	if (os.path.isfile(f) == False):
		#ASSERT: no configuration file
		#TODO: create a file
		sys.exit(2)
	
	lines = [line.strip() for line in open(f)]
	for line in lines:
		if (line == "" or line[0] == '#'):
			continue
			
		tokens = line.split('=')
		config_settings[tokens[0]] = tokens[1];
		
	return config_settings

def get_semaphore_date(f):
	if (os.path.isfile(f) == False):
		f = open(f, 'w')
		last_date = parser.parse('1/1/2000')
		print(last_date, file=f)
		f.close()

	lines = [line.strip() for line in open(f)]
	for line in lines:
		last_date = parser.parse(line)
	
	return last_date
		
	
def main(argv):

	# Get run time for semaphore update at the end
	update_time = datetime.now()
	verbose = 0
	CONFIG_FILE = ""
	HOME_DIR = expanduser("~")

	try:
		opts, args = getopt.getopt(argv, "hvVf:", ["file="])
	except:
		print('kindle2en.py -h -v -V -f <configfile>')
		sys.exit(2)
	for opt, arg in opts:
		if (opt == '-h'):
			usage = """Usage: kindle2en.py [options]
			
Options:
  -f       specific location of configuration file other than home dir
  -h       display help
  -v       verbose output
  -V       output version information and exit
"""
			print(usage)
			sys.exit(0)
		elif (opt == '-f'):
			CONFIG_FILE = arg
		elif (opt == '-v'):
			verbose = 1
		elif (opt == '-V'):
			print('kindle2en.py (1.0.0)')
	
	# Set file locations
	if (CONFIG_FILE == ""):
		CONFIG_FILE = HOME_DIR + '/.kindle2en.cfg'
		
	if (verbose == 1):
		print('Using config file at ' + CONFIG_FILE)
		
	# Read configuration file
	config = read_configuration(CONFIG_FILE)
	
	# Other settings
	SEMAPHORE = HOME_DIR + '/.kindle2en_sem'
	RECORD_DELIM = '=========='

	if (os.path.isfile(config['CLIPPINGS_FILE']) == False):
		# ASSERT: error! Can't find the clippings file; exit cleanly
		print('Cannot location "My Clippings.txt" at ' + config['CLIPPINGS_FILE'] + '.')
		sys.exit(1)

	# Process semaphore file for last_date value
	last_date = get_semaphore_date(SEMAPHORE)
	if (verbose == 1):
		print('Looking for updates since ' + last_date.strftime("%Y-%m-%d %H:%M:%S"))
	
	line_count = 0
	title_notes = {}
	is_title = prev_date = notenote = highlight = 0

	if (verbose == 1):
		print('Parsing the clippings file at ' + config['CLIPPINGS_FILE'])
	
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
			if (verbose == 1):
				print('    Notes updated for ' + title)
			msg_count = msg_count + 1
			session.quit()
	
	# Update semaphore file
	f = open(SEMAPHORE, 'w')
	print(update_time.strftime("%Y-%m-%d %H:%M:%S"), file=f)
	f.close()

	if (verbose == 1):
		print('Finished parsing clippings file. Updated ' + str(msg_count) + ' notes in Evernote.')
		print('Be sure to sync Evernote with the server to see your updates.')

if __name__ == "__main__":
   main(sys.argv[1:])


