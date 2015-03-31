#!/usr/bin/python

import argparse
import httplib
import json
import numpy
import time
import tornado.ioloop
import tornado.web
import stats as S # local

# rounds all the floats in a json
def round_all(obj, N):
	if isinstance(obj, float):
		return round(obj, N)
	elif isinstance(obj, dict):
		return dict((k, round_all(v, N)) for (k, v) in obj.items())
	elif isinstance(obj, (list, tuple)):
		return map(lambda(o): round_all(o, N), obj)
	return obj

def time_print(s):
	ts = time.strftime("[%m/%d/%y %H:%M:%S]")
	print ts + ": " + s
	
##### request handler which takes in POST requests and returns JSONs #####
class StatsHandler(tornado.web.RequestHandler):
	# take in a dict / other jsonable object and send it back
	def _return(self, reply):
		# logging
		if self.get_status() == httplib.OK:
			table = reply['table']
			r, c = len(table) - 1, len(table[0]) - 1
			time_print("Reply OK: Received request type %s (%d x %d), categorical test results." % (reply['request'], r, c))
		elif self.get_status() == httplib.BAD_REQUEST:
			errors = reply['Error']
			time_print("Reply BAD_REQUEST: Received bad request: "+ ";".join(errors))

		result = round_all(reply, 4)
		self._send_message(result)
		
	def _send_message(self, reply):
		self.set_header("Content-Type", "application/json")
		self.set_header("Access-Control-Allow-Origin", "*")
		self.write(json.dumps(reply, sort_keys=True, indent=4))
		self.finish()

	def get(self):
		info = {'Name': 'Magi Statistics server'}
		time_print("Received GET information request")
		
		self._send_message(info)
		
	def post(self):
		# load raw data
		rawdata = json.loads(self.request.body)

		# Sometimes JSON loading once isn't enough, in which case load it again
		# TODO: figure out why you need this, doesn't make any sense
		if type(rawdata) == type(u""): rawdata = json.loads(rawdata)

		# choose the request type
		requestType = "contingency" # default
		if "request" in rawdata:
			requestType = rawdata["request"]

		# check if we have that request
		stat_packages = dict(contingency=S.contingency_tests,
							 partitions=S.partition_tests)

		if requestType not in stat_packages:
			self.set_status(httplib.BAD_REQUEST)
			self._return({"Error": ["Unknown request"]})
			return

		# get the statistics package
		engine = stat_packages[requestType]()
		
		# check for any known errors
		errors = engine.validate(rawdata)
		if errors:
			self.set_status(httplib.BAD_REQUEST)
			self._return({"Error": errors})
			return
			
		# compute result
		result = engine.tests(rawdata)		
		result['request'] = requestType 
		self._return(result)

################## server code #####################
		
# tell the backend server to accept on "/" only
application = tornado.web.Application([
	(r"/", StatsHandler),
])

# listen on port 8888: todo: export to other ports based on command-line arg
if __name__ == "__main__":
	parser = argparse.ArgumentParser('Run a JSON-based statistics server.')
	parser.add_argument('--port', default=8888, help='port that the statistics server runs on', type=int)
	args = parser.parse_args()

	application.listen(args.port)
	print "Accepting JSON requests over HTTP on port %d..." % args.port
	tornado.ioloop.IOLoop.instance().start()

