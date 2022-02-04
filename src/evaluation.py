import csv,os

def evaluate_and_print(y_true_file_name,y_pred_file_name):
    CONFUSION_MATRIX = {'earn':[[0,0],[0,0]], 'acq':[[0,0],[0,0]], 'money-fx':[[0,0],[0,0]], 'crude':[[0,0],[0,0]], 'grain':[[0,0],[0,0]], 'trade':[[0,0],[0,0]], 'interest':[[0,0],[0,0]], 'wheat':[[0,0],[0,0]], 'ship':[[0,0],[0,0]], 'corn':[[0,0],[0,0]]}

    with open(os.getcwd()+y_true_file_name) as file1, open(os.getcwd()+y_pred_file_name) as file2:
        csvreader1 = csv.DictReader(file1)
        csvreader2 = csv.DictReader(file2)
        for line_pred,line_true in zip(csvreader1,csvreader2):
            for topic in CONFUSION_MATRIX:
                if line_true[topic] == "1" and line_pred[topic] == "1":
                    CONFUSION_MATRIX[topic][0][0] +=1
                elif line_true[topic] == "1" and line_pred[topic] == "0":
                    CONFUSION_MATRIX[topic][0][1] +=1
                elif line_true[topic] == "0" and line_pred[topic] == "1":
                    CONFUSION_MATRIX[topic][1][0] +=1
                elif line_true[topic] == "0" and line_pred[topic] == "0":
                    CONFUSION_MATRIX[topic][1][1] +=1


    print("\n\x1b[2;30;44mCONFUSION MATRIXS:\x1b[0m ")
    for topic in CONFUSION_MATRIX:
        print('{:>8} '.format(topic),CONFUSION_MATRIX[topic])


    accuracies = {topic:(CONFUSION_MATRIX[topic][0][0] +CONFUSION_MATRIX[topic][1][1])/(CONFUSION_MATRIX[topic][0][0]+CONFUSION_MATRIX[topic][1][0]+CONFUSION_MATRIX[topic][0][1]+CONFUSION_MATRIX[topic][1][1]) for topic in CONFUSION_MATRIX}
    print("\n\x1b[2;30;44mACCURACY:\x1b[0m ")
    for topic in accuracies:
        print('{:>8} '.format(topic),accuracies[topic])

    print("\n\x1b[2;30;44mPRECISION:\x1b[0m ")
    precisions = {topic:CONFUSION_MATRIX[topic][0][0]/(CONFUSION_MATRIX[topic][0][0]+CONFUSION_MATRIX[topic][0][1]) for topic in CONFUSION_MATRIX}
    for topic in CONFUSION_MATRIX:
        print('{:>8} '.format(topic),precisions[topic])
    print('{:>8} '.format("\x1b[2;30;43mMACRO_AVERAGE:\x1b[0m"),sum(precisions.values())/len(precisions))
    print('{:>8} '.format("\x1b[2;30;43mMICRO_AVERAGE:\x1b[0m"),sum(CONFUSION_MATRIX[x][0][0] for x in CONFUSION_MATRIX) / sum(CONFUSION_MATRIX[x][0][0]+CONFUSION_MATRIX[x][0][1] for x in CONFUSION_MATRIX))

    print("\n\x1b[2;30;44mRECALL:\x1b[0m ")
    recalls = {topic:(CONFUSION_MATRIX[topic][0][0])/(CONFUSION_MATRIX[topic][0][0]+CONFUSION_MATRIX[topic][1][0]) for topic in CONFUSION_MATRIX}
    for topic in CONFUSION_MATRIX:
        print('{:>8} '.format(topic),recalls[topic])
    print('{:>8} '.format("\x1b[2;30;43mMACRO_AVERAGE:\x1b[0m"),sum(recalls.values())/len(recalls))
    print('{:>8} '.format("\x1b[2;30;43mMICRO_AVERAGE:\x1b[0m"),sum(CONFUSION_MATRIX[x][0][0] for x in CONFUSION_MATRIX) / sum(CONFUSION_MATRIX[x][0][0]+CONFUSION_MATRIX[x][1][0] for x in CONFUSION_MATRIX))

    print("\n\x1b[2;30;44mF1:\x1b[0m ")
    f_1s = {topic:2*(recalls[topic]*precisions[topic])/(recalls[topic]+precisions[topic]) for topic in CONFUSION_MATRIX}
    for topic in CONFUSION_MATRIX:
        print('{:>8} '.format(topic),f_1s[topic])
    print('{:>8} '.format("\x1b[2;30;43mMACRO_AVERAGE:\x1b[0m"),sum(f_1s.values())/len(f_1s))
    print('{:>8} '.format("\x1b[2;30;43mMICRO_AVERAGE:\x1b[0m"),
    2*(sum(CONFUSION_MATRIX[x][0][0] for x in CONFUSION_MATRIX) / sum(CONFUSION_MATRIX[x][0][0]+CONFUSION_MATRIX[x][1][0] for x in CONFUSION_MATRIX)
    * (sum(CONFUSION_MATRIX[x][0][0] for x in CONFUSION_MATRIX) / sum(CONFUSION_MATRIX[x][0][0]+CONFUSION_MATRIX[x][0][1] for x in CONFUSION_MATRIX)))
    /((sum(CONFUSION_MATRIX[x][0][0] for x in CONFUSION_MATRIX) / sum(CONFUSION_MATRIX[x][0][0]+CONFUSION_MATRIX[x][1][0] for x in CONFUSION_MATRIX))
    + (sum(CONFUSION_MATRIX[x][0][0] for x in CONFUSION_MATRIX) / sum(CONFUSION_MATRIX[x][0][0]+CONFUSION_MATRIX[x][0][1] for x in CONFUSION_MATRIX))))





print("\x1b[2;30;42mNB train\x1b[0m")
evaluate_and_print('/output/NB_train_true.csv','/output/NB_train_pred.csv')
print("\n\n\x1b[2;30;42mNB test\x1b[0m")
evaluate_and_print('/output/NB_true.csv','/output/NB_pred.csv')
print("\n\n\x1b[2;30;42mKNN, K=1\x1b[0m")
evaluate_and_print('/output/KNN_true.csv','/output/KNN_pred_k_1.csv')
print("\n\n\x1b[2;30;42mKNN, K=3\x1b[0m")
evaluate_and_print('/output/KNN_true.csv','/output/KNN_pred_k_3.csv')
print("\n\n\x1b[2;30;42mKNN, K=5\x1b[0m")
evaluate_and_print('/output/KNN_true.csv','/output/KNN_pred_k_5.csv')
print("\n\n\x1b[2;30;42mKNN, K=7\x1b[0m")
evaluate_and_print('/output/KNN_true.csv','/output/KNN_pred_k_7.csv')
