import json
import requests
import argparse

def submit(data, port):
	site = 'http://127.0.0.1:%d/' % port
	r = requests.post(site, json.dumps(data))
	return r.text
	
# submit a json as a file to the statistics server
if __name__ == "__main__":
	parser = argparse.ArgumentParser('Submit a json file to the statistics server.')
	parser.add_argument('file', help='JSON file to submit', type=argparse.FileType('r'))
	parser.add_argument('--port', default=8888, help='port that the statistics server runs on', type=int)
	args = parser.parse_args()

	# send out the file
	print submit(json.load(args.file), args.port)
	
						   
							   
