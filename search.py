# Working program
from nltk.corpus import stopwords
from flask import Flask, request, render_template
from pymongo import MongoClient
from collections import Counter
from itertools import repeat, chain
import collections
import json
import itertools
import pprint
import os
#from nltk.stem.porter import PorterStemmer
#from nltk.stem.wordnet import WordNetLemmatizer
app = Flask(__name__)
filename = 'data.txt'

@app.route("/")
def main():
    return render_template('search.html')

@app.route("/send", methods=['POST'])
def send():
    query = request.form['query']
    query = query.lower()
    cachedStopwords = stopwords.words("english")
    query = ' '.join([word for word in query.split() if word not in cachedStopwords])
    q=query.split(" ")
    client = MongoClient()
    client = MongoClient('localhost', 27017)

    db = client.dataset
    invertedIndex = db.InvertedIndex
    labels = db.labels
    images = db.images
    out = open(filename, 'a')
    out.truncate(0);

    loadedImages = []
    for i in q:
        result = invertedIndex.find_one({"label": i})
        if result:
            for k in result['image']:
                Image = labels.find_one({"LabelName": k})
                if Image is not None:
                    url = images.find_one({"ImageID": Image['ImageID']})
                    if url not in loadedImages:
                        loadedImages.append(url)
                        out.write(url['Thumbnail300KURL'] + " " + Image['ImageID'] + " " + k + '\n' )

    out.close()

    arr = []
    c = 0
    f = open(filename, 'r')

    for line in f:
        imageStuff = line.rstrip("\n")
        imageParts = imageStuff.split(" ")
        imageUrl = imageParts[0]
        arr.append(imageParts)

    return render_template('result.html', text=request.form['query'], data=arr)

@app.route('/add_keywords', methods=['POST'])
def add_keywords():
    imageID = request.json['imageID']
    keywords = request.json['query_words']
    query = []
    query = keywords.split(" ")

    client = MongoClient()
    client = MongoClient('localhost', 27017)
    db = client.dataset
    markovChain = db.markovChain

    imageAnnotations = db.imageAnnotations
    result = imageAnnotations.find_one({"imageID": imageID})
    if result:
        annotations = result['annotations']
        for i in query:
            if i in annotations:
                annotations.remove(i)

        res1 = markovChain.find_one({"fromState": query, "toState": annotations})
        if res1:
            old_prob = res1['prob']
            M = res1['M']
            new_prob1 = ((M*old_prob)+1)/(M+1)
            markovChain.update(
            {
                "fromState": query,
                "toState": annotations
            },
            {
                '$set': {"prob": new_prob1, "M": M+1}
            })

        else:
            res2 = markovChain.find_one({"fromState": query})
            if res2:
                M = res2['M']
            else:
                M = 0
            new_prob1 = 1/(M+1)
            markovChain.insert_one(
                {
                    "fromState": query,
                    "toState": annotations,
                    "prob": new_prob1,
                    "M": M+1
                })

        cursor = markovChain.find({"fromState": query, "toState": { '$ne': annotations }})
        for document in cursor:
            toState = document['toState'] 
            old_prob = document['prob']
            new_prob2 = ((M*old_prob))/(M+1)
            markovChain.update(
            {
                "fromState": query,
                "toState": toState
            },
            {
                '$set': {"prob": new_prob2, "M": M+1}
            })

    # associatedTags = db.associatedTags

    # #adding the keywords if an entry for the image already exists
    # result = associatedTags.find_one({"imageID": imageID})
    # if result:
    #     for i in tags:
    #         if i not in result['tags']:
    #             temp_tags = result['tags']
    #             temp_tags.append(i)
    #             res = db.associatedTags.update_one({'imageID': imageID}, {'$set': {'tags':temp_tags}},)

    # #adding a new imageID and its keywords
    # else:
    #     result = db.associatedTags.insert_one({"imageID": imageID, "tags": tags})

    return ("Image ID is:"+imageID+" Tags: "+keywords)

@app.route('/remove_keywords', methods=['POST'])
def remove_keywords():
    imageID = request.json['imageID']
    keywords = request.json['query_words']
    tags = []
    tags = keywords.split(" ")

    client = MongoClient()
    client = MongoClient('localhost', 27017)
    db = client.dataset
    associatedTags = db.associatedTags

    result = associatedTags.find_one({"imageID": imageID})
    if result:
        for i in tags:
            if i in result['tags']:
                temp_tags = result['tags']
                temp_tags.remove(i)
                res = db.associatedTags.update_one({'imageID': imageID}, {'$set': {'tags':temp_tags}},)

    return ("Removed Image ID is:"+imageID+" Tags: "+keywords)


if __name__ == "__main__":
    app.run()
