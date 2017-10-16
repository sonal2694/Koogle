# The code below forms the back-end of the application

# packages imported in python

from nltk.corpus import stopwords
from flask import Flask, request, render_template
from pymongo import MongoClient
from collections import Counter
from itertools import repeat, chain
from itertools import chain, combinations
import collections
import json
import itertools
import pprint
import os

#  Flask uses the import name to know where to look up resources,
# templates, static files, instance folder. "__name__" is just a 
# convenient way to get the import name of the place the app is
# defined.

app = Flask(__name__)
filename = 'data.txt'

# Connecting to MongoDB

client = MongoClient()
client = MongoClient('localhost', 27017)
db = client.dataset
images_all =[]

# @app.route is a decorator used to match URLs to view functions in Flask apps.

@app.route("/")
def main():
    return render_template('search.html')

# Function where queries are received and images pertaining to it are
# retrived and ranked using the algorithm Koogle.

@app.route("/send", methods=['POST'])
def send():
    query = request.form['query']
    query = query.lower()
    cachedStopwords = stopwords.words("english")
    query = ' '.join([word for word in query.split() if word not in cachedStopwords])
    q=query.split(" ")

    invertedIndex = db.InvertedIndex
    labels = db.labels
    images = db.images

    del images_all[:]
    subsets = list(powerset(q))
    subsets.reverse()
    for s in subsets:
        s = list(s)
        retrieve_images(s)
        markovian_keywords = get_markov_keywords(s)
        if markovian_keywords:
            for i in markovian_keywords:
                retrieve_images(i)

    # getting the URLs of all the images retrieved in a .txt file

    out = open(filename, 'a')
    out.truncate(0);
    for i in images_all:
        res = images.find_one({"ImageID": i})
        out.write(res['Thumbnail300KURL'] + " " + i + '\n' )
    out.close()

    # Storing all the details of the retrieved images in an array that is
    # then sent to the front-end "result.html" via flask.

    arr = []
    f = open(filename, 'r')
    for line in f:
        imageStuff = line.rstrip("\n")
        imageParts = imageStuff.split(" ")
        arr.append(imageParts)

    return render_template('result.html', text=request.form['query'], data=arr)


# Finding the subsets of a list of keywords in the ascending order

@app.route('/powerset/<iterable>')
def powerset(iterable):
    q = list(iterable)
    return chain.from_iterable(combinations(q,r) for r in range(1, len(q)+1))

# Retrieving pictures from the database

@app.route('/retrieve_images/<s>')
def retrieve_images(s):
    count = 0
    imageAnnotations = db.imageAnnotations
    cursor_one = imageAnnotations.find({"annotations": {'$all': s}})
    for document in cursor_one:
        #to limit the number of images we get everytime
        if (count < 40):
            imageID = document['imageID']
            if (imageID not in images_all):
                images_all.append(imageID)
                count = count + 1

# Finding the semantically similar keywords of a subset using the
# markov chain

@app.route('/get_markov_keywords/<s>')
def get_markov_keywords(s):
    markovChain = db.markovChain
    semantic_keywords = []
    res = markovChain.find_one({"fromState": s})
    if res:
        #finding probabilities in decresing order
        max_prob_res = markovChain.find({"fromState": s}).sort("prob",-1)
        for doc in max_prob_res:
            prob = doc['prob']
            toState = doc['toState']
            semantic_keywords.append(toState)
        return semantic_keywords
    else:
        return None

# Function called when user selects an image; Updation of Markov chain.

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

    return ("Image ID is:"+imageID+" Tags: "+keywords)

# Function called when user deselects an image

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