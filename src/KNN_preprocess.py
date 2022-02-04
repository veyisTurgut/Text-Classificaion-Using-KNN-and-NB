import os
import string
import threading
import math, json

FILE_NAMES = []  # this list holds the names of the reuter files.
STOPWORDS = []  # this list holds the stopwords
# this dictionary holds the values returned from extractBody function which is executed parallelly by threads.
RETURN_VALUES_OF_THREADS = {}
TOP_TOPICS = []


def getFileNames():
    """
    This function traverses reuters21578 folder and appends names of sgm files to global FILE_NAMES list.
    """
    for file in os.listdir(os.getcwd()+"/reuters21578"):
        if file.endswith(".sgm"):
            FILE_NAMES.append(os.path.join("./reuters21578", file))


def getStopwords():
    """
    This function reads stopwords.txt and stores those stopwords in global STOPWORDS list.
    """
    f = open(os.getcwd()+"/stopwords.txt", "r")
    for line in f.readlines():
        STOPWORDS.append(line.strip())
    f.close()


def preprocessArticle(title, body):
    # merge title and body of the article
    BODY = title + " " + body
    # case-folding : lower every character in the article
    BODY = BODY.lower()
    # \n removal : remove newline characters from article
    BODY = BODY.replace("\n", " ")
    # stopword removal : remove stopwords from article
    for stopword in STOPWORDS:
        BODY = BODY.replace(' '+stopword+' ', ' ')
    # punctuation removal : remove punctuations by converting them to space characters.
    BODY = BODY.translate(BODY.maketrans(
        '', '', string.punctuation)).split(" ")
    # stopword removal (again): remove stopwords, numbers and empty strings from article
    BODY = [elem for elem in BODY if not (
        elem in STOPWORDS or elem.isnumeric() or elem == '')]
    #BODY = [elem for elem in BODY if not (elem in STOPWORDS or elem.isnumeric() or elem == '')]
    return BODY


def findTopics(file_name):
    """
    This function traverses a file and extracts the topics. Finally returns a dictionary where keys are topics and values are 
    corresponding occurrences bu manipulating global variable RETURN_VALUES_OF_THREADS.
    """
    with open(file_name, "rb") as f:
        topics = []
        contents = f.read().decode("latin-1")  # read smg file in latin-1 encoding
        while len(contents) > 0:  # read article by article
            # an article is surrounded with <REUTERS> tags.
            article = contents[contents.find(
                "<REUTERS"):contents.find("/REUTERS>")+9]
            # TOPICS section is surrounded with <TOPICS> tags.
            topics_of_the_article = article[article.find(
                "<TOPICS>")+8:article.find("</TOPICS>")]
            while len(topics_of_the_article) > 0:  # read topic by topic
                topic = topics_of_the_article[topics_of_the_article.find(
                    "<D>") + 3:topics_of_the_article.find("</D>")]
                topics.append(topic)
                topics_of_the_article = topics_of_the_article[topics_of_the_article.find(
                    "</D>")+4:]
            # move on to next article
            contents = contents[contents.find("/REUTERS>") + 9:]
        top_topics = {topic: topics.count(topic) for topic in set(topics)}
    RETURN_VALUES_OF_THREADS[file_name] = top_topics


def invertArticle(ID, TEXT):
    """
    This function returns an inverted index of an article.
    It takes the ID and TEXT part of the article and creates the inverted index.
    Example return value: {"term_1": {ID: [i1, i2, i3, ...]}, "term_2": {ID. [i1, i2, i3, ...]},
                            "term_3": {ID: [i1, i2, i3, ...]}, "term_4": {ID: [i1, i2, i3, ...]},..}
    """
    posting_list = {}
    for idx in range(len(TEXT)):
        current_word = TEXT[idx]
        # for every word in article
        if current_word == '':
            continue
        if current_word not in posting_list:
            # if this word did not already in the posting list, insert it with its location.
            posting_list[current_word] = {ID: [idx]}
        else:
            # if this word were already in the posting list, append new location to location list
            posting_list[current_word][ID].append(idx)
    return posting_list


def secondIndexBuilder(BODY):
    """
    Example BODY content: ['term1', 'term2', 'term3', 'term1', ...]

    Example return value:{'term1' : TF1, 'term2' : TF2, 'term3' : TF3, ...}
    """
    result = {term: 1 + math.log(BODY.count(term), 10) for term in set(BODY) if term != ''}
    return result


def merge(postings):
    """
    This function merges the inverted indexes of articles from a file. 
    For every smg sile, this function is called at the end of the "preprocess()" function.

    Example postings content:  {"term_1": {ID: [i1, i2, i3, ...]}, "term_2": {ID. [i1, i2, i3, ...]},
                            "term_3": {ID: [i1, i2, i3, ...]}, "term_4": {ID: [i1, i2, i3, ...]},..}

    Example return value: {"term_1": {ID1: [i1, i2, i3, ...], ID2: [i1, i2, i3, ...], ID999: [i1, i2, i3, ...]]},
                            "term_2": {ID13: [i1, i2, i3, ...], ID2242: [i1, i2, i3, ...], ID10919: [i1, i2, i3, ...]]},
                            "term_3":{ID241: [i1, i2, i3, ...], ID1221: [i1, i2, i3, ...], ID14999: [i1, i2, i3, ...]]},, ...}
    """
    big_posting = {} # this is the return value.
    #print(postings)
    for posting in postings: 
        # posting = "term_1": {ID: [i1, i2, i3, ...]}
        for key, val in posting.items(): 
            # key =  term_1
            # val: {ID: [i1, i2, i3, ...]}
            if key not in big_posting: # if key was not in the list previously, create it
                big_posting[key] = val
            else: # if key is already in the list, append new id next to it.
                for key_,val_ in val.items():
                    big_posting[key][key_] = val_
    return big_posting

def preprocess(file_name):
    """
    This function preprocess the reuters_xx.smg file.
    It reads the file article by article and stores the inverted index of each article in the "postings" variable.
    Then it calls the "merge()" function stores the returned value in global RETURN_VALUES_OF_THREADS variable.
    """
    with open(file_name, "rb") as f:
        contents = f.read().decode("latin-1")  # read smg file in latin-1 encoding
        postings = []
        doc_index = {"training":{}, "test":{}}
        while len(contents) > 0:  # read article by article
            # an article is surrounded with <REUTERS> tags.
            article = contents[contents.find(
                "<REUTERS"):contents.find("/REUTERS>")+9]
            if 'TOPICS="NO"' == article[9:20]:
                contents = contents[contents.find("/REUTERS>") + 9:] # move on to next article
                continue
            # find location of NEWID in the article
            new_id_idx = article.find('NEWID=')
            if new_id_idx > -1:  # if found assign it to NEWID variable
                new_id = int(article[new_id_idx+7:article.find('>')-1])
            else:  # if not found, move on to next article
                contents = contents[contents.find("/REUTERS>") + 9:]
                continue
            # title is surrounded with <TITLE> tags. Find its location
            title_idx = article.find("<TITLE>")
            if title_idx > -1:  # if found assign it to TITLE variable
                title = article[title_idx+7:article.find("</TITLE>")]
            else:  # if not found, assume its empty
                title = ""
            # body is surrounded with <BODY> tags. Find its location
            body_idx = article.find("<BODY>")
            if body_idx > -1:  # if found assign it to BODY variable
                body = article[body_idx+6:article.find("</BODY>")]
            else:  # if not found, assume its empty
                body = ""
            body = preprocessArticle(title,body)

            #### TOPICS
            topics_arr = []
            topics_str = article[article.find("<TOPICS>")+8:article.find("</TOPICS>")] # TOPICS section is surrounded with <TOPICS> tags.
            for topic in TOP_TOPICS:
                if topic in topics_str:
                    topics_arr.append(topic)
            ## NOTE :I realized that some of the articles do not have topics even though they say TOPICS="YES". Liars! :)
            if topics_arr == []:
                contents = contents[contents.find("/REUTERS>") + 9:] # move on to next article
                continue

            #### TRAIN-TEST SPLIT
            if 'LEWISSPLIT="TRAIN"' in article[15:55]:
                second_index = secondIndexBuilder(body)
                for i,topic in enumerate(topics_arr):                    
                    doc_index["training"][str(new_id)+"_"+str(i)] = {"topic":topic,"term-freqs": second_index}
                    postings.append(invertArticle(str(new_id)+"_"+str(i), body))
            if 'LEWISSPLIT="TEST"' in article[15:55]:
                doc_index["test"][new_id] = {"topics":topics_arr,"body": body}

            # move on to next article
            contents = contents[contents.find("/REUTERS>") + 9:]

    # store return value of this function in a global variable
    RETURN_VALUES_OF_THREADS[file_name] = [merge(postings), doc_index]


if __name__ == "__main__":
    """

    """
    getFileNames()  # store filenames in the global variable
    getStopwords()  # store stopwords in the global variable
    # LEARN TOP TOPICS
    threads = []
    for file in FILE_NAMES:
        # create threads for preprocessing each file
        extract_body_thread = threading.Thread(target=findTopics, args=(file,))
        threads.append(extract_body_thread)
        extract_body_thread.start()

    for thread in threads:
        # wait for threads to finish
        thread.join()
    empty = {}
    for filename, topics in RETURN_VALUES_OF_THREADS.items():
        empty = {k: topics.get(k, 0) + empty.get(k, 0)
                 for k in set(topics) | set(empty)}
    TOP_TOPICS = sorted(empty, key=empty.get, reverse=True)[:10]
    RETURN_VALUES_OF_THREADS.clear()

    for file in FILE_NAMES:
        # create threads for preprocessing each file
        extract_body_thread = threading.Thread(target=preprocess, args=(file,))
        threads.append(extract_body_thread)
        extract_body_thread.start()

    for thread in threads:
        # wait for threads to finish
        thread.join()

    biggest_posting = {}
    document_frequencies = {"training":{}, "test":{}}
    for filename in sorted(RETURN_VALUES_OF_THREADS.keys()):
        # append inverted indexes starting from first file, so that final result can be sorted automatically.
        posting_list = RETURN_VALUES_OF_THREADS[filename][0]
        document_frequencies["training"].update(RETURN_VALUES_OF_THREADS[filename][1]["training"])
        document_frequencies["test"].update(RETURN_VALUES_OF_THREADS[filename][1]["test"])
        for key, val in posting_list.items():
            ## key: term
            ## val: {ID1: [id1, id2, id3, ...]}
            if key not in biggest_posting:
                biggest_posting[key] = val
            else:
                for id,idxs in val.items():
                    ## id: ID1
                    ## idxs = [id1, id2, id3, ...]
                    biggest_posting[key][id] = idxs
    
    # write index to file in json format
    """ #for calculating document count for report
    print(len(biggest_posting))
    print(len(document_frequencies["training"]))
    print(len(set([x[:-2] if '_' in x else x for x in document_frequencies["training"]])))
    print(len(document_frequencies["test"]))
    """
    f1 = open(os.getcwd()+"/indexes/KNN_inverted_index.json", "w")
    json.dump(biggest_posting, f1)
    f2 = open(os.getcwd()+"/indexes/KNN_document_frequency_index.json","w")
    json.dump(document_frequencies["training"], f2)
    f3 = open(os.getcwd()+"/input/KNN_preprocessed_test_data.json","w")
    json.dump(document_frequencies["test"], f3)
