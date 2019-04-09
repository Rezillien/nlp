import string
from pathlib import Path
import numpy as np
from elasticsearch import Elasticsearch
from tqdm import tqdm

""""
Compute bigram counts in the corpora, ignoring bigrams which contain at least one token that is not a word 
(it contains characters other than letters). The text has to be properly normalized before the counts are computed: 
it should be downcased and all punctuation should be removed. Given the sentence: 
"The quick borwn fox jumps over the lazy dog", the bigram counts are as follows:

    "the quick": 1
    "quick brown": 1
    "brown fox": 1
    etc.

"""
es = Elasticsearch()


def lemmatize(word):
    analysis = es.indices.analyze(
        "prawo1",
        {
            "tokenizer": "standard",
            "filter": ["k_synonym", "lowercase", "morfologik_stem"],
            "text": word
        }
    )
    return analysis["tokens"][0]["token"]


def get_bigrams(text):
    text = text.lower().translate(str.maketrans('', '', string.punctuation))
    words = text.split()
    bigrams = []
    for i in range(1, len(words) - 1):
        bigrams.append((words[i - 1], words[i]))

    return bigrams


bigrams = []

for file in tqdm(Path("../ex1/").glob("*.txt")):
    with file.open() as f:
        text = f.read()
    bigrams.extend(get_bigrams(text))

#print(bigrams)

lemmat_cache = {}
bigrams_non_lemmatized = bigrams

bigrams_lemmatized=[]

for i in tqdm(bigrams):
    try:
        bigrams_lemmatized.append((lemmatize(i[0]),lemmatize(i[1])))
    except:
        pass # there is problem with elastic results

bigrams = bigrams_lemmatized

bigrams_count = {}

for i in bigrams:
    if not i in bigrams_count:
        bigrams_count[i]=1
    else:
        bigrams_count[i]=bigrams_count[i]+1

bigrams=bigrams_count

words = {}

for bigram, count in bigrams.items():
    for w in bigram:
        words[w] = words.get(w, 0) + count

for bigram, count in bigrams:
    for w in bigram:
        words[w] = words.get(w, 0) + count


# Use pointwise mutual information to compute the measure for all pairs of words.
bigrams_mutual_information = {
    bigram: np.log((bigrams[bigram] * (len(words) ** len(bigram))) / (np.prod([words[w] for w in bigram]) * bigrams[bigram]))
    for bigram in bigrams
}
print(sorted(bigrams_mutual_information.items(), key=lambda i: i[1])[-30:])


# Use log likelihood ratio (LLR) to compute the measure for all pairs of words

def H(k):
    N = k.sum()
    return ((k / N) * np.log(k / N + 1e-8)).sum()


def LLR(k):
    return (2 * k.sum()) * (H(k) - H(k.sum(axis=0)) - H(k.sum(axis=1)))


ngrams = np.sum(list(bigrams.values()))

bigrams_llr = {}

for bigram in tqdm(bigrams):
    w1 = bigram[0]
    w2 = bigram[1]
    w12 = bigrams.get((bigram[0], bigram[1]), 0) + bigrams.get((bigram[1], bigram[0]), 0)
    w1not2 = words[bigram[0]] - w12
    w2not1 = words[bigram[1]] - w12
    wnot1not2 = ngrams - w1not2 - w1not2 - w12
    bigrams_llr[bigram] = np.array([[w12, w1not2], [w2not1, wnot1not2]])

print(len(bigrams_llr))

#Sort the word pairs according to that measure in the descending order and display 30 top results
print(sorted(bigrams_llr.items(), key=lambda i: i[1])[-30:][::-1])

""""
    Answer the following questions:

Which measure works better for the problem?
LLR

What would be needed, besides good measure, to build a dictionary of multiword expressions?
Good lematizer, a lot of examples (for example wikipedia) and a lot of cpu

Can you identify a certain threshold which clearly divides the good expressions from the bad?
"""