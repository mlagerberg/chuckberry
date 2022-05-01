import json
import requests
from tag import Tag, TagFormatError

def fetch(endpoint):
	response = requests.get(endpoint)
	return response.json()

def loadFile(path):
	f = open(path, "r")
	data = json.loads(f.read())
	f.close()
	return data

def getTags(endpoint):
	data = {}
	if endpoint.startswith('http:') or endpoint.startswith('https:'):
		data = fetch(endpoint)
	else:
		data = loadFile(endpoint)
	if not "data" in data:
		print(f'Error loading project from {endpoint}')
		return {}
	if not "tags" in data["data"]:
		print('Project does not contain tags configuration')
		return {}
	tags = data["data"]["tags"]
	result = {}
	for tagValues in tags:
		try:
			tag = Tag(tagValues)
			result[tag.number] = tag
			tag.print()
		except TagFormatError:
			print('Invalid tag:', tagValues)
	return result
