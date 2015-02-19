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
def fisher(c_table): # two-sided
	return {"p": stats.fisher_exact(c_table)[1]}

def chi_square(c_table):
	res = dict(zip(["chi2", "p", "dof", "expected"],
				  stats.chi2_contingency(c_table)))
	res["valid"] = bool((res["expected"] >= 5).all())
	res["expected"] = res["expected"].tolist()
	return res
