# a local statistics 
from scipy import stats
import numpy

# return contingency table, x categories, y categories
def tabulate(x_list, y_list):
	x_cats, xinv = numpy.unique(x_list, return_inverse=True)
	y_cats, yinv = numpy.unique(y_list, return_inverse=True)

	c_table = numpy.zeros((len(x_cats), len(y_cats)))
	for pair in zip(xinv, yinv):
		c_table[pair[0]][pair[1]] += 1

	return (c_table, x_cats, y_cats)

# statistics reporters
class Fisher(object):
	def calc(self, c_table): # two-sided
		p = stats.fisher_exact(c_table)[1]
		return {"p": p, \
				"report": "p = %0.4f" % p}
	
	def title(self, x_cats, y_cats):
		return "Fisher's exact test, %s vs %s on %s vs %s membership" % \
		   (x_cats[0], x_cats[1], y_cats[0], y_cats[1])

class ChiSquare(object):
	def calc(self, c_table):
		res = dict(zip(["chi2", "p", "dof", "expected"],
				  stats.chi2_contingency(c_table)))
		res["valid"] = bool((res["expected"] >= 5).all())
		res["expected"] = res["expected"].tolist()
		res["report"] = "\chi^2(%d) = %0.4f, p = %0.4f" % \
						(res['dof'],res['chi2'],res['p'])
		return res

	def title(self, x_cats, y_cats):
		return "Chi square test, (%s) on (%s) membership" % \
		   (", ".join(x_cats), ", ".join(y_cats))
