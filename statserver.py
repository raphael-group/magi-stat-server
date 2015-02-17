import argparse
import json
import numpy
import tornado.ioloop
import tornado.web
import stats as S
# local

# expects that rawdata contains two homogeneous vectors under entries 'X' and 'Y' of equal length
def contingency_tests(rawdata):
	# Sometimes JSON loading once isn't enough, in which case 
	if type(rawdata) == type(u""): rawdata = json.loads(rawdata)
	stat_funs = {"chi-squared": S.chi_square, "fisher": S.fisher}
	
	# get contingency table
	(c_table, x_cats, y_cats) = S.tabulate(rawdata['X'], rawdata['Y'])

	# check for 2x2
	result = {}
	if len(x_cats) == 2 and len(y_cats) == 2:
#		print "2x2!"
		comparison = {"X1": x_cats[0],
					  "X2": x_cats[1],
					  "Y1": y_cats[0],
					  "Y2": y_cats[1]}

		stats = {}
		for key, method in stat_funs.iteritems():
			stats[key] = method(c_table)

		result = {"table": c_table.tolist(), "comparison": comparison, "stats": stats}
	else: # don't handle anything besides 2x2 for now
		result = {}
	return result

# rounds all the floats in a json
def round_all(obj, N):
	if isinstance(obj, float):
		return round(obj, N)
	elif isinstance(obj, dict):
		return dict((k, round_all(v, N)) for (k, v) in obj.items())
	elif isinstance(obj, (list, tuple)):
		return map(lambda(o): round_all(o, N), obj)
	return obj

class StatsHandler(tornado.web.RequestHandler):
	def _validate(self, raw): 
		errors = []
		if 'X' not in raw:
			errors.append("Missing X variable")
		else:
			# check for homogeneous type
			Xt = map(type, raw['X'])
			if any([t != Xt[0] for t in Xt]):
				errors.append("X has non-homogeneous type")
			
		if 'Y' not in raw:
			errors.append("Missing Y variable")
		else:
			Yt = map(type, raw['Y'])
			if any([t != Yt[0] for t in Yt]):
				errors.append("Y has non-homogeneous type")

		if 'X' in raw and 'Y' in raw: # should be same length
			if len(raw['X']) <> len(raw['Y']):
				errors.append('X and Y are unequal lengths')

		return errors

	# take in a dict / other jsonable object and send it back
	def _return(self, reply):
		result = round_all(reply, 4)
		self.set_header("Content-Type", "application/json")
		self.set_header("Access-Control-Allow-Origin", "*")
		self.write(json.dumps(result, sort_keys=True, indent=4))
		self.finish()
		
	def post(self):
		rawdata = json.loads(self.request.body)

		errors = self._validate(rawdata)
		if errors:
			self._return({"Error": errors})
			return
			
		# apply result
		result = contingency_tests(rawdata)
		self._return(result)

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
	print "Accepting JSON requests over HTTP on port %d" % args.port
	tornado.ioloop.IOLoop.instance().start()

