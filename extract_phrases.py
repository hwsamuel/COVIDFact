from gensim.models.phrases import Phrases, Phraser
import pickle
from nltk import word_tokenize
from nltk.util import ngrams
from nltk import download
from nltk.lm import NgramCounter
from pandas import read_csv
from pickle import dump, load

treatment_word_list = ['treatment', 'treated', 'treats', 'treat', 'treating', 'therapy', 'therapeutic']
cause_word_list = ['aethiology', 'aetiology', 'etiology', 'causes', 'cause', 'caused', 'causing', 'aitiology', 'causality', 'causal', 'causation', 'causativity', 'causative', 'causable', 'causability', 'induce']
prevent_word_list = ['preventable', 'prevent', 'prevents', 'preventing', 'prevented', 'preventability', 'preventible', 'preventiveness', 'preventive', 'prevention', 'prophylaxis', 'prophylax', 'prophylactic', 'prophylaxis']

'''
#filename = 'medical_datasets/prevent_word_list.p'
#filename = 'medical_datasets/cause_word_list.p'
filename = 'medical_datasets/treatment_word_list.p'
text = pickle.load(open(filename, 'rb'))
text_bigrams = [ngrams(sent, 2) for sent in text]
text_unigrams = [ngrams(sent, 1) for sent in text]
ngram_counts = NgramCounter(text_bigrams + text_unigrams)
pickle.dump(ngram_counts, open('treatment_phrases.p', 'wb'))
'''
cause_phrase_filename = 'cause_phrases.p'
prevent_phrase_filename = 'prevent_phrases.p'
treatment_phrase_filename = 'treatment_phrases.p'


def get_phrases(word:str):
	phrase_list = []
	if word=='cause':
		phrase_list.extend(cause_word_list)
		cause_phrases = pickle.load(open(cause_phrase_filename, 'rb'))
		for word in cause_word_list:
			phrase_list.extend([word+' ' + _ for _ in list(cause_phrases[[word]])])
	
	elif word=='prevent':
		phrase_list.extend(prevent_word_list)
		prevent_phrases = pickle.load(open(prevent_phrase_filename, 'rb'))
		for word in prevent_word_list:
			phrase_list.extend([word+' ' + _ for _ in list(prevent_phrases[[word]])])

	elif word=='treat':
		phrase_list.extend(treatment_word_list)
		treatment_phrases = pickle.load(open(treatment_phrase_filename, 'rb'))
		for word in treatment_word_list:
			phrase_list.extend([word+' ' + _ for _ in list(treatment_phrases[[word]])])
	
	return phrase_list

if __name__=='__main__':
	#print(get_phrases('cause'))
	#print(get_phrases('prevent'))
	cause_tweets = []
	#treat_phreses_set = set(get_phrases('treat'))
	med_text = read_csv('grebe_covid_med_for_hamman_with_vector.csv', usecols=['text'], dtype=str)
	for text in med_text.text:
		if set(cause_word_list).intersection(set(text.split())):
			cause_tweets.append(1)
			print('here')
		else:
			cause_tweets.append(0)
	dump(cause_tweets, open('cause_tweets.p', 'wb'))
	
	
	
	
	
