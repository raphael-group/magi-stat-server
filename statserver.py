import argparse
import httplib
import json
import numpy
import tornado.ioloop
import tornado.web
import stats as S # local

##### request handler which takes in POST requests and returns JSONs #####
class StatsHandler(tornado.web.RequestHandler):
	# take in a dict / other jsonable object and send it back
	def _return(self, reply):
		# logging
		if self.get_status() == httplib.OK:
			table = reply['table']
			r, c = len(table) - 1, len(table[0]) - 1
			print "Received request type %s (%d x %d), returning OK, categorical test results." % (reply['request'], r, c)
		elif self.get_status() == httplib.BAD_REQUEST:
			errors = reply['Error']
			print "Received bad request, returning BAD_REQUEST, errors: " + ";".join(errors)

		self.set_header("Content-Type", "application/json")
		self.set_header("Access-Control-Allow-Origin", "*")
		self.write(json.dumps(result, sort_keys=True, indent=4))
		self.finish()
		
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

