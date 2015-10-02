
def build(neg_word_path, pos_word_path):
	# Build vocabulary from path
	vocab = []
	f1 = open(neg_word_path, 'r')
	for line in f1:
		if (line[0] != ';') and (line[0] != '\n'):
			vocab.append(line[:-1])
	f1.close()

	f2 = open(pos_word_path, 'r')
	for line in f2:
		if (line[0] != ';') and (line[0] != '\n'):
			vocab.append(line[:-1])
	f2.close()

	vocab.sort()

	return vocab
