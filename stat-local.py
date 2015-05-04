#!/usr/bin/python

import argparse
import json
import os
import subprocess
import stats as S # local
import sys
import unittest

class TestStatLocal(unittest.TestCase):
	pass

def test_generator_local(input_file, output_file):
	def test(self):
		with open( "tests/" + input_file) as fin:
			str_in = fin.read()
		
		args = ["python", "./stat-local.py", "--inputdata=" + str_in]
		file_result = subprocess.check_output(args)

		returned = json.loads(file_result)
		with open( "tests/" + output_file) as fout:
			json_out = json.load(fout)

		self.assertEqual(returned, json_out) # input_file
		
	return test

# generate all the tests
test_files = os.listdir('tests/')
input_files = [f for f in test_files if f[-3:] == '.in']
output_files = [f for f in test_files if f[-4:] == '.out']

# generate a new test for each line in the test list file
for file_in in input_files:
	# a writable name
	test_name = file_in.split('.')[0]
	file_out = test_name + '.out'
	if file_out in output_files:
		# add the test
		setattr(TestStatLocal, "test_" + test_name, \
				test_generator_local(file_in, file_out))
		
if __name__ == "__main__":
	stat_packages = dict(contingency=S.contingency_tests,
					 partitions=S.partition_tests)

	parser = argparse.ArgumentParser('Statistics command-line engine for MAGI.')
	
	parser.add_argument('--inputdata', default='{}', help='data in stringifyed json', type = json.loads)
	
#	parser.add_argument('--stattype', help='statistics request type', choices = stat_packages.keys)
	
	args = parser.parse_args()

	rawdata = []	
	if args.inputdata:
		rawdata = args.inputdata
	else:
		# todo: allow streaming to input of data
		print "Currently not supporting streaming, provide --inputdata"
		sys.exit(1)
		pass

	request_type = "contingency" # default
	if "request" in rawdata:
		request_type = rawdata["request"]
	elif "stattype" in args: # command line arge takes precedence
		request_type = args.stattype

	# producing a response now
	if not request_type:
		result = {"Error": ["Unknown request"]}
	else:
		# get the correct stat engine
		engine = stat_packages[request_type]()

		errors = engine.validate(rawdata)
		if errors:
			for err in errors:
				result = {"Error": errors}
		else:
			# calculate result and print to output
			result = engine.tests(rawdata)
			result['request'] = request_type
			
	print json.dumps(result, sort_keys=True, indent=4)
	sys.exit(0)
	
	
