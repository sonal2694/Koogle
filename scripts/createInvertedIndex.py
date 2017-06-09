from pymongo import MongoClient
import pprint

client = MongoClient()
client = MongoClient('localhost', 27017)

db = client.dataset
collection = db.dict
destinationCollection = db.InvertedIndex
cursor = collection.find({})


for document in cursor:
	splittedLabels = document['label'].split(' ')
 	for i in splittedLabels:
 		destinationCollection.update({
 			"label" : i
 			},{
 			"$push": {"image": document['dictID']}
 			},upsert=True)

#cursor2 = destinationCollection.find({})
#counter = 0
#for i in cursor2:
#	if len(i['image']) > 1:
		# pprint.pprint(i)
#		counter += 1
	# pprint.pprint(i['image'])

#print("Number of Labels with multiple images: ")
#print(counter)