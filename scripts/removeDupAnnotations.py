from pymongo import MongoClient
import pprint

client = MongoClient()
client = MongoClient('localhost', 27017)

db = client.dataset
imageAnnotations = db.imageAnnotations
cursor = imageAnnotations.find({})
counter = 0
lastBreak = 157400
labelRecordsCount = 167018

for document in cursor:
	counter = counter +1
	if counter>lastBreak:
		print (counter,"/",labelRecordsCount," \r")
		imageID = document['imageID']
		annotations = []
		annotations = document['annotations']
		annotations = list(set(annotations))
		imageAnnotations.update({
	 			"imageID" : imageID
	 			},
	 			{
	 			"imageID" : imageID,
	 			"annotations": annotations
	 			})