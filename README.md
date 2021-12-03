# Koogle

The project is an image search engine using a methodology for the retrieval of images which is based on Markov chains and its ability to store the semantics of the present situation in its states. The algorithm called Koogle, creates a Global Markov Chain for keyword relevance and for storing the user semantics, where each state can hold more than one keyword. This project shows how multiple keywords can be included in a single state and how the proposed ranking algorithm produces relevant results in most cases and can be used to give desired images to its targeted users.
The project will run only on a local system.

## Getting Started

### Prerequisites

Install Python 3 if not already installed. To manage software packages for Python, install pip.

```
$ sudo apt-get update
$ sudo apt-get install python3
$ sudo apt-get install -y python3-pip
```

Install the python packages pymongo and nltk. You can install Python packages using:

```
$ pip3 install package_name
```

Install Flask by following the instructions given [here](http://flask.pocoo.org/docs/0.12/installation/).

Install MongoDB by following the instructions given [here](https://docs.mongodb.com/v3.0/tutorial/install-mongodb-on-ubuntu/).

Dataset used in the project can be downloaded from [here](https://github.com/openimages/dataset).

## Running the tests

On the terminal, run mongoDB by typing:

```
$ mongo
```

Create a database called 'dataset'. Import all .csv files into their respective collections. Exit mongoDB.

On the terminal, open the script folder contained in the project folder and run the files by typing:

```
$ python3 createImageAnnotations.py
$ python3 removeDupAnnotations.py
```

Come out of the script folder and run the main file, search.py, by typing:

```
$ python3 search.py
```

The search engine runs on http://127.0.0.1:5000/.

### Input

Type your query in the search box and click on SEARCH. For example,

```
traditional sport
```
You get directed to another page with the results where you can select your desired images.

## Built With

* [Python](https://www.python.org/about/gettingstarted/) - Backend Language
* [Flask](http://flask.pocoo.org/) - The web framework used
* [MongoDB](https://docs.mongodb.com/) - Database Program

## Authors

* [Sonal Singh](https://github.com/sonal2694)
* [Yash Choukse](https://github.com/yash1195)
