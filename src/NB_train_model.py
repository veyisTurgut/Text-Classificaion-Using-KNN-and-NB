import csv, math, os

TOPIC_COUNTS = {} # {topic1: 433, topic2: 124, ...}
VOCAB_WORD_BASED = {} # {term1: {topic1: 5, topic2: 7}, term2: {topic9: 1, topic5: 2}, ...}
VOCAB_TOPIC_BASED = {} # {topic1: {term1: 5, term2: 7}, topic2: {term1: 1, term2: 2}, ...}
MULTILABEL_THRESHOLD_MULTIPLIER = 5

file = open(os.getcwd()+'/input/NB_training.csv')
numline = len(file.readlines())
file.close()
train_validation_split = numline//5*4

### TRAINING PHASE
# with %80 of the data, prepare a word based vocab, i.e: train model
with open(os.getcwd()+'/input/NB_training.csv') as csvfile:
    csvreader = csv.reader(csvfile, delimiter=',', quotechar='"')
    line_number = 0 
    for row in csvreader:
        if line_number > train_validation_split:
            break
        id = int(row[0])
        words = row[1].split(';')
        topics = row[2].split(';')
        for word in words:
            if word not in VOCAB_WORD_BASED:
                VOCAB_WORD_BASED[word] = {}
                for topic in topics:
                    if topic not in VOCAB_WORD_BASED[word]:
                        VOCAB_WORD_BASED[word][topic] = 0
                    VOCAB_WORD_BASED[word][topic] += 1
            else:
                for topic in topics:
                    if topic not in VOCAB_WORD_BASED[word]:
                        VOCAB_WORD_BASED[word][topic] = 0
                    VOCAB_WORD_BASED[word][topic] += 1
# with %80 of the data, prepare a topic based vocab
with open(os.getcwd()+'/input/NB_training.csv') as csvfile:    
    csvreader = csv.reader(csvfile, delimiter=',', quotechar='"')
    for row in csvreader:
        if line_number > train_validation_split:
            break
        id = int(row[0])
        words = row[1].split(';')
        topics = row[2].split(';')
        for topic in topics:
            if topic not in TOPIC_COUNTS:
                TOPIC_COUNTS[topic] = 0
            TOPIC_COUNTS[topic] += 1
        for topic in topics:
            for word in words:
                if topic not in VOCAB_TOPIC_BASED:
                    VOCAB_TOPIC_BASED[topic] = {}
                    VOCAB_TOPIC_BASED[topic][word] = 1
                else:
                    if word not in VOCAB_TOPIC_BASED[topic]:
                        VOCAB_TOPIC_BASED[topic][word] = 0
                    VOCAB_TOPIC_BASED[topic][word] += 1

### find probabilities of words and topics
PROBS_TOPICS = {}
for topic in TOPIC_COUNTS:
    PROBS_TOPICS[topic] = math.log(TOPIC_COUNTS[topic] / numline)

PROBS_WORDS = {}
alpha = 1 # laplacian smoothing parameter
for word in VOCAB_WORD_BASED:
    total_occurrence = sum(VOCAB_WORD_BASED[word].values())
    PROBS_WORDS[word] = {topic:math.log(((VOCAB_WORD_BASED[word][topic] if topic in VOCAB_WORD_BASED[word] else 0) + alpha) / (total_occurrence + alpha * len(VOCAB_WORD_BASED))) for topic in TOPIC_COUNTS}

### VALIDATION PHASE
Y_true = {}
Y_pred = {}
# predict rest of the (%20) data using previously trained model.
with open(os.getcwd()+'/input/NB_training.csv') as csvfile:
    csvreader = csv.reader(csvfile, delimiter=',', quotechar='"')
    line_number = 0 
    for row in csvreader:
        if line_number < train_validation_split:
            line_number +=1
            continue
        id = int(row[0])
        words = row[1].split(';')
        topics = row[2].split(';')
        Y_true[id]= topics
        topic_score = {}
        for topic in TOPIC_COUNTS:
            score = PROBS_TOPICS[topic]
            total_words_of_topics = sum(VOCAB_TOPIC_BASED[topic].values())
            for word in words:
                total_occurrences_of_words = VOCAB_WORD_BASED.get(word)
                if total_occurrences_of_words is None:
                    score += math.log((0 + alpha) / (total_words_of_topics + alpha * len(VOCAB_WORD_BASED)))
                else:
                    score += math.log((total_occurrences_of_words.get(topic,0) + alpha) / (total_words_of_topics + alpha * len(VOCAB_WORD_BASED)))
            topic_score[topic] = score
        
        sorted_list = sorted(topic_score,key=topic_score.get,reverse=True)
        current_pred = []
        for i in range(len(sorted_list)-1):
            if (topic_score[sorted_list[0]] - topic_score[sorted_list[i]]) * MULTILABEL_THRESHOLD_MULTIPLIER < (topic_score[sorted_list[i]] - topic_score[sorted_list[i+1]]):    
                current_pred.append(sorted_list[i])
        Y_pred[id] = current_pred
        line_number +=1

TOPICS = ['earn', 'acq', 'money-fx', 'crude', 'grain', 'trade', 'interest', 'wheat', 'ship', 'corn']
with open(os.getcwd()+'/output/NB_train_pred.csv', 'w') as test_file:
    header = ['doc_id']+ TOPICS
    file_writer = csv.DictWriter(test_file, fieldnames = header)
    file_writer.writeheader()
    for doc_id,topics in Y_pred.items():
        file_writer.writerow({"doc_id":doc_id, **{topic: 1 if topic in topics else 0 for topic in TOPICS }})

with open(os.getcwd()+'/output/NB_train_true.csv', 'w') as test_file:
    header = ['doc_id']+ TOPICS
    file_writer = csv.DictWriter(test_file, fieldnames = header)
    file_writer.writeheader()
    for doc_id,topics in Y_true.items():
        file_writer.writerow({"doc_id":doc_id, **{topic: 1 if topic in topics else 0 for topic in TOPICS }})
