import argparse
import httplib
import json
import numpy
import tornado.ioloop
import tornado.web
import stats as S # local

# expects that rawdata contains two homogeneous vectors under entries 'X' and 'Y' of equal length
def contingency_tests(rawdata):
	stat_funs = {"chi-squared": S.chi_square, "fisher": S.fisher}

	# remove the nulls
	xIndicesToRemove = set( i for i, x in enumerate(rawdata['X']) if x is None or x.lower() == 'null' )
	yIndicesToRemove = set( i for i, y in enumerate(rawdata['Y']) if y is None or y.lower() == 'null' )
	indicesToRemove = xIndicesToRemove | yIndicesToRemove
	rawdata['X'] = [ x for i, x in enumerate(rawdata['X']) if i not in indicesToRemove ]
	rawdata['Y'] = [ y for i, y in enumerate(rawdata['Y']) if i not in indicesToRemove ]
		
	# get contingency table
	(c_table, x_cats, y_cats) = S.tabulate(rawdata['X'], rawdata['Y'])

	# construct the results object, including the contingency table
	result = dict(table=[[""] + list(y_cats)], \
				  stats={}, \
				  samplesRemoved=len(indicesToRemove))
	for x, row in zip(x_cats, c_table.tolist()):
		result['table'].append([x] + row)


	# check the number of categories
	if len(x_cats) == 1 or len(y_cats) == 1: # can't run tests on a vector
		pass
	elif len(x_cats) == 2 and len(y_cats) == 2:
		for key, method in stat_funs.iteritems():
			result['stats'][key] = method(c_table)
	else:
		# run the r x c chi-squared test
		result['stats'] = S.chi_square(c_table)

		# calculate marginal distributions
		margin_X = numpy.sum(c_table,1)
		margin_Y = numpy.sum(c_table,0)
		total = numpy.sum(margin_X)
		
		# generate all pairs of categories
		range_X = range(len(x_cats)) if len(x_cats) > 2 else [0]
		range_Y = range(len(y_cats)) if len(y_cats) > 2 else [0]
		i_pairs = [(x,y) for x in range_X for y in range_Y]

		posthoc = []
		for i,j in i_pairs:
			# create the 2 x 2 contingency table
			sub_table = numpy.zeros((2,2))
			sub_table[0,0] = c_table[i,j]
			sub_table[0,1] = margin_X[i] - c_table[i,j]
			sub_table[1,0] = margin_Y[j] - c_table[i,j]
			sub_table[1,1] = total - numpy.sum(sub_table)
			
			sub_result = dict(stats={})
			if len(x_cats) > 2:
				sub_result['Xcat'] = x_cats[i]
			if len(y_cats) > 2:
				sub_result['Ycat'] = y_cats[j]
				
			for key, method in stat_funs.iteritems():
				sub_result['stats'][key] = method(sub_table)
			posthoc.append(sub_result)

		result['posthoc'] = posthoc

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
			Xt = set(map(type, raw['X']))
			if type(None) in Xt: Xt.remove(type(None))
			if len(Xt) > 1:
				errors.append("X has non-homogeneous type")
			
		if 'Y' not in raw:
			errors.append("Missing Y variable")
		else:
			Yt = set(map(type, raw['Y']))
			if type(None) in Yt: Yt.remove(type(None))
			if len(Yt) > 1:
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
		# load raw data
		rawdata = json.loads(self.request.body)

		# Sometimes JSON loading once isn't enough, in which case load it again
		# TODO: figure out why you need this, doesn't make any sense
		if type(rawdata) == type(u""): rawdata = json.loads(rawdata)

		# check for any known errors
		errors = self._validate(rawdata)
		if errors:
			self.set_status(httplib.BAD_REQUEST)
			self._return({"Error": errors})
			return
			
		# apply result
		result = contingency_tests(rawdata)		
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

