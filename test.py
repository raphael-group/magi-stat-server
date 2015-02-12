import json
import urllib2

if __name__ == "__main__":
	with open("example-association-data.json") as f:
		data = json.load(f)

	req = urllib2.Request('http://127.0.0.1:8888/')
	req.add_header('Content-Type', 'application/json')
	response = urllib2.urlopen(req, json.dumps(data))

	print response.read()

						   
							   
