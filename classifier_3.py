#TF-IDF and NaiveBayes

import pandas as pd
import csv
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score
from sklearn import naive_bayes
from sklearn.naive_bayes import GaussianNB
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics import accuracy_score
from sklearn.metrics import precision_score
from sklearn.metrics import recall_score
from sklearn.metrics import f1_score
from sklearn.metrics import classification_report

train_data = pd.read_csv('corpus.csv', encoding = 'utf-8', delimiter = ';', names = ['tweet', 'score'])

X_train,X_test,y_train,y_test = train_test_split(train_data["tweet"],train_data["score"],test_size=0.2)

vect = TfidfVectorizer()

X_train_vectorized = vect.fit_transform((X_train).values.astype('U'))

model = naive_bayes.MultinomialNB()

model.fit(X_train_vectorized, y_train)

feature_names = np.array(vect.get_feature_names())
sorted_index=model.coef_[0].argsort()

predictions=model.predict(vect.transform((X_test).values.astype('U')))


#print(predictions)
print(feature_names[sorted_index[:-50:-1]])

#accuracy
accuracy = accuracy_score(y_test, predictions)
#print(accuracy)

#precision
precision = precision_score(y_test, predictions)
#print(precision)

#recall
recall = recall_score(y_test, predictions)
#print(recall)


#f1_score
f1_score = f1_score(y_test, predictions)
#print(f1_score)
#print(roc_auc_score(y_test, predictions))
report = classification_report(y_test, predictions, target_names = ['tweet', 'score'])
#print(report)


sentence = input()
if model.predict(vect.transform([sentence]))==[1]:
    print("кажется, это агрессивное сообщение")
else:
    print("скорее всего, в этом сообщении агрессии нет")
