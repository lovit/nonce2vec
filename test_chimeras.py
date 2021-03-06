#This test the chimeras with a one-off learning procedure.
#python test_chimeras.py models/wiki_all.sent.split.model data/chimeras/chimeras.dataset.l4.tokenised.test.txt 1 10000 3 15 1 70 1.9 5

import gensim, logging
from scipy import stats
from numpy import *
import math
import sys
import re

background = sys.argv[1]
dataset = sys.argv[2]

alpha = sys.argv[3]
sample = sys.argv[4]
neg = sys.argv[5]
window = sys.argv[6]
iter = sys.argv[7]
lambda_den = sys.argv[8]
sample_decay = sys.argv[9]
window_decay = sys.argv[10]

spearmans = []

#########################################
# Spearman correlation
#########################################

#Note: this is scipy's spearman, without tie adjustment
def spearman(x,y):
	return stats.spearmanr(x, y)[0]



###########################################
# Start
###########################################

nonce = "___"
aborted = False
c = 0
f=open(dataset)
for l in f:
    fields=l.rstrip('\n').split('\t')
    sentences = []
    for s in fields[1].split("@@"):
      sentences.append(s.split(' '))
    probes = fields[2].split(',')
    responses = fields[3].split(',')
    print "--"
    print sentences
    print probes
    print responses

    model = gensim.models.Word2Vec.load(background)
    vocab_size = len(model.wv.vocab)
    model.alpha=float(alpha)
    model.sample=float(sample)
    model.sample_decay=float(sample_decay)
    model.iter=int(iter)
    model.negative=int(neg)
    model.nonce=nonce
    model.window=int(window)
    model.window_decay=int(window_decay)
    model.lambda_den=float(lambda_den)
    model.build_vocab(sentences, update=True)
    model.min_count=1
    model.train(sentences)
		
    system_responses = []
    human_responses = []
    p_count = 0
    for p in probes:
      try:
        cos = model.similarity("___",p)
        system_responses.append(cos)
        human_responses.append(responses[p_count])
      except:
        print "ERROR processing",p
      p_count+=1

    if len(system_responses) > 1:
      print system_responses
      print human_responses
      print model.most_similar(nonce,topn=10)
		
      sp = spearman(human_responses,system_responses)	
      print "RHO:",sp
      if not math.isnan(sp):
        spearmans.append(sp)
    c+=1


f.close()

print "AVERAGE RHO:",float(sum(spearmans))/float(len(spearmans))
