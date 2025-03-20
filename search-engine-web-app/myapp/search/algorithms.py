from collections import defaultdict
from array import array
import math
import numpy as np  
from nltk.tokenize import word_tokenize
from nltk.stem import PorterStemmer
from nltk.corpus import stopwords
import collections
from numpy import linalg as la



def create_index_tfidf(corpus_dict):

    num_tweets = len(corpus_dict)
    index = defaultdict(list)
    tf = defaultdict(list)  # term frequencies of terms in tweets
    df = defaultdict(int)   # tweet frequencies of terms in the corpus
    idf = defaultdict(float)

    for tweet_id, tweet_data in corpus_dict.items():
        content = tweet_data['content']
        if isinstance(content, str):  # Only splitting if content is a string
            terms = content.split()
        else:
            terms = []  # Handling NaN content as an empty list

        current_tweet_index = defaultdict(lambda: [tweet_id, array('I')])  # Initialize tweet-specific index

        # Process each term and its position
        for position, term in enumerate(terms):
            current_tweet_index[term][1].append(position)

        # Normalizing term frequencies
        norm = math.sqrt(sum(len(info[1]) ** 2 for info in current_tweet_index.values()))  # Direct norm calculation

        # Calculating the tf(dividing the term frequency by the above computed norm) and df weights
        for term, info in current_tweet_index.items():
            # Appending the tf for current term (tf = term frequency in current doc/norm)
            tf[term].append(np.round((len(info[1])) / norm, 4))
            # Incrementing the document frequency of current term (number of documents containing the current term)
            df[term] += 1 # increment DF for current term

        # Merge the current tweet index with the main index
        for term, info in current_tweet_index.items():
            index[term].append(info)

    # Computing IDF
    log_num_tweets = math.log(float(num_tweets))  # Precomputing log(num_tweets)
    for term, doc_freq in df.items():
        idf[term] = np.round(log_num_tweets - math.log(doc_freq), 4)  # Calculate and round idf in one line

    return index, tf, df, idf


# Function to preprecess the query
def query_normalizer(line):

    #tokenise
    tokens = word_tokenize(line)

    stop_words = set(stopwords.words("english"))
    stemmer = PorterStemmer()
    # Cleaning: Remove stopwords, punctuation, non-alphanumeric, URLs, hashtags, and stemming
    relevant_tokens = [
        stemmer.stem(token.lower()) for token in tokens
        if token.isalnum() and not token.startswith(("http", "www"))
        and token.lower() not in stop_words and len(token) > 2
    ]
    return relevant_tokens


# Search function to get all the documents that satisfy the information needs
def search_tf_idf(query, index, idf, tf):
    query = query_normalizer(query)
    docs = None
    # print('Normalized query:', query)
    for term in query:
        try:
            # store in term_docs the ids of the docs that contain "term"
            term_docs = {posting[0] for posting in index[term]}

            # Initializing with the documents for the first term and intersection with the rest
            docs = term_docs if docs is None else docs & term_docs
        except:
            # If any term is not in the index, returning an empty list immediately since no doc can contain all terms
            return []

    docs = list(docs) if docs else []
    #print(len(docs))

    # Ranking the documents that contain all terms in the query
    ranked_docs = rank_documents(query, docs, index, idf, tf)
    return ranked_docs


# Ranking function
def rank_documents(query, docs, index, idf, tf):  # docs are tweets in our case

  # Declaring dictionary with key-value pair (k,[0]*len(terms))
  doc_vectors = defaultdict(lambda: [0] * len(query))
  query_vector = [0] * len(query)

  # computing the norm for the query tf
  query_terms_count = collections.Counter(query)  # get the frequency of each term in the query in a dictionary
  query_norm = la.norm(list(query_terms_count.values()))

  for termIndex, term in enumerate(query):  #termIndex is the index of the term in the query
    # if term not in index:       # already checked in search function
    #   continue

    ## Compute tf*idf (normalize TF as done with documents) for the terms in query
    query_vector[termIndex] = (query_terms_count[term] / query_norm) * idf[term]

    # Generate doc_vectors for matching docs
    for doc_index, (doc, postings) in enumerate(index[term]):
      if doc in docs:
        doc_vectors[doc][termIndex] = tf[term][doc_index] * idf[term]

  # Calculating the score of each doc
  # Computing the cosine similarity between queyVector and each docVector (using np.dot)
  doc_scores = [[np.dot(curDocVec, query_vector), doc] for doc, curDocVec in doc_vectors.items()]
  doc_scores.sort(reverse=True)
  # print(doc_scores)
  result_docs = [x[1] for x in doc_scores]

  if len(result_docs) == 0:
      print("No results found, try again")
      #query = input()
      #docs = search_tf_idf(query, index)
  #print ('\n'.join(result_docs), '\n')
  else:
      return result_docs


def search_in_corpus(corpus_dict, query):
    # 1. create create_tfidf_index    
    index, tf, df, idf = create_index_tfidf(corpus_dict)

    # 2. apply ranking
    ranked_docs = search_tf_idf(query, index, idf, tf)

    return ranked_docs
