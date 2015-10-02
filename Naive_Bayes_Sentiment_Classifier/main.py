from build_vocab import *
from train import *
from test import *



def main():
    # args should include the following in sequence:
    # file path for negative words
    # file path for positive words
    # directory of negative training/testing examples
    # directory of positive training/testing examples
    # partial=True means model test on testing split; otherwise on training split
    # neg_hand=True means negation handling is enabled
    # bigram_hand=True means bigram handling is enabled

    partial = False
    neg_hand = False
    bigram_hand = False

    args = ['/Users/tianshuren/Google Drive/10701/Homework 1/opinion-lexicon-English/negative-words.txt',
            '/Users/tianshuren/Google Drive/10701/Homework 1/opinion-lexicon-English/positive-words.txt',
            '/Users/tianshuren/Google Drive/10701/Homework 1/review_polarity/txt_sentoken/neg/*',
            '/Users/tianshuren/Google Drive/10701/Homework 1/review_polarity/txt_sentoken/pos/*',
            partial, neg_hand, bigram_hand]

    N_Voc = args[0]
    P_Voc = args[1]
    N_Train = args[2]
    P_Train = args[3]
    N_Test = N_Train
    P_Test = P_Train

    config = [partial, neg_hand, bigram_hand]

    bigrams = ['extremely', 'quite', 'just', 'almost', 'very', 'too', 'enough']

    print 'building vocabulary...'
    vocab = build(N_Voc, P_Voc)
    print 'training neg files at ' + N_Train + '; pos files at ' + P_Train + '...'
    (num_neg, num_pos, vocab) = train(N_Train, P_Train, vocab, bigrams, config)
    print 'testing on negative files at ' + N_Test + '...'
    (neg_correct, neg_total) = test(N_Test, 'negative', vocab, bigrams, num_neg, num_pos, config)
    print 'testing on positive files at ' + P_Test + '...'
    (pos_correct, pos_total) = test(P_Test, 'positive', vocab, bigrams, num_neg, num_pos, config)
    total_accuracy = float(neg_correct + pos_correct) / (neg_total + pos_total)
    print 'total accuracy is %f' % total_accuracy
