import csv
import sys
from os import listdir
from nltk.stem import porter

stemmer = porter.PorterStemmer()

def readIndex(term, argv):
    termid = 0
    with open("termids.txt", "r") as termReader:
        for row in csv.reader(termReader, delimiter = '\t'):
            if row[1] == term:
                termid = int(row[0])
    termReader.close()

    with open("term_index.txt") as reader:
        for row in csv.reader(reader, delimiter = '\t'):
            if termid == int(row[0]):
                print("Listing for term: %s"%argv[1])
                print("TERMID: %d"%termid)
                print("Number of documents containing term: %d"%int(row[2]))
                print("Term frequency in corpus: %d"%int(row[1]))
    reader.close()

def main(argv):
    term = argv[1]
    stemmed = stemmer.stem(term)
    readIndex(stemmed, argv)


if __name__ == "__main__":
    if(len(sys.argv)==3):
        main(sys.argv[1:])
    else:
        print("Usage: script.py --term term")
        sys.exit()
