This branch of MAGI is meant to serve enrichment queries.  These queries are statistics that are requested by the user among different categories, such as gender, survival or mutation status.

## Input data format ##
Enrichment queries can either be served as AJAX requests to a server or as locally on the command line.  In either case a query is formed as a JSON body with the fields "X" and "Y", which should be two lists of equal length and the same type, representing the category membership of a sample.  Examples of proper JSON bodies can be found as .in files with the tests folder.

If no category membership exists for a sample (e.g. the mutation status of a sample is unknown), then the string "null" can replace the value and the sample will be treated as missing data in the calculation.

## Available test types ##
Tests currently exists for two categories (and their labeled type):
* to determine if the two categories are associated (contingency).  This is done with Fisher's exact test or the chi-squared test.  The appropriate test is chosen based on the number of categories in the X and Y lists.

* whether two partitions are similar in their clusterings (partition).  This is done with the Adjusted Rand Index.

The labeled type is given in the "request" field in the JSON body, which must be one of the labeled types.  If no request field is given, then the request is assumed to be "contingency".

## Output format ##
The output contains the following fields:
* request: The request type that was given
* samplesRemoved: The number of samples marked as missing (null)
* stats: A map of data related to the statistics result, including:
** A header string giving a human-readable description of the test
** X: the distinct categories in the "X" input JSON
** Y: the distinct categories in the "Y" input JSON
** p: the p-value of the given test,
** report: formatted deescriptions of the test result in a dictionary, including
*** html
*** tex
* table: A list of lists, row-wise, containing the contingency table, including row and column headers.

## Examples for running: ##
To run the server:	
> python statserver.py --port=19999

To test the server:
> python runTests.py --port=19999

To submit a JSON file to the server:
> python submit.py --port=19999

To run a file locally (no server required):
> python stat-local.py --inputdata=$(cat tests/example.in)

To test the local interface:
> python -m unittest stat-local