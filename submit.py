import json
import urllib2
import argparse

def submit(data, port):
	req = urllib2.Request('http://127.0.0.1:%d/' % port)
	req.add_header('Content-Type', 'application/json')
	return urllib2.urlopen(req, json.dumps(data)).read()

# submit a json as a file to the statistics server
if __name__ == "__main__":
	parser = argparse.ArgumentParser('Submit a json file to the statistics server.')
	parser.add_argument('file', help='JSON file to submit', type=argparse.FileType('r'))
	
	parser.add_argument('--port', default=8888, help='port that the statistics server runs on')
	args = parser.parse_args()

	# send out the file
	print submit(json.load(args.file), args.port)
	
						   
							   
