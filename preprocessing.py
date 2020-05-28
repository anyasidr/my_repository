from pandas import read_csv
import re
import pymorphy2
import nltk
from nltk.tokenize import word_tokenize

corpus = pd.read_csv('corpus.csv', encoding = 'utf-8', delimiter = ';', names = ['tweet', 'score']

#приведение слов к нижнему регистру
                     
corpus.tweet = corpus.tweet.str.lower()

#очистка данных
                     
corpus.tweet = re.sub('[^((А-Яа-я)\s)]', '', corpus.tweet)
                     
                
#deleting spaces at the beginning and at the end of each line

corpus.tweet = corpus.tweet.str.strip()                     

#tokenizing the corpus

tokens = nltk.word_tokenize(corpus.tweet)
                     
#removing stopwords

stopwords = []
with open('stopwords.txt', encoding = 'utf-8') as file:
    stopwords = file.read().splitlines()
corpus.tweet = [word for word in tokens if word not in stopwords]

#lemmatization
morph = pymorphy2.MorphAnalyzer()
corpus.tweet =  [morph.parse(word)[0].normal_form for word in corpus.tweet]

corpus.tweet = ' '.join(corpus.tweet)
return corpus.tweet
    
