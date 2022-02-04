import os
import string
import threading
import csv
import math

FILE_NAMES = [] # this list holds the names of the reuter files.
STOPWORDS = [] # this list holds the stopwords
RETURN_VALUES_OF_THREADS = {} # this dictionary holds the values returned from extractBody function which is executed parallelly by threads.
TOP_TOPICS = []
def getFileNames():
    """
    This function traverses reuters21578 folder and appends names of sgm files to global FILE_NAMES list.
    """
    for file in os.listdir("./reuters21578"):
        if file.endswith(".sgm"):
            FILE_NAMES.append(os.path.join("./reuters21578", file))


def getStopwords():
    """
    This function reads stopwords.txt and stores those stopwords in global STOPWORDS list.
    """
    f = open("./stopwords.txt", "r")
    for line in f.readlines():
        STOPWORDS.append(line.strip())
    f.close()


def secondIndexBuilder(BODY):
    """
    Example BODY content: ['term1', 'term2', 'term3', 'term1', ...]

    Example return value:{'term1' : TF1, 'term2' : TF2, 'term3' : TF3, ...}
    """
    result = {term:1+ math.log(BODY.count(term),10)  for term in set(BODY) if term != ''}
    return result


def preprocessArticle(title,body):
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
    BODY = ";".join([elem for elem in BODY if not (elem in STOPWORDS or elem.isnumeric() or elem == '')])
    return BODY

def findTopics(file_name):
    """
    This function traverses a file and extracts the topics. Finally returns a dictionary where keys are topics and values are 
    corresponding occurrences bu manipulating global variable RETURN_VALUES_OF_THREADS.
    """
    with open(file_name, "rb") as f:
        topics=[]
        contents = f.read().decode("latin-1") # read smg file in latin-1 encoding
        while len(contents) > 0: # read article by article
            article = contents[contents.find("<REUTERS"):contents.find("/REUTERS>")+9] # an article is surrounded with <REUTERS> tags.
            topics_of_the_article = article[article.find("<TOPICS>")+8:article.find("</TOPICS>")] # TOPICS section is surrounded with <TOPICS> tags.
            while len(topics_of_the_article) > 0: # read topic by topic
                topic = topics_of_the_article[topics_of_the_article.find("<D>") + 3 :topics_of_the_article.find("</D>")]
                topics.append(topic)
                topics_of_the_article = topics_of_the_article[topics_of_the_article.find("</D>")+4:]
            contents = contents[contents.find("/REUTERS>") + 9:] # move on to next article
        top_topics = {topic:topics.count(topic) for topic in set(topics)}
    RETURN_VALUES_OF_THREADS[file_name] = top_topics

def indexer(file_name):
    """
    This function creates an index from the reut2_xxx.smg file.
    It reads the file article by article and stores the inverted index of each article in the "postings" variable.
    Then it calls the "merge()" function stores the returned value in global RETURN_VALUES_OF_THREADS variable.
    """

    training_set = []
    test_set = []
    with open(file_name, "rb") as f:
        contents = f.read().decode("latin-1") # read smg file in latin-1 encoding
        while len(contents) > 0: # read article by article
            article = contents[contents.find("<REUTERS"):contents.find("/REUTERS>")+9] # an article is surrounded with <REUTERS> tags.
            if 'TOPICS="NO"' == article[5:25]:
                contents = contents[contents.find("/REUTERS>") + 9:] # move on to next article
                continue
            ### INDEX
            new_id_idx = article.find('NEWID=') # find location of NEWID in the article
            if new_id_idx > -1: # if found assign it to NEWID variable
                new_id = int(article[new_id_idx+7:article.find('>')-1])
            else: # if not found, move on to next article
                contents = contents[contents.find("/REUTERS>") + 9:]
                continue
            #### TITLE
            title_idx = article.find("<TITLE>") # title is surrounded with <TITLE> tags. Find its location
            if title_idx > -1: # if found assign it to TITLE variable
                title = article[title_idx+7:article.find("</TITLE>")]
            else: # if not found, assume its empty
                title = ""
            #### BODY
            body_idx = article.find("<BODY>") # body is surrounded with <BODY> tags. Find its location
            if body_idx > -1: # if found assign it to BODY variable
                body = article[body_idx+6:article.find("</BODY>")]
            else: # if not found, assume its empty
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

            if 'LEWISSPLIT="TRAIN"' in article[5:55]:
                training_set.append([new_id,body,";".join(topics_arr)])
            if 'LEWISSPLIT="TEST"' in article[5:55]:
                test_set.append([new_id,body,";".join(topics_arr)])


            contents = contents[contents.find("/REUTERS>") + 9:] # move on to next article
    
    # store return value of this function in a global variable
    RETURN_VALUES_OF_THREADS[file_name] = [training_set, test_set]


if __name__ == "__main__":  
    """
    
    """
    getFileNames() # store filenames in the global variable
    getStopwords() # store stopwords in the global variable
    ### LEARN TOP TOPICS
    threads = []
    for file in FILE_NAMES:
        # create threads for preprocessing each file
        extract_body_thread = threading.Thread(target=findTopics, args=(file,))
        threads.append(extract_body_thread)
        extract_body_thread.start()

    for thread in threads:
        # wait for threads to finish
        thread.join()
    empty={}
    for filename,topics in RETURN_VALUES_OF_THREADS.items():
        empty = {k: topics.get(k, 0) + empty.get(k, 0) for k in set(topics) | set(empty)}
    TOP_TOPICS = sorted(empty, key=empty.get, reverse=True)[:10]
    RETURN_VALUES_OF_THREADS.clear()

    ### PREPROCESS AND INDEX DATASET
    threads = []
    for file in FILE_NAMES:
        # create threads for indexing each file
        extract_body_thread = threading.Thread(target=indexer, args=(file,))
        threads.append(extract_body_thread)
        extract_body_thread.start()

    for thread in threads:
        # wait for threads to finish
        thread.join()

    with open(os.getcwd()+'/input/NB_training.csv', 'w') as test_file:
            ...#clear file
    with open(os.getcwd()+'/input/NB_test.csv', 'w') as test_file:
            ...#clear file
    for filename in sorted(RETURN_VALUES_OF_THREADS.keys()):
        with open(os.getcwd()+'/input/NB_training.csv', 'a') as test_file:
            file_writer = csv.writer(test_file)
            for row in RETURN_VALUES_OF_THREADS[filename][0]:
                file_writer.writerow(row)
        with open(os.getcwd()+'/input/NB_test.csv', 'a') as test_file:
            file_writer = csv.writer(test_file)
            for row in RETURN_VALUES_OF_THREADS[filename][1]:
                file_writer.writerow(row)
        
