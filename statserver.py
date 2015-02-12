import json
import numpy
import tornado.ioloop
import tornado.web
from scipy import stats

# return contingency table, x categories, y categories
def tabulate(x_list, y_list):
	x_cats, xinv = numpy.unique(x_list, return_inverse=True)
	y_cats, yinv = numpy.unique(y_list, return_inverse=True)

	c_table = numpy.zeros((len(x_cats), len(y_cats)))
	for pair in zip(xinv, yinv):
		c_table[pair[0]][pair[1]] += 1

	return (c_table, x_cats, y_cats)

# statistics reporters
def stat_fisher(c_table):
	return {"p": stats.fisher_exact(c_table)[1]}

def stat_chisquare(c_table):
	res = dict(zip(["chi2", "dof", "p", "expected"],
				  stats.chi2_contingency(c_table)))
	res["valid"] = bool((res["expected"] >= 5).all())
	res["expected"] = res["expected"].tolist()
	return res

# expects that rawdata contains two vectors under entries 'X' and 'Y' of equal length
def contingency_tests(rawdata):
	stat_map = {"chi-squared": stat_chisquare, "fisher": stat_fisher}
	# todo: make all this async
	# get contingency table
	(c_table, x_cats, y_cats) = tabulate(rawdata['X'], rawdata['Y'])

	# check for 2x2
	result = {}
	if len(x_cats) == 2 and len(y_cats) == 2:
		comparison = {"X1": x_cats[0],
					  "X2": x_cats[1],
					  "Y1": y_cats[0],
					  "Y2": y_cats[1]}

		stats = {}
		for key, method in self.stat_map.iteritems():
			stats[key] = method(c_table)

		result = {"table": c_table.tolist(), "comparison": comparison, "stats": stats}
	else: # don't handle anything besides 2x2 for now
		result = {}
		
	return result

class StatsHandler(tornado.web.RequestHandler):
	def badRequest(self):
		self.set_status(http.HTTPStatus.BAD_REQUEST)
		self.finish()
		
	def post(self):
		# todo: check other features of request
		rawdata = json.loads(self.request.body)
		
		if 'X' not in rawdata or 'Y' not in rawdata:
			self.badRequest()
			return

		# todo: async this
		result = contingency_tests(rawdata)
		self.set_header("Content-Type", "application/json")
		self.write(json.dumps(result, sort_keys=True))

# tell the backend server to accept on "/" only
application = tornado.web.Application([
	(r"/", StatsHandler),
])

# listen on port 8888: todo: export to other ports based on command-line arg
if __name__ == "__main__":
	application.listen(8888)
	tornado.ioloop.IOLoop.instance().start()

