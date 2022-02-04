* My python version is 3.8.10
* No external library is used.
* Run all the scripts from the `veyis` folder
## NB

* You can run the NB preprocess using the following command: <code> python3 src/NB_preprocess.py</code> 
  * It will generate two csv files named <code> NB_training.csv</code> and <code> NB_test.csv</code> in the input folder.
  * They are approximately 5 MB and NB algorithm uses them as input files.
* You can train the NB model using the following command: <code> python3 src/NB_train_model.py</code>.
  * It will generate two csv files named <code> NB_train_true.csv</code> and <code> NB_train_pred.csv</code> in the output folder.
* You can run the the NB model on the test data using the following command: <code> python3 src/NB_test_model.py</code>.
  * It will generate two csv files named <code> NB_true.csv</code> and <code> NB_pred.csv</code> in the output folder.

## KNN

* You can run the KNN preprocess using the following command: <code> python3 src/KNN_preprocess.py</code> 
  * It will generate three json files named <code> KNN_document_frequency_index.json</code>, <code> KNN_inverted_index.json</code> and <code> KNN_preprocessed_test_data.json</code> in the indexes and input folders.
  * They are approximately 18 MB and KNN algorithm uses them as input files.
* You can run the the KNN model on the test data using the following command: <code> python3 src/KNN_classifier.py</code>.
  * It will generate 5 csv files named <code> KNN_true.csv</code>,  <code> KNN_pred_k_1.csv</code>, <code> KNN_pred_k_3.csv</code>,<code> KNN_pred_k_5.csv</code> and <code> KNN_pred_k_7.csv</code> in the output folder.

* You can evaluate all these models using `evaluate.py` script in the src folder. To run it use the following command: `python3 src/evaluate.py`. **IMPORTANT REMINDER**: You should run the commands above previously to evaluate them.

* To perform randomization test, run the statistical_significance.py script using the following command: `python3 src/statistical_significance.py`.

### Other notes

* [Reuters dataset](https://archive.ics.uci.edu/ml/datasets/reuters-21578+text+categorization+collection) and stopwords.txt must be in the root folder, not in src folder.


**Adalet Veyis Turgut**