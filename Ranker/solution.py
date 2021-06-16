from nltk.tokenize import RegexpTokenizer
from nltk.stem import porter
from collections import defaultdict
import collections
from collections import Counter
import xml.etree.ElementTree as et
import operator
import codecs
import hashlib
import math
import re
import sys
import csv

stemmer = porter.PorterStemmer()

docs = dict()
topics = dict()
queryTF = {}
queryLength = dict()
docLength = dict()
cachedStopWords = []
vectorspace = {}
termDF = dict()

def loadStopwords(filename):
    with open(filename, "r") as f:
        for word in f:
            word = word.split('\n')
            cachedStopWords.append(word[0])
    f.close()

def getTermID(term):
    with open("termids.txt", "r") as reader:
        id = 0
        name = ""
        for row in csv.reader(reader, delimiter='\t'):
            id = int(row[0])
            name = row[1]
            if name != term:
                id = 0
            else:
                break
    reader.close()
    return id

def getDocID(docname):
    with open("docids.txt", "r") as reader:
        id = 0
        name = ""
        for row in csv.reader(reader, delimiter='\t'):
            id = int(row[0])
            name = row[1]

            if name != docname:
                id = 0
            else:
                break
    reader.close()
    return id


def getDocNames():
    with open("docids.txt", "r") as reader:
        for row in csv.reader(reader, delimiter='\t'):
            docs[int(row[0])] = row[1]

    reader.close()

def extractQueryTopics():
    tree = et.parse('topics.xml')
    root = tree.getroot()

    for topic in root.findall('topic'):
        number = topic.get('number')
        query = topic.find('query').text
        topics[query] = int(number)


def getDocLength():
    with open("docInfo.txt", "r") as reader:
        sum = 0
        for row in csv.reader(reader, delimiter='\t'):
            docLength[int(row[0])] = int(row[2])
            sum = sum + int(row[2])
    reader.close()
    return sum/len(docLength)

def computeDOCTF():
    avgDocLength = getDocLength()
    docTFwriter = open("docTF.txt", "w")

    with open("termPositions.txt", "r") as reader:
        termid = 0
        docid = 0
        counter = 0
        for row in csv.reader(reader, delimiter='\t'):
            docid = int(row[0])
            termid = int(row[1])
            counter = 0
            if termid is not None:
                counter = len(row[2:])
                tfCount = counter
                docTFwriter.write(str(docid)+"\t"+str(termid)+"\t"+str(tfCount)+"\n")

    reader.close()
    docTFwriter.close()

def readDocTF():
    # global vectorspace
    with open("docTF.txt", "r") as reader:
        docid = 0
        termid = 0
        tf = 0
        for row in csv.reader(reader, delimiter='\t'):
            docid = int(row[0])
            termid = int(row[1])
            tf = int(row[2])
            if docid not in vectorspace:
                vectorspace[docid] = {}
            vectorspace[docid][termid] = tf
    reader.close()


def getTermDF():
    with open("term_index.txt", "r") as reader:
        termid = 0
        for row in csv.reader(reader, delimiter='\t'):
            termid = int(row[0])
            termDF[termid] = int(row[2])
    reader.close()

def processQuery(query, number):
    count = 0
    termID = 0
    words = [re.sub(r"[^a-z0-9]+", '', k) for k in query.split()]
    words = [word.lower() for word in words]
    new_words = [word for word in words if word not in cachedStopWords]
    tokens = map(lambda x: stemmer.stem(x), new_words)
    queryTF[number] ={}
    for token in tokens:
        termID = getTermID(token)
        if termID is not None:
            # tid = int(termID)
            count = count + 1
            if termID not in queryTF[number]:
                queryTF[number][termID] = 1
            else:
                queryTF[number][termID] = queryTF[number][termID] + 1

    return count

def getQueryLengths():
    sum = 0
    for query, number in topics.items():
        queryLen = processQuery(query, number)
        queryLength[number] = queryLen
        sum = sum + queryLen

    return sum/len(topics)

def rankBM25():
    bm25writer = open("BM25Ranked.txt", "w")
    print("Calculcating Query Lengths...")
    querylen = getQueryLengths()
    print("\nReading Document Lengths ...")
    avgDocLength = getDocLength()

    k1 = 1.2
    k2 = 220.0
    b = 0.75
    doclen = len(docs)


    for num, queryTermDic in queryTF.items():
        print("Query: %s" % num)
        print("Scoring Documents ...")
        scores = dict()
        sorted_dict = dict()

        for docid, docTermDic2 in vectorspace.items():
            score = 0.0

            for termid, tf in queryTermDic.items():
                t1 = 0.0
                t2 = 0.0
                t3 = 0.0

                m = termDF.get(termid)
                dLen = docLength.get(docid)
                docTF = docTermDic2.get(termid)

                if docTF is None:
                    continue

                k = k1 * ( (1-b) + (b * (dLen/avgDocLength) ) )

                t1 = (doclen + 0.5) / (m + 0.5)
                t2 = ( ( (1 + k1) * docTF) / ( k + docTF) )
                t3 = ( ( (1 + k2) * tf) / (k2 + tf) )

                score = score + ( math.log2(t1) * t2 * t3)

            scores[score] = docid
            sorted_x = sorted(scores.items(), key=operator.itemgetter(0), reverse=True)
            sorted_dict = collections.OrderedDict(sorted_x)

        j=0
        for s,doc in sorted_dict.items():
            j = j+1
            docname = docs.get(doc)
            bm25writer.write(str(num)+" 0 "+str(docname)+" " +
                             str(j)+" "+str(s)+" run 1"+" \n")

    bm25writer.close()

def rankDS():
    with open("term_index.txt", "r") as reader:
        termId = 0
        collecFreq = dict()
        for row in csv.reader(reader, delimiter ='\t'):
            termId = int(row[0])
            collecFreq[termId] = int(row[1])
    reader.close()

    dswriter = open("DSRanked.txt", "w")
    corpusLength = getDocLength() * len(docs)
    mu = getDocLength()
    readDocTF()
    getQueryLengths()

    for num, queryTermDic in queryTF.items():
        print("Query: %d"%num)
        print("Scoring Documents ...")

        alpha = 0.0
        reverseAlpha = 0.0
        scores = dict()
        sorted_dict = dict()
        for docid, docTermDic2 in vectorspace.items():
            score = 1.0
            for termid, tf in queryTermDic.items():
                N = docLength.get(docid)

                alpha = math.log2(N) - math.log2((N+mu))
                reverseAlpha = math.log2(mu) - math.log2((N+mu))

                param1 = docTermDic2.get(termid)
                param2 = collecFreq.get(termid)

                if param1 is None:
                    continue
                if param2 is None:
                    continue

                result = ((alpha + (math.log2(param1) - math.log2(N))) + (reverseAlpha + (math.log2(param2) - math.log2(corpusLength))))
                score = score * result

            scores[score] = docid
            sorted_x = sorted(scores.items(), key=operator.itemgetter(0), reverse=True)
            sorted_dict = collections.OrderedDict(sorted_x)

        print("Writing Scores: ")

        j=0
        for s, doc in sorted_dict.items():
            j = j+1
            docname = docs.get(doc)
            dswriter.write(str(num)+" 0 "+str(docname)+" "+str(j)+" "+str(s)+" "+" run1"+"\n")

    dswriter.close()

qrel = {}
def readQrel():
    with open("relevance judgements.qrel", "r") as reader:
        docid = 0
        topic = 0
        grade = 0
        for row in csv.reader(reader, delimiter=' '):
            topic = int(row[0])
            zer = int(row[1])
            docid = getDocID(row[2])
            grade = int(row[3])

            if topic not in qrel:
                qrel[topic] = {}
            if grade > 0:
                qrel[topic][docid] = 1

    reader.close()

bm25 = dict()
def BM25MAP():
    with open("BM25Ranked.txt", "r") as reader1:
        query = 0
        docid = 0
        rank = 0

        for row in csv.reader(reader1, delimiter=' '):
            query = int(row[0])
            docid = getDocID(row[2])
            rank = int(row[3])

            if query not in bm25:
                bm25[query] = dict()
            bm25[query][docid] = rank

    reader1.close()

    mapBM25 = 0.0
    for t,dict1 in bm25.items():
        avgPrec = 0.0
        relevantDocs = 0
        docCount = 0
        totalRelevantDocs = len(dict1)
        print("Query: %d"%t)
        for d,r in dict1.items():
            docCount = docCount + 1
            if d in qrel.get(t):
                relevantDocs = relevantDocs + 1
                avgPrec = avgPrec + (relevantDocs/docCount)
            # print("P@%d: %d/%d: %.5f"%(docCount, relevantDocs, docCount, (relevantDocs/docCount)))
            if docCount == 5:
                print("P@5: %d/%d: %.5f"%(relevantDocs, docCount, (relevantDocs/docCount)))
            elif docCount == 10:
                print("P@10: %d/%d: %.5f"%(relevantDocs, docCount, (relevantDocs/docCount)))
            elif docCount == 20:
                print("P@20: %d/%d: %.5f"%(relevantDocs, docCount, (relevantDocs/docCount)))
            elif docCount == 30:
                print("P@30: %d/%d: %.5f"%(relevantDocs, docCount, (relevantDocs/docCount)))
        avgPrec = avgPrec / totalRelevantDocs
        print("Average Precision = %.5f"%avgPrec)
        print("Total Relevant Doc = %d"%totalRelevantDocs)
        mapBM25 = mapBM25 + avgPrec
    mapBM25 = mapBM25 / len(bm25)
    print("Mean Average Precision for BM25 = %.5f"%mapBM25)

ds = dict()
def DSMAP():
    with open("DSRanked.txt", "r") as reader1:
        topic = 0
        doc = 0
        r = 0

        for row in csv.reader(reader1, delimiter=' '):
            topic = int(row[0])
            doc = getDocID(row[2])
            r = int(row[3])

            if topic not in ds:
                ds[topic] = dict()
            ds[topic][doc] = r

    reader1.close()

    mapDS = 0.0
    for t1,dict2 in ds.items():
        averagePrec = 0.0
        relevantDoc = 0
        docCounter = 0
        totalRelevantDoc = len(dict2)
        print("Query: %d"%t1)
        for d1,r1 in dict2.items():
            docCounter = docCounter + 1
            if d1 in qrel.get(t1):
                relevantDoc = relevantDoc + 1
                averagePrec = averagePrec + (relevantDoc/docCounter)
            if docCounter == 5:
                print("P@5: %d/%d: %.5f"%(relevantDoc, docCounter, (relevantDoc/docCounter)))
            elif docCounter == 10:
                print("P@10: %d/%d: %.5f"%(relevantDoc, docCounter, (relevantDoc/docCounter)))
            elif docCounter == 20:
                print("P@20: %d/%d: %.5f"%(relevantDoc, docCounter, (relevantDoc/docCounter)))
            elif docCounter == 30:
                print("P@30: %d/%d: %.5f"%(relevantDoc, docCounter, (relevantDoc/docCounter)))
        averagePrec = averagePrec / totalRelevantDoc
        print("Average Precision = %.5f"%averagePrec)
        print("Total Relevant Doc = %d"%totalRelevantDoc)
        mapDS = mapDS + averagePrec
    mapDS = mapDS / len(ds)
    print("Mean Average Precision for DS = %.5f"%mapDS)


def main(argv):
    if argv[1] == "BM25":
        rankBM25()
        BM25MAP()
    elif argv[1] == "DS":
        rankDS()
        DSMAP()

if __name__ == "__main__":
    getDocNames()
    extractQueryTopics()
    computeDOCTF()

    print("\nReading Document Term frequency ...")
    readDocTF()
    print("\nReading Term Document frequency ...")
    getTermDF()
    readQrel()

    if(len(sys.argv)==3):
        main(sys.argv[1:])
    else:
        print("Usage: script.py --score scoringFunction")
        sys.exit()
