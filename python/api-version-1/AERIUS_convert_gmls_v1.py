#!/usr/bin/python
import json
import time
from os import listdir
import os
from pprint import pprint

"""
Open the file, create json object send this json to AERIUS connect endpoint
Process the result test on successful and write the result to a result file
"""
def gml_convert(inputDir, filename, outputDir):
	f = open(os.path.join(inputDir, filename),'rb')
	bytes = f.read()
	f.close
	# create json text object
	json_text = """
	{
		"jsonrpc":"2.0",
		"id":0,
		"method":"gmlconvert.convert",
		"params":{"file":
			{
				"name":"",
				"data":""
			}}
	}
	"""
	# replace paramaters
	json_data = json.loads(json_text)
	json_data["id"] = long(time.time() * 1000) #create unique id
	json_data["params"]["file"]["name"] = filename #add filename
	json_data["params"]["file"]["data"] = bytes.encode("base64","strict") #encode the data

	try:
		from websocket import create_connection
		ws = create_connection("ws://connect.aerius.nl/connect/1/services", 10000)
		
	except Exception, msg:
		print "Unexpected connection error %s" % msg
		return
		
	try:
	    #sending data
		ws.send(json.dumps(json_data))
		result = ws.recv()
		# write result part
		if result.find("successfull") > -1:
			if (result.find("filename") > -1):
				# we have result
				json_input = json.loads(result)
				if not (filename.lower().find('.gml') > -1):
					filename += ".gml"
				filename = os.path.join(outputDir, filename)
				print "writing result %s" % filename
				fileOut = open(filename, "w+")
				fileOut.write(json_input["result"]["data"])
				
			else:
				# we have aerius errors
				json_input = json.loads(result)
				filename = os.path.join(outputDir, "error" + "_"  + filename + "_error.txt")
				print "error in conversie writing output %s" % filename
				print "error '%s'" % json_input
				fileOut = open(filename, "w+")
				fileOut.write("%s" % json_input)
				
		else: 
			# we have JSON-RPC error
			filename = os.path.join(outputDir, "error" + "_"  + filename + "_error.txt")
			fileOut = open(filename, "w+")
			fileOut.write("%s" % result)

	except Exception, msg:
		print "Unexpected result error %s" % msg
		
	finally:
		ws.close()
		
	return
	
# read files from directory 
# make sure output dir exists and has only files
print "start"
inputDir = 'c://tmp//input'
outputDir = 'c://tmp//output'
files = listdir(inputDir)
for file in files:
	print "reading %s" % file
	gml_convert(inputDir, file, outputDir)