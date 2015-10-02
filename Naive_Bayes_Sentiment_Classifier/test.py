import glob
import math
import re


def test(path, label, vocab_in, bigrams, num_neg, num_pos, config):
	vocab = vocab_in
	partial = config[0]
	neg_hand = config[1]
	bigram_hand = config[2]

	test_path = path
	total_predictions = 0
	correct_predictions = 0
	if label == 'positive':
		true_label = 1
	else:
		true_label = 0

	for path in glob.glob(test_path):
		if partial and re.findall('cv(\d+)', path) < ['800']:
			pass
		elif (not partial and re.findall('cv(\d+)', path) > ['800']):
			pass
		else:
			doc = open(path, 'r')
			if (bigram_hand and neg_hand):
				features = extract_features_bgnh(doc, vocab, bigrams)
			elif (bigram_hand):
				features = extract_features_bg(doc, vocab, bigrams)
			elif (neg_hand):
				features = extract_features_nh(doc, vocab)
			else:
				features = extract_features_basic(doc, vocab)
			res = classify(features, num_neg, num_pos)
			if res == true_label:
				correct_predictions += 1
			else:
				print 'file misidentified' + doc.name
			total_predictions += 1
			doc.close()

	print 'accuracy rate is %f' % (float(correct_predictions)/total_predictions)

	return correct_predictions, total_predictions


def classify(features, num_neg, num_pos):
	# Classify document based on Naive Bayes model.

	smo_fac = 0.1
	log_prob_neg = 0
	log_prob_pos = 0
	# likelihood from testing data
	for index in features:
		log_prob_neg += math.log((num_neg[index] + smo_fac) / (num_neg[-1] + smo_fac * len(num_neg)))
		log_prob_pos += math.log((num_pos[index] + smo_fac) / (num_pos[-1] + smo_fac * len(num_pos)))

	# add likelihood from prior distribution
	log_prob_neg += math.log(float(num_neg[-1]) / (num_neg[-1] + num_pos[-1]))
	log_prob_pos += math.log(float(num_pos[-1]) / (num_neg[-1] + num_pos[-1]))

	return log_prob_pos > log_prob_neg


def extract_features_bgnh(doc, vocab, bigrams):
	# Extract features with Bigram and Negation handling
	res = []
	is_negate = False
	is_bigram = False
	prev_word = ""
	for line in doc:
		for word in line.split(' '):
			if (is_negate):
				if to_add('not_' + word, vocab, res):
					res.append(vocab.index('not_' + word))
				is_negate = False
			elif (is_bigram):
				if to_add(prev_word + ' ' + word, vocab, res):
					res.append(vocab.index(prev_word + ' ' + word))
				is_bigram = False
			else:
				if to_add(word, vocab, res):
					res.append(vocab.index(word))
			if ((word[-3:] == 'n\'t') or (word == 'not')):
				is_negate = True
			if (word in bigrams):
				is_bigram = True
				prev_word = word
	return res


def extract_features_bg(doc, vocab, bigrams):
	# Extract features with Bigram handling
	res = []
	is_bigram = False
	prev_word = ""
	for line in doc:
		for word in line.split(' '):
			if (is_bigram):
				if to_add(prev_word + ' ' + word, vocab, res):
					res.append(vocab.index(prev_word + ' ' + word))
				is_bigram = False
			else:
				if to_add(word, vocab, res):
					res.append(vocab.index(word))
			if (word in bigrams):
				is_bigram = True
				prev_word = word

	return res


def extract_features_nh(doc, vocab):
	# Extract features with Negation handling
	res = []
	is_negate = False
	for line in doc:
		for word in line.split(' '):
			if (is_negate):
				if to_add('not_' + word, vocab, res):
					res.append(vocab.index(word))
				is_negate = False
			else:
				if to_add(word, vocab, res):
					res.append(vocab.index(word))
			if ((word[-3:] == 'n\'t') or (word == 'not')):
				is_negate = True

	return res


def extract_features_basic(doc, vocab):
	# Most basic version. No negation/bigram handling
	res = []
	for line in doc:
		for word in line.split(' '):
			if to_add(word, vocab, res):
				res.append(vocab.index(word))
	return res


def to_add(s, vocab, res):
	# helper function to decide if string s is in vocabulary, and not included in output of this iteration
	# (already indicated s exist in file).
	return ((s in vocab) and (not vocab.index(s) in res))
