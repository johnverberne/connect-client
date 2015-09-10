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
	f = open(os.path.join(inputDir, filename),'rb')
	bytes = f.read()
	f.close
	# create json text object
	json_text = """
	{
		"jsonrpc":"2.0",
		"id":0,
		"method":"calculator.calculate",
		"params":{"listener":0,
			"file":
			{
				"name":"",
				"data":""
			},
			"options":
			{
				"calculationType":"PERMIT",
				"exportType":"GIS_ALL",
				"email":"john.verberne@gmail.com",
				"maximumRange":10000,
				"reference":"uw reference",
				"substances":["NOX","NH3"],
				"tempProject":0,
				"tempProjectYears":1,
				"year":"2015"
			}}
	}
	"""
	# replace paramaters
	json_data = json.loads(json_text)
	json_data["id"] = long(time.time() * 1000) #create unique id
	json_data["params"]["listener"]= long(time.time() * 1000) #call back create unique id
	json_data["params"]["file"]["name"] = filename #add filename
	json_data["params"]["file"]["data"] = bytes.encode("base64","strict") #encode the data
	json_data["params"]["options"]["reference"] = "uw reference " + time.strftime("%c")
	
	try:
		from websocket import create_connection
		ws = create_connection("ws://connect.aerius.nl/connect/1/services", 10000)
		
	except Exception, msg:
		print "Unexpected connection error %s" % msg
		return
		
	try:
	    # sending data
		ws.send(json.dumps(json_data))
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