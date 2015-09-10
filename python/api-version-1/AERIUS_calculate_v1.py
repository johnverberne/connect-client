#!/usr/bin/python
import json
import time
from os import listdir
import os
from pprint import pprint

"""
Open the file, create json object send this json to AERIUS connect endpoint
"""
def gml_calculate(inputDir, filename):
	f = open(os.path.join(inputDir, filename),'r')
	input = f.read()
	f.close
	data = {}
	data["jsonrpc"] = "2.0"
	data["id"] = long(time.time() * 1000)
	data["method"] = "calculator.calculate"
	params = {}
	file = {}
	file["name"] = filename
	file["data"] = input.encode("base64","strict") #encode
	params["file"] = file
	params["listener"] = long(time.time() * 1000) + 1
	options = {}
	substances = ["NOX","NH3"]
	options["substances"] = substances
	options["calculationType"] = "PERMIT"
	options["email"] = "john.verberne@gmail.com"
	options["exportType"] = "GIS_ALL"
	options["reference"] = "opdracht op " + time.strftime("%c")
	options["tempProject"] = 0
	options["tempProjectYears"] = 1
	options["year"] = "2021"
	params["options"] = options
	data["params"] = params
	
	json_data = json.dumps(data)

	try:
		from websocket import create_connection
		ws = create_connection("ws://connect.aerius.nl/connect/1/services", 10000)
		#ws = create_connection("ws://localhost:8080/connect/1/services", 10000)
		
	except Exception, msg:
		print "Unexpected connection error %s" % msg
		return
		
	try:
	    # sending data
		ws.send(json_data)
		result = ws.recv()
		# write result part
		if (result.find("successful") > -1 or result.find("result") > -1):
			json_input = json.loads(result)
			print "calcualtion submitted %s" % json_input
			
		else: 
			json_input = json.loads(result)
			print "error in calculation"
			print "error '%s'" % json_input
			print json_input
			
	except Exception, msg:
		print "Unexpected result error %s" % msg
		
	finally:
		ws.close()
		
	return
	
# read files from directory 
inputDir = 'c://tmp//input'
files = listdir(inputDir)
for file in files:
	print "sending %s" % file
	gml_calculate(inputDir, file)