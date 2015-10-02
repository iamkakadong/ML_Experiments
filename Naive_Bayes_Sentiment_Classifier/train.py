import glob
import re


def train(neg_file_path, pos_file_path, vocab_in, bigrams_in, config):
	# train files in indicated directory with specified configuration.

	bigrams = bigrams_in

	count = 0

	vocab = vocab_in
	# Vocabulary is m * 1 vector. 
	num_neg = [0] * len(vocab)
	neg_path = neg_file_path
	pos_path = pos_file_path

	(num_neg, vocab) = update(neg_path, vocab, bigrams, num_neg, config)
	count += num_neg[-1]	# last item is the number of neg training samples

	num_pos = [0] * len(vocab)
	(num_pos, vocab) = update(pos_path, vocab, bigrams, num_pos, config)
	count += num_pos[-1]	# last item is the number of pos training samples

	tmp = num_neg[-1]
	del num_neg[-1]
	num_neg.extend([0] * (len(vocab) - len(num_neg)))
	num_neg.append(tmp)
	
	print 'total number of files trained %d' % count
	return num_neg, num_pos, vocab


def update(directory, vocab, bigrams, counts, config):
	# directory points to a list of training files
	# vocab is a vocabulary that contains meaningful words
	# bigrams is list of bigrams to detect
	# counts is a list s.t. len(counts) = len(vocab). counts[i] = # of times vocab[i] appears in the training files
	# config is configuration of negation handling and bigram handling

	neg_hand = config[1]
	bigram_hand = config[2]
	num_files = 0
	for path in glob.glob(directory):
		if re.findall('cv(\d+)', path) > ['799']:
			pass
		else:
			doc = open(path, 'r')
			if (neg_hand and bigram_hand):
				msgs = extract_message_bgnh(doc, vocab, bigrams)
			elif (bigram_hand):
				msgs = extract_message_bg(doc, vocab, bigrams)
			elif (neg_hand):
				msgs = extract_message_nh(doc, vocab)
			else:
				msgs = extract_message_basic(doc, vocab)
			for msg in msgs:
				if msg > len(counts) - 1:
					counts.append(1)
				else:
					counts[msg] += 1
			doc.close()
			num_files += 1

	counts.append(num_files)

	pairs = zip(counts, range(0, len(counts)))
	del pairs[-1]
	pairs.sort(reverse=True)
	pairs = pairs[0:10]
	sent_car = []
	for i in pairs:
		sent_car.append(vocab[i[1]] + str(i[0]))
	print sent_car

	return counts, vocab


def extract_message_bgnh(doc, vocab, bigrams):
	# Extract message supporting Bigram and Negation handling.
	res = []
	is_negate = False
	is_bigram = False
	for line in doc:
		for word in line.split(' '):
			if (word in vocab):
				if is_negate and (word != 'not' or word[-3:] != 'n\t'):
					if (not (('not_' + word) in vocab)):
						vocab.append('not_' + word)
					if (not (vocab.index(('not_' + word)) in res)):
						res.append(vocab.index('not_' + word))	# always the last item in vocab
					is_negate = False
				elif is_bigram:
					if (not (prev_word + ' ' + word) in vocab):
						vocab.append(prev_word + ' ' + word)
					if (not vocab.index(prev_word + ' ' + word) in res):
						res.append(vocab.index(prev_word + ' ' + word))
					is_bigram = False
				elif (not (vocab.index(word) in res)):
					res.append(vocab.index(word))
			else:
				is_negate = False
				is_bigram = False
			if (word == 'not' or word[-3:] == 'n\'t'):
				is_negate = True
			if (word in bigrams):
				is_bigram = True
				prev_word = word
	return res


def extract_message_bg(doc, vocab, bigrams):
	# Extract message supporting Bigram handling.
	res = []
	is_bigram = False
	prev_word = ""
	for line in doc:
		for word in line.split(' '):
			if (word in vocab):
				if is_bigram:
					if (not (prev_word + ' ' + word) in vocab):
						vocab.append(prev_word + ' ' + word)
					if (not vocab.index(prev_word + ' ' + word) in res):
						res.append(vocab.index(prev_word + ' ' + word))
					is_bigram = False
				elif (not (vocab.index(word) in res)):
					res.append(vocab.index(word))
			else:
				is_bigram = False
			if (word in bigrams):
				is_bigram = True
				prev_word = word
	return res


def extract_message_nh(doc, vocab):
	# Extract message supporting Negation handling.
	is_negate = False
	res = []
	for line in doc:
		for word in line.split(' '):
			if (word in vocab):
				if is_negate:
					if (not (('not_' + word) in vocab)):
						vocab.append('not_' + word)	# always the last item in vocab
					if (not (vocab.index(('not_' + word)) in res)):
						res.append(vocab.index('not_' + word))
				elif (not (vocab.index(word) in res)):
					res.append(vocab.index(word))
			if (word == 'not' or word[-3:] == 'n\'t'):
				is_negate = True
			else:
				is_negate = False
	return res


def extract_message_basic(doc, vocab):
	# Most basic version. No negation/bigram handling
	res = []
	for line in doc:
		for word in line.split(' '):
			if (word in vocab) and (not vocab.index(word) in res):
				res.append(vocab.index(word))
	return res
