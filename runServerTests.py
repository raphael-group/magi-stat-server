import argparse
import json
import os
import subprocess
import sys
import unittest
import submit # local

class TestStatServer(unittest.TestCase):
	pass

def test_generator_server(input_file, output_file, port):
	def test(self):
		with open('tests/' + input_file) as fin:
			json_in = json.load(fin)
		with open('tests/' + output_file) as fout:
			json_out = json.load(fout)

		returned = json.loads(submit.submit(json_in, port))
		self.assertEqual(returned, json_out) # input_file
		
	return test

if __name__ == "__main__":
	# set default for the test file
	parser = argparse.ArgumentParser('Submit a json file to the statistics server.')
	parser.add_argument('--dir', help='directory', type=str, default='tests/')
	parser.add_argument('--port', default=8888, help='port that the statistics server runs on', type=int)

	# parse only the arguments you need:
	# todo: pass the other arguments to unittest
	args = parser.parse_known_args(sys.argv)[0]
	test_files = os.listdir(args.dir)
	input_files = [f for f in test_files if f[-3:] == '.in']
	output_files = [f for f in test_files if f[-4:] == '.out']

	# generate a new test for each line in the test list file
	for file_in in input_files:
		# a writable name
		test_name = file_in.split('.')[0]
		file_out = test_name + '.out'
		if file_out in output_files:
			# add the test
			setattr(TestStatServer, "test_" + test_name, \
					test_generator_server(file_in, file_out, port=args.port)) 

	# pass only the title to unittest			
	unittest.main(argv = ['testServer.py'])
						   
							   
