from elasticsearch import Elasticsearch
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
from itertools import chain
import Levenshtein as levenshtein
from typing import Dict

es = Elasticsearch()

data = [h["_id"] for h in es.search(
    index="prawo1",
    doc_type="ustawa",
    body={
        "query": {
            "match_all": {}
        }
    }
)["hits"]["hits"]]

result = {}
for i in data:
    for token, metadata in \
            es.termvectors("prawo1", "ustawa", i, term_statistics=True, fields=["text"])["term_vectors"]["text"][
                "terms"].items():
        result[token] = metadata["term_freq"]

# 1,2
print('<ex>1,2')
print(result)

result_filtered = {}

for i in result:
    if len(i) > 2 and i.isalpha():
        result_filtered[i] = result[i]

# 3
print('<ex>3')
print(result_filtered)

result_sorted = sorted(result_filtered.items(), key=lambda s: -s[1])
plt.plot(list(range(len(result_sorted))), [np.log(r[1]) for r in result_sorted])

# 4
print('<ex>4')
plt.show()

polimorfologik = []

with Path("./polimorfologik/polimorfologik-2.1.txt").open() as file:
    for line in file.readlines():
        polimorfologik.append(line.split(";")[0:2])
words = set(chain.from_iterable(polimorfologik))
unknowns_words = []
for word in result_filtered:
    if word not in words:
        unknowns_words.append(word)

# 5
print('<ex>5')
print(unknowns_words)

highest_unknowns_words = [w for w in result_sorted if w[0] not in words]

# 6
print('<ex>6')
print(highest_unknowns_words[:30])

unknown_words_with_three_occurences = [w for w in highest_unknowns_words if w[1] == 3]

# 7
print('<ex>7')
print(unknown_words_with_three_occurences[:30])

known_words = {k: v for k, v in result_filtered.items() if k in words}


def probable_correction(word: str, frequency_dict: Dict[str, int]) -> str:
    return \
        sorted(frequency_dict.keys(), key=lambda key: -np.log(frequency_dict[key]) / levenshtein.distance(word, key))[0]


levenstain_distance = {}

for w in unknown_words_with_three_occurences:
    levenstain_distance[w[0]] = \
        sorted(known_words.keys(), key=lambda key: -(known_words[key] / levenshtein.distance(w[0], key)))[0]

print('<ex>8')
print(levenstain_distance)
