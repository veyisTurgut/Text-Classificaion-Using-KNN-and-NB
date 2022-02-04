import json, csv, math, os


def calculateTermFrequencyOfTheQuery(query: list) -> dict:
    """
    Calculates the term frequency of the input query.
    Example term: wordx
    Example query: [word1, word2, word3, word1, ...]
    Formula: 1 + log_10(document.count(term))

    Example return value: {'term1': TF1, 'term2': TF2, 'term3': TF3}
    """
    return {term: 1 + math.log(query.count(term), 10) for term in query}

def calculateInverseDocumentFrequency(posting_lists: dict) -> dict:
    """
    Calculates the inverse document frequency of the query terms.
    Formula: log_10(N/len(documents that contain term))

    Example posting_lists: {term1: {ID1: [i1, i2, i3, ...], ID2: [i1, i2, i3, ...], ID999: [i1, i2, i3, ...]},
                        term2: {ID1985: [i1, i2, i3, ...], ID2204: [i1, i2, i3, ...], ID9929: [i1, i2, i3, ...]}, ...}

    Example return value: {'term1': IDF1, 'term2': IDF2, 'term3': IDF3, ...}
    """
    return {term: math.log((21578+1)/len(posting_list), 10) if len(posting_list) > 0 else 0 for term, posting_list in posting_lists.items()}

def calculateTfIdfScoreForDocuments(TF_of_documents: dict, IDF_of_document_terms: dict) -> dict:
    """
    Calculates the TF-IDF score of a document.
    Formula: tf[term, document] * idf[term] for each term

    Example TF_of_documents: {"DOC1": {"term1": TF1, "term2": TF2, ...}, "DOC2": {"term1": TF1, "term2": TF2, ...}, ...}
    Example IDF_of_documents: {"term1": IDF1, "term2": IDF2, "term3": IDF3, "term4": IDF4, ...}

    Example return value: {DOC1: {'term1': TF-IDF1, 'term2': TF-IDF2, ...}, DOC6114: {'term1': TF-IDF1, ...}, ...}
    """
    return{doc:{term:TF*IDF_of_document_terms[term] for term, TF in TF_values.items()} for doc,TF_values in TF_of_documents.items()}

def calculateCosineScore(query: dict, document: dict) -> float:
    """
    Calculates cosine similarity score of the query and a document.
    Formula: sum(query[i]*document[i] for each i) / (sqrt( sum(query[i]^2 for each i) * sum(document[j]^2 for each j))) 
    """
    return sum( query[term]*document.get(term,0) for term in query) / math.sqrt(sum(query[term]**2 for term in query) * sum(document[term]**2 for term in document))

def freeTextSearch(query_terms, posting_lists: dict, related_docs: dict, document_terms_postings: dict, DOCUMENT_INDEX: dict) -> list:

    """
    Performs free text search on the index file.
    Steps:
    - find tf values
        - find tf values of query by calling "calculateTermFrequencyOfTheQuery" function above
        - tf values are already in the (DOCUMENT_INDEX parameter)[document_frequency_index.json file] for documents, no need to calculate
    - find idf values
        - find idf values of the query terms
        - find idf valuesof the related document terms
    - find tf-idf for each doc and the query
        - find tf-idf values of the query
        - find tf-idf values of documents
    - calculate cosine similarity of the query and documents
    - sort with respect to cosine similarities in descending order
    """
    # TF: find tf values of query
    TF_of_query = calculateTermFrequencyOfTheQuery(query_terms)
    # IDF: find idf values of query terms and related document terms
    IDF_of_query = calculateInverseDocumentFrequency(posting_lists)
    IDF_of_document_terms = calculateInverseDocumentFrequency(document_terms_postings)
    # TF-IDF: find tf-idf values of the query and the documents
    TF_IDF_score_of_query = {term: TF_of_query[term] * IDF_of_query[term] for term in TF_of_query.keys()}
    TF_IDF_scores_of_documents = calculateTfIdfScoreForDocuments(related_docs, IDF_of_document_terms)
    # calculate cosine similarity of the query and documents
    result = {doc_id: calculateCosineScore(TF_IDF_score_of_query, TF_IDF_scores_of_a_document)
              for doc_id, TF_IDF_scores_of_a_document in TF_IDF_scores_of_documents.items()}
    # sort documents with respect to cosine similarities in decreasing order
    #print(IDF_of_query)
    #print(TF_IDF_score_of_query)
    return sorted(result.items(), key=lambda x: x[1], reverse=True)

def readIndexFileForQuery(query_terms: list, INVERTED_INDEX: dict, DOCUMENT_INDEX: dict) -> dict:
    """
    Reads the input query and INDEX file, then returns posting lists of query_terms.
    """
    query_postings = {term: INVERTED_INDEX.get(term,{}) for term in query_terms}
    related_docs = {doc_id: DOCUMENT_INDEX[doc_id].get("term-freqs") for doc_id in set([item for sublist in [list(x.keys()) for x in list(query_postings.values())] for item in sublist])}
    document_terms_postings = {term: INVERTED_INDEX.get(term,{}) for term in set([item for sublist in [x.keys() for x in related_docs.values()] for item in sublist])}
    return query_postings, document_terms_postings,related_docs

def search(query_terms: list, INVERTED_INDEX: dict, DOCUMENT_INDEX: dict):
    """
    Decides the type of the query and calls corresponding functions.
    """
    query_postings, document_terms_postings,related_docs = readIndexFileForQuery(list(set(query_terms)), INVERTED_INDEX, DOCUMENT_INDEX)
    result = freeTextSearch(query_terms, query_postings,related_docs, document_terms_postings, DOCUMENT_INDEX)
    return result

if __name__ == "__main__":
    # first load index_files to memory
    inverted_index_file = open(os.getcwd()+'/indexes/KNN_inverted_index.json',)
    INVERTED_INDEX = json.load(inverted_index_file)
    inverted_index_file.close()
    document_index_file = open(os.getcwd()+'/indexes/KNN_document_frequency_index.json',)
    DOCUMENT_INDEX = json.load(document_index_file)
    document_index_file.close()
    test_data_file = open(os.getcwd()+'/input/KNN_preprocessed_test_data.json',)
    TEST_DATA = json.load(test_data_file)
    test_data_file.close()

    Y_true = {}
    Y_pred = {"1":{}, "3":{}, "5":{}, "7":{}}
    MULTILABEL_THRESHOLD_MULTIPLIER = 2
    for doc_index,data in TEST_DATA.items():
        Y_true[doc_index] = data["topics"]
        article = data["body"]
        result = search(article,INVERTED_INDEX,DOCUMENT_INDEX)
        for K in [1,3,5,7]:
            top_k_results = result[:K]
            closest_topics = [DOCUMENT_INDEX.get(point[0]).get('topic') for point in top_k_results]
            topic_probs = {topic: closest_topics.count(topic)/len(closest_topics) for topic in set(closest_topics)}
            sorted_list = sorted(topic_probs,key=topic_probs.get,reverse=True)
            current_pred = []
            for i in range(len(sorted_list)):
                if topic_probs[sorted_list[i]] > 0.4:    
                    current_pred.append(sorted_list[i])
            if(len(current_pred) == 0):
                for i in range(len(sorted_list)):
                    if topic_probs[sorted_list[i]] > 0.32:    
                        current_pred.append(sorted_list[i])
            Y_pred[str(K)][doc_index] = current_pred
        
    TOPICS = ['earn', 'acq', 'money-fx', 'crude', 'grain', 'trade', 'interest', 'wheat', 'ship', 'corn']
    for k in [1,3,5,7]:
        with open(os.getcwd()+'/output/KNN_pred_k_'+str(k)+'.csv', 'w') as test_file:
            header = ['doc_id']+ TOPICS
            file_writer = csv.DictWriter(test_file, fieldnames = header)
            file_writer.writeheader()
            for doc_id,topics in Y_pred[str(k)].items():
                file_writer.writerow({"doc_id":doc_id, **{topic: 1 if topic in topics else 0 for topic in TOPICS }})

    with open(os.getcwd()+'/output/KNN_true.csv', 'w') as test_file:
        header = ['doc_id', 'earn', 'acq', 'money-fx', 'crude', 'grain', 'trade', 'interest', 'wheat', 'ship', 'corn']
        file_writer = csv.DictWriter(test_file, fieldnames = header)
        file_writer.writeheader()
        for doc_id,topics in Y_true.items():
            file_writer.writerow({"doc_id":doc_id, **{topic: 1 if topic in topics else 0 for topic in TOPICS }})