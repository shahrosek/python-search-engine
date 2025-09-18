# Python Search Engine from Scratch

This repository contains the source code for a simple search engine built from the ground up in Python. The project was completed as part of my Information Retrieval course and is split into two main components: an **Indexer** and a **Ranker**.

## 🎯 Objective
To implement the core components of a search engine, demonstrating an understanding of text processing, index construction, and statistical ranking models used to score and retrieve relevant documents.

## ⚙️ Components

### 1. The Indexer
The `Indexer/` directory contains the scripts responsible for processing a raw document collection and building an efficient inverted index.

* **Text Processing Pipeline**:
    1.  Parses and extracts clean text from HTML files.
    2.  Tokenizes text using regular expressions.
    3.  Converts all tokens to lowercase.
    4.  Removes common stopwords from a provided list.
    5.  Applies the **Porter Stemmer** to reduce words to their root form.
* **Inverted Index Construction**:
    * Generates `docids.txt` and `termids.txt` to map documents and terms to unique integers.
    * Creates a `term_index.txt` file containing the complete inverted lists.
    * Implements **Delta Encoding** on DOCIDs and term positions within the inverted lists to ensure the index is compact and efficient.

### 2. The Ranker
The `Ranker/` directory contains the `solution.py` script, which uses the generated index to score and rank documents for a given set of queries (`topics.xml`).

* **Query Processing**: Applies the same tokenization and stemming pipeline to user queries to ensure consistency with the indexed documents.
* **Scoring Functions Implemented**:
    * `--score TF`: Vector Space Model using **Okapi TF** weighting.
    * `--score TF-IDF`: Vector Space Model using **TF-IDF** weighting.
    * `--score BM25`: The probabilistic **Okapi BM25** ranking function.
    * `--score JM`: A **Language Model** approach with **Jelinek-Mercer Smoothing**.

## 📈 Evaluation
The performance of each ranking model was evaluated against a ground-truth dataset (`corpus.qrel`) using the **Graded Average Precision (GAP)** metric. A detailed report comparing the effectiveness of each algorithm is included in the project documentation.

## 🛠️ Tech Stack
* **Language**: `Python`
* **Key Libraries**: `NLTK` (for stemming and stopwords), standard file I/O and data structure libraries.
