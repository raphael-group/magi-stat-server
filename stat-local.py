#!/usr/bin/python

import argparse
import json
import sys
import stats as S # local

if __name__ == "__main__":
	stat_packages = dict(contingency=S.contingency_tests,
					 partitions=S.partition_tests)

	parser = argparse.ArgumentParser('Statistics command-line engine for MAGI.')
	
	parser.add_argument('--inputdata', default='{}', help='data in stringifyed json', type = json.loads)
	
#	parser.add_argument('--stattype', help='statistics request type', choices = stat_packages.keys)
	
	args = parser.parse_args()

	rawdata = []	
	if "inputdata" in args:
		rawdata = args.inputdata
	else:
		# todo: allow streaming to input of data
		pass

	request_type = "contingency" # default
	if "request" in rawdata:
		request_type = rawdata["request"]
	elif "stattype" in args: # command line arge takes precedence
		request_type = args.stattype
	
	if not request_type:
		print "Error: statistics type not specified"
		sys.exit(1)

	# get the correct stat engine
	engine = stat_packages[request_type]()

	errors = engine.validate(rawdata)
	if errors:
		for err in errors:
			print "Error: " + err
		sys.exit(1)

	# calculate result and print to output
	result = engine.tests(rawdata)
	print json.dumps(result, sort_keys=True, indent=4)
	sys.exit(0)
	
	
