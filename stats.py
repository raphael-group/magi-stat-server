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
	def __init__(self, x_cats, y_cats):
		self.x_cats = list(x_cats)
		self.y_cats = list(y_cats)

	def calc(self, c_table): # two-sided
		p = stats.fisher_exact(c_table)[1]
		html = "<b>P</b>-value = %s" % format(p, 'g')
		tex = "$P = %s$" % format(p, 'g')
		res = dict(p=p, X=", ".join(self.x_cats), Y=", ".join(self.y_cats),
				   report=dict(tex=tex, html=html))
		return res
	
	def title(self):
		return "Fisher's exact test, %s vs %s on %s vs %s membership" % \
		   (self.x_cats[0], self.x_cats[1], self.y_cats[0], self.y_cats[1])

class Chi2(object):
	def __init__(self, x_cats, y_cats):
		self.x_cats = list(x_cats)
		self.y_cats = list(y_cats)

	def calc(self, c_table):
		res = dict(zip(["chi2", "p", "dof", "expected"],
				  stats.chi2_contingency(c_table)))
		res["Valid (all cells > 5)"] = bool((res["expected"] >= 5).all())
		res["Expected"] = res["expected"].tolist()
		res["X"] = ", ".join(self.x_cats)
		res["Y"] = ", ".join(self.y_cats)
		tex = "$\chi^2(%d) = %0.4f, P = %0.4f$" % (res['dof'],res['chi2'],res['p'])
		html = "&chi;<sup>2</sup>(%d) = %s, <b>P</b>-value = %s" % (res['dof'],format(res['chi2'], 'g'),format(res['p'], 'g'))
		res["report"] = dict(tex=tex, html=html)
		return res

	def title(self):
		return "Chi square test, (%s) on (%s) membership" % \
		   (", ".join(self.x_cats), ", ".join(self.y_cats))
