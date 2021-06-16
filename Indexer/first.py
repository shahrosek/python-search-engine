import sys
from os import listdir
from os.path import isfile, join, basename
from nltk.tokenize import RegexpTokenizer
from nltk.stem import porter
from collections import defaultdict
from bs4 import BeautifulSoup
import codecs
import hashlib
import string
import re

totalFiles = 0
totalDirectories = 0
cachedStopWords = []
termIds = dict()
termPositions = dict()
docId = 0
tId = 0
totalTerms = 0

stemmer = porter.PorterStemmer()

docIdFile = open("docids.txt", "w")
termIdFile = open("termids.txt", "w")
termPosFile = open("termPositions.txt", "w")
docInfoFile = open("docInfo.txt", "w")


def loadStopwords(filename):
    with open(filename, "r") as f:
        for word in f:
            word = word.split('\n')
            cachedStopWords.append(word[0])
    f.close()


def processFile(file, docIdFile):
    try:
        print("Processing file: " + file)

        global docId
        global tId
        global termIds
        global totalTerms

        docId = docId + 1
        docIdFile.write(str(docId)+"\t" + basename(file) + "\n")

        with codecs.open(file, "r", encoding='utf-8', errors='ignore') as f:
                soup = BeautifulSoup(f, 'html.parser')
                data = soup.find('body')

                if data is None:
                    return

                for script in data(["script", "style"]):
                    script.extract()

                words = data.get_text()
                words = words.lower()
                words = [re.sub(r"[^a-z0-9]+", '', k) for k in words.split()]

                new_words = [
                    word for word in words if word not in cachedStopWords]

                tokens = map(lambda x: stemmer.stem(x), new_words)

                position = 0
                distinctTerms = 0
                positionDict = dict()

                for t in tokens:
                    if t not in termIds and len(t) > 1:
                        tId = tId + 1
                        termIds[t] = tId
                        termIdFile.write(str(tId)+"\t"+t+"\n")

                    if t not in positionDict:
                        positionDict[t] = []
                    position = position + 1
                    positionDict[t].append(position)

                for k, v in positionDict.items():
                    termid = termIds.get(k)
                    if termid is None:
                        continue
                    termPosFile.write(str(docId)+"\t"+str(termid))
                    distinctTerms = distinctTerms + 1

                    for pos in v:
                        termPosFile.write("\t"+str(pos))
                        totalTerms = totalTerms + 1
                    termPosFile.write("\n")

                docInfoFile.write(
                    str(docId)+"\t"+str(distinctTerms)+"\t"+str(totalTerms))
                docInfoFile.write("\n")

        f.close()

    except Exception as e:
        print(e)


def readDirectory(directory, docIdFile):
    try:
        global totalFiles
        global totalDirectories
        files = [f for f in listdir(directory)]
        for f in files[1:]:
            # #FOR DEBUGGING ONLY
            # if totalFiles == 10: #Temporarily, of course. DEBUGGING REASONS
                # break
            file = join(directory,f)
            if isfile(file) == True:
                processFile(file,docIdFile)
                totalFiles = totalFiles + 1
            else:
                totalDirectories = totalDirectories + 1
                readDirectory(file,docIdFile)
    except:
        print("Error while reading the directories")
        sys.exit()


def main(argv):
    try:
        loadStopwords("stoplist.txt")
        print("Directory: " + argv[0])
        readDirectory(argv[0],docIdFile)
        docIdFile.close()
        termIdFile.close()
        docInfoFile.close()
        termPosFile.close()
        print("Total Files: "+str(totalFiles))
        print("Total Directories: "+str(totalDirectories))
    except Exception as e:
        print("Error in main.")
        print(e)


if __name__ == "__main__":
    if(len(sys.argv)==2):
        main(sys.argv[1:])
    else:
        print("Usage: script.py directory")
        sys.exit()
