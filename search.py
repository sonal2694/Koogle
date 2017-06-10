# Working program
from nltk.corpus import stopwords
from flask import Flask, request, render_template
from pymongo import MongoClient
from collections import Counter
from itertools import repeat, chain
import collections
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
    print(query)
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

    for i in q:
        result = invertedIndex.find_one({"label": i})
        if result:
            for k in result['image']:
                Image = labels.find_one({"LabelName": k})
                if Image is not None:
                    url = images.find_one({"ImageID": Image['ImageID']})
                    out.write(url['Thumbnail300KURL'] + " " + Image['ImageID'] + '\n' )

    out.close()

    arr = []
    c = 0
    f = open(filename, 'r')

    for line in f:
        imageStuff = line.rstrip("\n")
        imageParts = imageStuff.split(" ")
        imageUrl = imageParts[0]

        arr.append(imageParts)


        c = c+1

    return render_template('result.html', text=request.form['query'], data=arr)

if __name__ == "__main__":
    app.run()
