
from collections import defaultdict
import codecs
import hashlib
import csv

indexWriter = open("term_index.txt", "w")

def inverter():
    docid = 0
    termid = 0
    with open("termPositions.txt", "r") as reader:
        index = {}
        for row in csv.reader(reader, delimiter = '\t'):
            docid = int(row[0])
            termid = int(row[1])
            if termid not in index:
                index[termid] = {}
            if docid not in index[termid].items():
                index[termid][docid] = []

            for position in row[2:]:
                index[termid][docid].append(int(position))
                sorted(index[termid][docid])

    reader.close()

    docfreq = 0
    collecfreq = 0

    prevDoc = -1
    for tid, dic2 in index.items():
        indexWriter.write(str(tid)+"\t")

        docfreq = len(dic2)
        collecfreq = 0

        for did, positions in dic2.items():
            collecfreq = collecfreq + len(positions)

        indexWriter.write(str(collecfreq)+"\t"+str(docfreq)+"\t")
        prevDoc = -1
        doc = 0

        for docId, Positions in dic2.items():

            if prevDoc == -1:
                doc = docId
                prevDoc = doc
            else:
                doc = docId - prevDoc
                prevDoc = docId

            prevPos  = 0
            firstPos = 0
            for p in Positions:
                if prevPos == 0:
                    prevPos = doc
                    firstPos = p
                else:
                    doc = 0
                    p = p - firstPos
                indexWriter.write(str(doc)+","+str(p)+"\t")
        indexWriter.write("\n")

    indexWriter.close()

if __name__ == "__main__":
    inverter()
