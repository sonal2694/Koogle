from pymongo import MongoClient
import pprint

client = MongoClient()
client = MongoClient('localhost', 27017)

db = client.dataset
labels = db.labels
dictCollection = db.dict
destinationCollection = db.imageAnnotations
cursor = labels.find({}).batch_size(30)

labelRecordsCount =  cursor.count()

counter = 0

try:
	for document in cursor:
		counter = counter + 1
		print " ",counter,"/",labelRecordsCount," \r",

		imageID = document['ImageID']
		labelName = document['LabelName']
		result = dictCollection.find_one({"dictID": labelName})
		if result:
			splittedLabels = result['label'].split(' ')
			for i in splittedLabels:
				destinationCollection.update(
					{
						"imageID" : imageID
					},
					{
						"$push": {"annotations": i}
					}, upsert=True)
	print counter
except:
	print counter
cursor.close()
