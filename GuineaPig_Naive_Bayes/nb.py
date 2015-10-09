from guineapig import *
import sys
import re
import string

# supporting routines can go here
def tokenizer(line):
	l = list()
	tmp = ''
	isdigit = True
	for c in line:
		if c == ' ' or c == '\n':
			if isdigit:
				pass
			else:
				l.append(tmp)
			tmp = ''
			isdigit = True
		elif c in string.punctuation:
			pass
		elif not c.isdigit():
			isdigit = False
			tmp = tmp + c
		else:
			tmp = tmp + c
	return l

def tokens(line):
	info = line.split('\t')
	labels = info[1].split(',')
	words = info[2]
	# for tok in tokenizer(words):
		# yield (tok.lower(), 1)
	for tok in tokenizer(words):
		for label in labels:
			yield ('=ANY', label)
			yield (tok.lower(), label)
			# yield (tok.lower(), 'Y=ANY')
	for label in labels:
		yield ('Y=', label)
		yield ('Y=ANY', label)

def genKV(counts):
	word = counts[0][0]
	label = counts[0][1]
	yield (word, label + '=' + str(counts[1]))

def tsplit(line):
	info = line.split('\t')
	docId = info[0]
	words = info[2]
	for tok in tokenizer(words):
		yield (tok.lower(), docId)
	yield ('=ANY', docId)
	yield ('Y=', docId)
	yield ('Y=ANY', docId)

def compute():
	# Calculates log probability for each label
	return 0

#always subclass Planner
class NB(Planner):
	# params is a dictionary of params given on the command line. 
	# e.g. trainFile = params['trainFile']
	params = GPig.getArgvParams()

	# Begin of Training
	lines = ReadLines(params['trainFile'])
	msgs = Flatten(lines,by=tokens)
	counts = Group(msgs, by=lambda x:x, reducingTo=ReduceToCount())

	keyVal = Flatten(counts, by=genKV)
	something = Group(keyVal, by=lambda (word, msg):word, retaining=lambda (word, msg):msg,\
					  reducingTo=ReduceTo(str, lambda accum,val:accum+val))
	# End of Training

	# Begin of Testing
	linesT = ReadLines(params['testFile'])
	msgsT = Flatten(linesT,by=tsplit)
	table = Join(Jin(something,by=lambda(key,val):key), Jin(msgsT,by=lambda(word,id):word))\
			| ReplaceEach(by=lambda((key,val),(word,id)):(key,(val,id)))
	summaries = Filter(table, by=lambda(word,msg):(word == '=ANY' or word == 'Y+ANY')) #| Flatten(by=lambda test:(test[0],test[1][0]))
	something2 = Join(Jin(table,by=lambda(word,msg):msg[1]), Jin(summaries,by=lambda(word,msg):msg[1])) \
				 | ReplaceEach(by=lambda((word1,msg1),(word2,msg2)):(msg1[1],(msg1[0],msg2[0])))
	# TO-DO: Finish compute function
	something3 = Flatten(something2,by=compute)
	# TO-DO: Logic in this line.
	res = Group(something3, by=lambda (id, msgs):id, \
				reducingTo=ReduceTo(list, by=lambda accum, val:accum + val))
# always end like this
if __name__ == "__main__":
	NB().main(sys.argv)

# supporting routines can go here
