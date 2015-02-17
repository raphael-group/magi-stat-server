import argparse
import json
import unittest
import submit

class TestStatServer(unittest.TestCase):
	pass

def test_generator(input_file, output_file, port):
	def test(self):
		with open('tests/' + input_file) as fin:
			json_in = json.load(fin)
		with open('tests/' + output_file) as fout:
			json_out = json.load(fout)

		returned = json.loads(submit.submit(json_in, port))
		print type(returned)
		self.assertEqual(returned, json_out) # input_file
		
	return test

if __name__ == "__main__":
	# set default for the test file
	parser = argparse.ArgumentParser('Submit a json file to the statistics server.')
	parser.add_argument('--profile', help='two-column list of files', type=argparse.FileType('r'),
						default='tests/testlist.txt')
	parser.add_argument('--port', default=8888, help='port that the statistics server runs on')

	args = parser.parse_args()

	# generate a new test for each line in the test list file
	for line in args.profile:
		profile = line.rstrip().split(' ')
		# a writable name
		name = profile[0].split('.')[0]
		test_name = 'test_' + name
		
		# add the test
		setattr(TestStatServer, test_name, test_generator(*profile, port=args.port)) 

	unittest.main()
						   
							   
