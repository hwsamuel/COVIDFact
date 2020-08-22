
import gensim.downloader as api
from pickle import load, dump
import numpy as np
from pandas import DataFrame, read_csv, concat
from random import shuffle
from gensim.summarization.textcleaner import split_sentences
from nltk.tokenize import word_tokenize
from sklearn import svm
import re
from sklearn.model_selection import train_test_split
import ast
from sklearn.metrics import precision_recall_fscore_support
from gensim.models import KeyedVectors
from sklearn.linear_model import LinearRegression
from sklearn.linear_model import LogisticRegression
from sklearn.neural_network import MLPClassifier
from sklearn.model_selection import ShuffleSplit

def conversion(training_data_csv, vector_csv):
	training_data_csv.dropna(inplace=True)
	# brief_cleaning = (sub("[^A-Za-z]+", ' ', str(row)).lower() for row in df_temp_clean['temp_clean'])
	
	for index, datapoint in training_data_csv.iterrows():
		temp_list = []
		for sentence in split_sentences(datapoint.text):
			sentence = re.sub("[^A-Za-z]+", ' ', str(sentence)).lower()
			sentence = re.sub(r'\s+', ' ', str(sentence))
			#print(word_tokenize(sentence))
			temp_list.append(encode(word_tokenize(sentence)))
		temp_df = np.array(temp_list)
		temp_df = np.average(temp_df, axis=0)
		temp_df = DataFrame([[str(temp_df), datapoint.label]], columns=['vector', 'label'])
		temp_df.to_csv(vector_csv, index=False, header=False, mode='a')


# google only modification 
# google only csvs ok

#vector_csv = 'training_data_vector_new_combined_10.csv'

#og_encoder = api.load("word2vec-google-news-300")
og_encoder = KeyedVectors.load_word2vec_format('word2vec_twitter_tokens_getit_actual.bin', binary=True, unicode_errors='ignore')
#encoder = load(open('w2v_model_google_true.p', 'rb'))
encoder = load(open('w2v_model_pubmed_opinion_sk_5_5.p', 'rb'))
#nn_model = load(open('trained_regressor_google_combined.p', 'rb'))
nn_model = load(open('trained_regressor_model_pubmed_opinion_sk_5_5.p', 'rb'))


data_filename = 'tweets_health_curated_list_mod.csv'
training_data_filename = 'training_data_sick.csv'
testing_data_filename = 'testing_data_sick.csv'

vector_traindata_final = 'trainset_final_sick.csv'
vector_testdata_final = 'testset_final_sick.csv'

df = read_csv(data_filename)
rs = ShuffleSplit(n_splits=1, test_size=0.20, random_state=0)
train_indices = []
test_indices = []
for train_index, test_index in rs.split(list(df.index)):
	train_indices = train_index
	test_indices = test_index

df.iloc[train_indices].to_csv(training_data_filename, columns=['id', 'text', 'label'], index=False)
df.iloc[test_indices].to_csv(testing_data_filename, columns=['id', 'text', 'label'], index=False)

# remove this when done
df = DataFrame(columns=['vector', 'label'])
df.to_csv(vector_traindata_final, index=False)
df.to_csv(vector_testdata_final, index=False)


def encode(tokens, label=None):
	X = []
	y = []
	for token in tokens:
		#if token in og_encoder.vocab:
		#	X.append(og_encoder[token])
		#	y.append(label)
		
		if token in og_encoder.vocab:
			X.append(nn_model.predict(og_encoder[token].reshape(1, -1))[0])
			y.append(label)
		
		elif token in encoder.wv.vocab:
			X.append(encoder.wv.get_vector(token))
			y.append(label)
		
		#else:
		#	#print(encoder.vector_size)
		#	X.append(np.zeros(encoder.vector_size))
		#	y.append(-1)
	if not X:
		df = np.zeros(encoder.vector_size)
		return df
	else:
		df = np.array(X)
	return np.average(df, axis=0)
	# return (X,y)


def tokenize(sentence):
	tokens = word_tokenize(sentence)
	# tokens = [t1.lower() for t1 in tokens if t1 not in punctuation] # Remove punctuations & stop words using Glasgow stop words list
	return tokens
	
def convert_str_dataframe(df_vector, X, y):
	for index, lst_string_temp in df_vector.iterrows():
		X_ = re.sub('\n', '', lst_string_temp.vector)
		y_ = lst_string_temp.label
		X_ = re.sub('\s+', ',', X_)
		X_ = re.sub('\[\,', '[', X_)
		X.append(ast.literal_eval(X_))
		y.append(y_)
	

if __name__=='__main__':
	
	
	training_data_csv = read_csv(training_data_filename)
	testing_data_csv = read_csv(testing_data_filename)
	
	
	conversion(training_data_csv, vector_traindata_final)
	conversion(testing_data_csv, vector_testdata_final)


	#lst_string = training_data_vector_shuffle[~training_data_vector_shuffle.vector.str.contains('nan')]
	X_train = []
	y_train = []
	X_test = []
	y_test = []
	
	training_data_vector_training_shuffle = read_csv(vector_traindata_final)
	training_data_vector_testing_shuffle = read_csv(vector_testdata_final)
	
	convert_str_dataframe(training_data_vector_training_shuffle, X_train, y_train)
	convert_str_dataframe(training_data_vector_testing_shuffle, X_test, y_test)


	print(np.array(X_train).shape)
	print(np.array(y_train).shape)
	print(np.array(X_test).shape)
	print(np.array(y_test).shape)
	print(type(np.array(X_train)[0][0]))
	print(training_data_vector_testing_shuffle.shape)
	
	C = 1.5
	print(C)
	
	clf = svm.SVC(C=C, gamma='scale', kernel='rbf')
	clf.fit(X_train, y_train)
	print(clf.score(X_test, y_test))
	
	'''
	clf = LogisticRegression(random_state=0, C=C, solver='lbfgs', max_iter=10000).fit(X_train, y_train)
	print(clf.score(X_test, y_test))
	#print(clf.predict(X_test))
	'''
	'''
	clf = MLPClassifier(hidden_layer_sizes=(300, 600, 300, 50 ), random_state=1, max_iter=3000).fit(X_train, y_train)
	print(clf.loss_)
	print(clf.score(X_test, y_test))
	'''
	#print(y_test)
	print(precision_recall_fscore_support(y_test, clf.predict(X_test), labels=[0, 1]))
	# df = np.array(encode(['virus', 'coronavirus', 'covid-19'])[0])
	# print(np.average(df, axis=0))
	





