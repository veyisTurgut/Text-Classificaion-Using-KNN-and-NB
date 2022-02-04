import os
import csv
import random

# NB MACRO F1:    0.7477451745524447
# KNN_1 MACRO F1: 0.6767223522927053
# KNN_3 MACRO F1: 0.7407012849375776
# KNN_5 MACRO F1: 0.7620758728480217
# KNN_7 MACRO F1: 0.8054397197000875


macro_avgs_of_models = {"NB_pred": 0.7477451745524447, "KNN_pred_k_1": 0.6767223522927053,
                        "KNN_pred_k_3": 0.7407012849375776, "KNN_pred_k_5": 0.7620758728480217, "KNN_pred_k_7": 0.8054397197000875}
model_names = ["NB_pred", "KNN_pred_k_1", "KNN_pred_k_3", "KNN_pred_k_5", "KNN_pred_k_7"]
TRUE_VALS = []
with open(os.getcwd()+"/output/NB_true.csv") as file1:
    csvreader1 = csv.reader(file1)
    i = 0
    for true_line, in zip(csvreader1):
        if i == 0:  # pass header of the csv
            i += 1
            continue
        TRUE_VALS.append(true_line[1:])
for m1 in range(len(model_names)):   
    for m2 in range(m1+1,len(model_names)):
        model_1 = model_names[m1]
        model_2 = model_names[m2]
        counter = 0
        for _ in range(1000):
            model_1_shuffled = []
            model_2_shuffled = []
            CONFUSION_MATRIX_MODEL_1 = [[[0, 0], [0, 0]]]*10
            CONFUSION_MATRIX_MODEL_2 = [[[0, 0], [0, 0]]]*10

            with open(os.getcwd()+"/output/"+model_1+".csv") as file1, open(os.getcwd()+"/output/"+model_2+".csv") as file2:
                csvreader1 = csv.reader(file1)
                csvreader2 = csv.reader(file2)
                i = 0
                for pred_1, pred_2 in zip(csvreader1, csvreader2):
                    if i == 0:  # pass header of the csv
                        i += 1
                        continue
                    model_1_pred = pred_1[1:]
                    model_2_pred = pred_2[1:]
                    for j in range(len(model_1_pred)):
                        rand = random.random()
                        if rand > 0.5:
                            temp = model_1_pred[j]
                            model_1_pred[j] = model_2_pred[j]
                            model_2_pred[j] = temp
                    model_1_shuffled.append(model_1_pred)
                    model_2_shuffled.append(model_2_pred)

            for line_pred, line_true in zip(model_1_shuffled, TRUE_VALS):
                for i in range(len(line_pred)):
                    if line_true[i] == "1" and line_pred[i] == "1":
                        CONFUSION_MATRIX_MODEL_1[i][0][0] += 1
                    elif line_true[i] == "1" and line_pred[i] == "0":
                        CONFUSION_MATRIX_MODEL_1[i][0][1] += 1
                    elif line_true[i] == "0" and line_pred[i] == "1":
                        CONFUSION_MATRIX_MODEL_1[i][1][0] += 1
                    elif line_true[i] == "0" and line_pred[i] == "0":
                        CONFUSION_MATRIX_MODEL_1[i][1][1] += 1
            for line_pred, line_true in zip(model_2_shuffled, TRUE_VALS):
                for i in range(len(line_pred)):
                    if line_true[i] == "1" and line_pred[i] == "1":
                        CONFUSION_MATRIX_MODEL_2[i][0][0] += 1
                    elif line_true[i] == "1" and line_pred[i] == "0":
                        CONFUSION_MATRIX_MODEL_2[i][0][1] += 1
                    elif line_true[i] == "0" and line_pred[i] == "1":
                        CONFUSION_MATRIX_MODEL_2[i][1][0] += 1
                    elif line_true[i] == "0" and line_pred[i] == "0":
                        CONFUSION_MATRIX_MODEL_2[i][1][1] += 1

            precisions_model_1 = [CONFUSION_MATRIX_MODEL_1[i][0][0] /
                            (CONFUSION_MATRIX_MODEL_1[i][0][0]+CONFUSION_MATRIX_MODEL_1[i][0][1]) for i in range(len(CONFUSION_MATRIX_MODEL_1))]
            recalls_model_1 = [(CONFUSION_MATRIX_MODEL_1[i][0][0])/(CONFUSION_MATRIX_MODEL_1[i][0][0] +
                                                        CONFUSION_MATRIX_MODEL_1[i][1][0]) for i in range(len(CONFUSION_MATRIX_MODEL_1))]
            f_1s_model_1 = [2*(recalls_model_1[i]*precisions_model_1[i])/(recalls_model_1[i] +
                                                        precisions_model_1[i]) for i in range(len(CONFUSION_MATRIX_MODEL_1))]
            macro_f1_model_1 = sum(f_1s_model_1)/len(f_1s_model_1)

            precisions_model_2 = [CONFUSION_MATRIX_MODEL_2[i][0][0]/(
                CONFUSION_MATRIX_MODEL_2[i][0][0]+CONFUSION_MATRIX_MODEL_2[i][0][1]) for i in range(len(CONFUSION_MATRIX_MODEL_2))]
            recalls_model_2 = [(CONFUSION_MATRIX_MODEL_2[i][0][0])/(CONFUSION_MATRIX_MODEL_2[i][0]
                                                                [0]+CONFUSION_MATRIX_MODEL_2[i][1][0]) for i in range(len(CONFUSION_MATRIX_MODEL_2))]
            f_1s_model_2 = [2*(recalls_model_2[i]*precisions_model_2[i])/(recalls_model_2[i] +
                                                                    precisions_model_2[i]) for i in range(len(CONFUSION_MATRIX_MODEL_2))]
            macro_f1_model_2 = sum(f_1s_model_2)/len(f_1s_model_2)
            if abs(macro_f1_model_1 - macro_f1_model_2) > abs(macro_avgs_of_models[model_1]-macro_avgs_of_models[model_2]):
                counter += 1
        p = (counter+1) / 1001
        print(model_1, model_2, p)
